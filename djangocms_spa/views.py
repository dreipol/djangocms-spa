import json

from cms.utils.page_resolver import get_page_from_request
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from rest_framework.views import APIView

from .content_helpers import (get_frontend_data_dict_for_cms_page, get_frontend_data_dict_for_partials,
                              get_partial_names_for_template)
from .decorators import cache_view


class ObjectPermissionMixin(object):
    model = None
    request = None

    def has_change_permission(self):
        if hasattr(self, 'model'):
            model_permission_code = '%s.change_%s' % (self.model._meta.app_label, self.model._meta.model_name)
            return self.request.user.has_perm(model_permission_code)
        return True


class MetaDataMixin(object):
    def get_meta_data(self):
        return {
            'title': '',
            'description': ''
        }


class MultipleObjectSpaMixin(MetaDataMixin, ObjectPermissionMixin, MultipleObjectMixin):
    list_container_name = settings.DJANGOCMS_SPA_DEFAULT_LIST_CONTAINER_NAME
    model = None
    queryset = None

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(MultipleObjectSpaMixin, self).get(request, *args, **kwargs)

    def get_fetched_data(self):
        object_list = []
        editable = self.has_change_permission()

        for object in self.object_list:
            if hasattr(object, 'get_frontend_list_data_dict'):
                placeholder_name = 'cms-plugin-{app}-{model}-{pk}'.format(
                    app=object._meta.app_label,
                    model=object._meta.model_name,
                    pk=object.pk
                )
                object_list.append(object.get_frontend_list_data_dict(self.request, editable=editable,
                                                                      placeholder_name=placeholder_name))

        return {
            'containers': {
                self.list_container_name: object_list
            },
            'meta': self.get_meta_data()
        }


class SingleObjectSpaMixin(MetaDataMixin, ObjectPermissionMixin, SingleObjectMixin):
    object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(SingleObjectSpaMixin, self).get(request, *args, **kwargs)

    def get_fetched_data(self):
        data = {}

        if hasattr(self.object, 'get_frontend_detail_data_dict'):
            data = self.object.get_frontend_detail_data_dict(self.request, editable=self.has_change_permission())

        data['meta'] = self.get_meta_data()
        return data


class SpaApiView(APIView):
    template_name = None

    @cache_view
    def dispatch(self, request, *args, **kwargs):
        return super(SpaApiView, self).dispatch(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        data = {
            'data': self.get_fetched_data()
        }

        partials = self.get_partials()
        if partials:
            data['partials'] = partials

        return HttpResponse(
            content=json.dumps(data),
            content_type='application/json',
            status=200
        )

    def get_partials(self):
        partial_names = get_partial_names_for_template(template=self.get_template_names(), get_all=False,
                                                       requested_partials=self.request.GET.get('partials'))
        return get_frontend_data_dict_for_partials(
            partials=partial_names,
            request=self.request,
            editable=self.request.user.has_perm('cms.edit_static_placeholder'),
        )

    def get_template_names(self):
        return self.template_name


class SpaCmsPageDetailApiView(SpaApiView):
    cms_page = None
    cms_page_title = None

    def get(self, request, **kwargs):
        try:
            self.cms_page = get_page_from_request(request, use_path=kwargs.get('path', ''))
            self.cms_page_title = self.cms_page.title_set.get(language=request.LANGUAGE_CODE)
        except AttributeError:
            return JsonResponse(data={}, status=404)

        return super(SpaCmsPageDetailApiView, self).get(request, **kwargs)

    def get_fetched_data(self):
        data = {}

        view_data = get_frontend_data_dict_for_cms_page(
            cms_page=self.cms_page,
            cms_page_title=self.cms_page_title,
            request=self.request,
            editable=self.request.user.has_perm('cms.change_page')
        )
        if view_data:
            data.update(view_data)

        return data

    def get_template_names(self):
        return self.cms_page.get_template()


class SpaListApiView(MultipleObjectSpaMixin, SpaApiView):
    def get_fetched_data(self):
        data = {}

        view_data = super(SpaListApiView, self).get_fetched_data()
        if view_data:
            data.update(view_data)

        return data


class SpaDetailApiView(SingleObjectSpaMixin, SpaApiView):
    def get_fetched_data(self):
        data = {}

        view_data = super(SpaDetailApiView, self).get_fetched_data()
        if view_data:
            data.update(view_data)

        return data
