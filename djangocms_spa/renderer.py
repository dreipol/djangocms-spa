from django.conf import settings

from .cms_plugins import SPAPluginMixin


class BaseSPARenderer(object):
    """
    Some base data needs to be available for all plugins.
    """
    frontend_component_name = ''
    plugin_class = None

    def render(self, request, plugin, instance=None, editable=False):
        context = {
            'content': {},
            'type': self.frontend_component_name
        }

        if editable:
            # This is the structure of the template `cms/toolbar/plugin.html` that is used to register
            # the frontend editing.
            context['cms'] = [
                'cms-plugin-{}'.format(instance.id),
                {
                    'type': 'plugin',
                    'page_language': instance.language,
                    'placeholder_id': instance.placeholder.id,
                    'plugin_name': str(instance._meta.verbose_name),
                    'plugin_type': self.plugin_class.__class__.__name__,
                    'plugin_id': instance.id,
                    'plugin_language': instance.language,
                    'plugin_parent': instance.parent.id if instance.parent else None,
                    'plugin_order': instance.position,
                    'plugin_restriction': self.plugin_class.get_child_classes(instance.placeholder,
                                                                              instance.page) or [],
                    'plugin_parent_restriction': self.plugin_class.get_parent_classes(instance.placeholder,
                                                                                      instance.page) or [],
                    'onClose': False,
                    'addPluginHelpTitle': 'Add plugin to {parent_plugin_name}'.format(
                        parent_plugin_name=instance.get_plugin_name()),
                    'urls': instance.get_action_urls()
                }
            ]

        return context


class MixinPluginRenderer(BaseSPARenderer):
    """
    Renders the plugins which use the SPAPluginMixin.
    """

    def __init__(self, plugin_class: SPAPluginMixin):
        super().__init__()
        self.plugin_class = plugin_class

    @property
    def frontend_component_name(self):
        return self.plugin_class.frontend_component_name

    def render(self, request, plugin, instance=None, editable=False):
        context = super(MixinPluginRenderer, self).render(request, plugin, instance, editable)
        return plugin.render_spa(request=request, context=context, instance=instance)


class SPAFormFieldWidgetRenderer(object):
    def __init__(self, form, field, name):
        self.form = form
        self.field = field
        self.name = name

    def render(self):
        context = {
            'id': self.name,
            'label': str(self.field.label),
            'component': self._get_component_name(),
            'val': self._get_value_for_field()
        }

        messages = self._get_messages_for_field()
        context['messages'] = messages

        state = self._get_state_for_field()
        context['state'] = state

        if hasattr(self.field.widget, 'input_type'):
            context['type'] = self.field.widget.input_type

        if self.field.widget.attrs.get('placeholder'):
            context['placeholder'] = str(self.field.widget.attrs['placeholder'])

        if self.field.widget.attrs.get('spa_attrs'):
            context.update(self.field.widget.attrs['spa_attrs'])

        try:
            widget_context = self.field.widget.render_spa(field=self.field)
        except:
            widget_context = {}

        context.update(widget_context)

        return context

    def _get_component_name(self):
        widget_class = type(self.field.widget)
        module_path = '.'.join([widget_class.__module__, widget_class.__name__])
        return settings.DJANGOCMS_SPA_COMPONENT_NAMES.get(module_path, '')

    def _get_value_for_field(self):
        if hasattr(self.form, 'cleaned_data') and self.name in self.form.cleaned_data.keys():
            return str(self.form.cleaned_data[self.name])
        elif self.name in self.form.data.keys():
            return str(self.form.data[self.name])
        elif self.name in self.form.initial.keys():
            return self.form.initial[self.name]
        elif self.field.initial is not None:
            return self.field.initial
        return ''

    def _get_messages_for_field(self):
        messages = {}

        if self.field.help_text:
            messages['info'] = self.field.help_text

        if self.name in self.form.errors.keys():
            messages['error'] = [str(error.message) for error in self.form.errors[self.name].data]

        return messages

    def _get_state_for_field(self):
        state = {}

        if self.field.required:
            state['required'] = True

        if hasattr(self.field, 'is_disabled') and self.field.is_disabled:
            state['disabled'] = True

        # Add errors
        if self.name in self.form.errors.keys():
            state['error'] = True

        return state
