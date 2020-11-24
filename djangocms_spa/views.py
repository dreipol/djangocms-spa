from contextlib import suppress

from cms.utils.moderator import use_draft
from cms.utils.page import get_page_from_path
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse
from django.urls import NoReverseMatch, resolve, reverse
from django.utils.translation import activate
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

import json
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
    url_name = ''
    page_title = ''
    page_description = ''

    def get_meta_data(self):
        meta_data = {
            'title': self.page_title,
            'description': self.page_description
        }

        language_links = self.get_translated_urls()
        if language_links:
            meta_data['languages'] = language_links
        return meta_data

    def get_translated_urls(self):
        request_language = self.request.LANGUAGE_CODE
        if self.url_name:
            url_name = self.url_name
        else:
            url_name = resolve(self.request.path).url_name

        language_links = {}
        for language_code, language in settings.LANGUAGES:
            if language_code != request_language:
                activate(language_code)
                with suppress(NoReverseMatch):
                    language_links[language_code] = reverse(url_name, args=self.args, kwargs=self.kwargs)
        activate(request_language)
        return language_links


class MultipleObjectSpaMixin(MetaDataMixin, ObjectPermissionMixin, MultipleObjectMixin):
    list_container_name = settings.DJANGOCMS_SPA_DEFAULT_LIST_CONTAINER_NAME
    model = None
    queryset = None
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        data = {
            'data': self.get_fetched_data()
        }

        partials = self.get_partials()
        if partials:
            data['partials'] = partials

        response = HttpResponse(
            content=json.dumps(data, cls=settings.DJANGOCMS_SPA_JSON_ENCODER),
            content_type='application/json',
            status=200
        )

        if hasattr(settings, 'GIT_COMMIT_HASH'):
            response['X-App-Version'] = settings.GIT_COMMIT_HASH

        return response

    def get_partials(self):
        partial_names = get_partial_names_for_template(template=self.get_template_names(), get_all=False,
                                                       requested_partials=self.request.GET.get('partials'))
        return get_frontend_data_dict_for_partials(
            partials=partial_names,
            request=self.request,
            editable=self.request.user.has_perm('cms.edit_static_placeholder'),
        )

    def get_fetched_data(self):
        return {}

    def get_template_names(self):
        return self.template_name


class CachedSpaApiView(SpaApiView):
    add_language_code = True
    cache_key = None

    @cache_view
    def dispatch(self, request, *args, **kwargs):
        return super(CachedSpaApiView, self).dispatch(request, *args, **kwargs)

    def get_cache_key(self):
        return self.cache_key


class SpaCmsPageDetailApiView(CachedSpaApiView):
    cms_page = None
    cms_page_title = None

    def get(self, request, **kwargs):
        draft = use_draft(request)
        preview = 'preview' in request.GET
        try:
            self.cms_page = get_page_from_path(site=get_current_site(request), path=kwargs.get('path', ''),
                                               preview=preview, draft=draft)
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


class SpaListApiView(MultipleObjectSpaMixin, CachedSpaApiView):
    def get_fetched_data(self):
        data = {}

        view_data = super(SpaListApiView, self).get_fetched_data()
        if view_data:
            data.update(view_data)

        return data


class SpaDetailApiView(SingleObjectSpaMixin, CachedSpaApiView):
    def get_fetched_data(self):
        data = {}

        view_data = super(SpaDetailApiView, self).get_fetched_data()
        if view_data:
            data.update(view_data)

        return data


class SpaFormApiView(SpaApiView):
    form_class = None

    def __init__(self, *args, **kwargs):
        if not self.form_class:
            raise NotImplementedError("form_class has to be set in subclasses")
        super(SpaFormApiView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, request=request)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        self.post_save(form)
        return JsonResponse(data=(form.get_api_response_data_dict()), status=200)

    def form_invalid(self, form):
        return JsonResponse(data=form.get_api_response_data_dict(), status=400)

    def post_save(self, form):
        """
        This method is called after the form was saved. You can use it to send emails...
        :param form:
        """
        pass
