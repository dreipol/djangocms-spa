from .cms_plugins import SPAPluginMixin
from .renderer import BaseSPARenderer, MixinPluginRenderer


class RendererPool(object):
    def __init__(self):
        self.renderers = {}

    def register_renderer(self, renderer: BaseSPARenderer.__class__):
        self._register_renderer(renderer())

    def _register_renderer(self, renderer: BaseSPARenderer):
        self.renderers[renderer.plugin_class.__name__] = renderer

    def register_plugin(self, plugin_class: 'SPAPluginMixin'):
        if not issubclass(plugin_class, SPAPluginMixin):
            raise TypeError()

        renderer = MixinPluginRenderer(plugin_class)
        self._register_renderer(renderer)
        return renderer

    def renderer_for_plugin(self, plugin) -> BaseSPARenderer:
        plugin_class = plugin.__class__
        renderer = self.renderers.get(plugin_class.__name__, None)
        if not renderer:
            try:
                renderer = self.register_plugin(plugin_class)
            except TypeError:
                pass

        return renderer

renderer_pool = RendererPool()
