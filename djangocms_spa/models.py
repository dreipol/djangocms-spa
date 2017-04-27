from cms.utils.urlutils import admin_reverse
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from menus.menu_pool import MenuRenderer

from appconf import AppConf


class DjangoCmsSPAConf(AppConf):
    DEFAULT_TEMPLATE = 'index.html'
    TEMPLATES = {
        DEFAULT_TEMPLATE: {
            'cms_template': 'index.html',
            'static_placeholders': ['']
        }
    }
    CACHE_TIMEOUT = 60 * 10
    DEFAULT_LIST_CONTAINER_NAME = 'object_list'
    CMS_PAGE_DATA_POST_PROCESSOR = None
    PLACEHOLDER_DATA_POST_PROCESSOR = None
    # The CMS used the `position` field to order plugins until treebeard was introduced and a `path` field was added.
    # At the moment the render and structure mode both use `position` to order the plugins but it is very likely that
    # this is changed in the future.
    PLUGIN_ORDER_FIELD = 'position'
    PARTIAL_CALLBACKS = {}


class DjangoCmsMixin(models.Model):
    class Meta:
        abstract = True

    def get_placeholder_field_names(self):
        """
        Returns a list with the names of all PlaceholderFields.
        """
        return [field.name for field in self._meta.fields if field.get_internal_type() == 'PlaceholderField']

    def get_cms_placeholder_json(self, request, placeholder_name):
        return {
            'cms': [
                placeholder_name,
                {
                    'type': 'generic',
                    'page_language': request.LANGUAGE_CODE,
                    'placeholder_id': '',
                    'plugin_name': '%s %s' % (_('Edit'), self._meta.verbose_name),
                    'plugin_type': '',
                    'plugin_id': self.pk,
                    'plugin_language': '',
                    'plugin_parent': '',
                    'plugin_order': '',
                    'plugin_restriction': [],
                    'plugin_parent_restriction': [],
                    'onClose': 'REFRESH_PAGE',
                    'addPluginHelpTitle': '%s %s' % (_('Add plugin to'), self._meta.verbose_name),
                    'urls': {
                        'add_plugin': admin_reverse('cms_page_add_plugin'),
                        'edit_plugin': '{url}?language={language_code}'.format(
                            url=reverse(
                                'admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=(self.pk,)),
                            language_code=request.LANGUAGE_CODE
                        ),
                        'move_plugin': admin_reverse('cms_page_move_plugin'),
                        'delete_plugin': admin_reverse('cms_page_delete_plugin', args=(self.pk,)),
                        'copy_plugin': admin_reverse('cms_page_copy_plugins')
                    }
                }
            ]
        }


def set_menu_renderer_context(self, context):
    """
    Monkey patch the MenuRenderer by adding a helper method to store the context.
    """
    self.context = context

MenuRenderer.set_context = set_menu_renderer_context
