from cms.plugin_base import CMSPluginBase


class SPAPluginMixin(object):
    frontend_component_name = None
    parse_child_plugins = True

    def render_spa(self, request, context, instance):
        return context


class SPAPluginBase(SPAPluginMixin, CMSPluginBase):
    render_template = 'djangocms_spa/empty.html'  # The plugin needs a template although we render JSON only.
