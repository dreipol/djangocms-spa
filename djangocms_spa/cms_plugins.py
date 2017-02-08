from cms.plugin_base import CMSPluginBase


class JsonCMSPluginBase(CMSPluginBase):
    frontend_component_name = ''
    instance = None

    def render_json_plugin(self, request, instance=None, position=0, include_admin_data=False):
        self.instance = instance
        context = {
            'content': {},
            'position': position,
            'type': self.frontend_component_name
        }

        if include_admin_data:
            # This is the structure of the template `cms/toolbar/plugin.html` that is used to register
            # the frontend editing.
            context['cms'] = [
                'cms-plugin-{}'.format(instance.id),
                {
                    'type': 'plugin',
                    'page_language': instance.language,
                    'placeholder_id': instance.placeholder.id,
                    'plugin_name': str(instance._meta.verbose_name),
                    'plugin_type': self.__class__.__name__,
                    'plugin_id': instance.id,
                    'plugin_language': instance.language,
                    'plugin_parent': instance.parent.id if instance.parent else None,
                    'plugin_order': instance.position,
                    'plugin_restriction': self.get_child_classes(instance.placeholder, instance.page) or [],
                    'plugin_parent_restriction': self.get_parent_classes(instance.placeholder, instance.page) or [],
                    'onClose': False,
                    'addPluginHelpTitle': 'Add plugin to {parent_plugin_name}'.format(
                        parent_plugin_name=instance.get_plugin_name()),
                    'urls': instance.get_action_urls()
                }
            ]

        return context


class JsonOnlyPluginBase(JsonCMSPluginBase):
    render_template = 'djangocms_spa/empty.html'  # The plugin needs a template although we render JSON only.
