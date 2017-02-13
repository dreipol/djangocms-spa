from cms.plugin_base import CMSPluginBase


class SPAPluginMixin(object):
    frontend_component_name = None

    def render_spa(self, request, context, instance, position, include_admin_data):
        return context


class SPAPluginBase(CMSPluginBase, SPAPluginMixin):
    render_template = 'djangocms_spa/empty.html'  # The plugin needs a template although we render JSON only.
