from urllib.request import url2pathname

from cms.models import StaticPlaceholder
from django.conf import settings

from djangocms_spa.renderer_pool import renderer_pool

from .utils import get_function_by_path


def get_frontend_data_dict_for_cms_page(cms_page, cms_page_title, request, editable=False):
    """
    Returns the data dictionary of a CMS page that is used by the frontend.
    """
    placeholders = list(cms_page.placeholders.all())
    placeholder_frontend_data_dict = get_frontend_data_dict_for_placeholders(
        placeholders=placeholders,
        request=request,
        editable=editable
    )
    global_placeholder_data_dict = get_global_placeholder_data(placeholder_frontend_data_dict)
    data = {
        'containers': placeholder_frontend_data_dict,
        'meta': {
            'title': cms_page_title.title,
            'description': cms_page_title.meta_description or '',
        }
    }

    if placeholder_frontend_data_dict:
        data['containers'] = placeholder_frontend_data_dict

    if global_placeholder_data_dict:
        data['global_placeholder_data'] = global_placeholder_data_dict

    post_processer = settings.DJANGOCMS_SPA_CMS_PAGE_DATA_POST_PROCESSOR
    if post_processer:
        func = get_function_by_path(post_processer)
        data = func(cms_page=cms_page, data=data, request=request)

    return data


def get_frontend_data_dict_for_placeholders(placeholders, request, editable=False):
    """
    Takes a list of placeholder instances and returns the data that is used by the frontend to render all contents.
    The returned dict is grouped by placeholder slots.
    """
    data_dict = {}
    for placeholder in placeholders:
        if placeholder:
            plugins = []

            # We don't use the helper method `placeholder.get_plugins()` because of the wrong order by path.
            placeholder_plugins = placeholder.cmsplugin_set.filter(language=request.LANGUAGE_CODE).order_by(
                settings.DJANGOCMS_SPA_PLUGIN_ORDER_FIELD)

            for plugin in placeholder_plugins:
                # We need the complete cascading structure of the plugins in the frontend. This is why we ignore the
                # children here and add them later in the loop.
                if not plugin.parent:
                    plugins.append(get_frontend_data_dict_for_plugin(
                        request=request,
                        plugin=plugin,
                        editable=editable)
                    )

            if plugins or editable:
                data_dict[placeholder.slot] = {
                    'type': 'cmp-%s' % placeholder.slot,
                    'plugins': plugins,
                }

            if editable:
                # This is the structure of the template `cms/toolbar/placeholder.html` that is used to register
                # the frontend editing.
                from cms.plugin_pool import plugin_pool
                plugin_types = [cls.__name__ for cls in plugin_pool.get_all_plugins(placeholder.slot, placeholder.page)]
                allowed_plugins = plugin_types + plugin_pool.get_system_plugins()

                data_dict[placeholder.slot]['cms'] = [
                    'cms-placeholder-{}'.format(placeholder.pk),
                    {
                        'type': 'placeholder',
                        'name': str(placeholder.get_label()),
                        'page_language': request.LANGUAGE_CODE,
                        'placeholder_id': placeholder.pk,
                        'plugin_language': request.LANGUAGE_CODE,
                        'plugin_restriction': [module for module in allowed_plugins],
                        'addPluginHelpTitle': 'Add plugin to placeholder {}'.format(placeholder.get_label()),
                        'urls': {
                            'add_plugin': placeholder.get_add_url(),
                            'copy_plugin': placeholder.get_copy_url()
                        }
                    }
                ]

    return data_dict


def get_frontend_data_dict_for_plugin(request, plugin, editable):
    """
    Returns a serializable data dict of a CMS plugin and all its children. It expects a `render_json_plugin()` method
    from each plugin. Make sure you implement it for your custom plugins and monkey patch all third-party plugins.
    """
    json_data = {}
    instance, plugin = plugin.get_plugin_instance()

    if not instance:
        return json_data

    renderer = renderer_pool.renderer_for_plugin(plugin)
    if renderer:
        json_data = renderer.render(request=request, plugin=plugin, instance=instance, editable=editable)

    if hasattr(plugin, 'parse_child_plugins') and plugin.parse_child_plugins:
        children = []
        for child_plugin in instance.get_children().order_by(settings.DJANGOCMS_SPA_PLUGIN_ORDER_FIELD):
            # Parse all children
            children.append(
                get_frontend_data_dict_for_plugin(
                    request=request,
                    plugin=child_plugin,
                    editable=editable
                )
            )

        if children:
            json_data['plugins'] = children

    return json_data


def get_partial_names_for_template(template=None, get_all=True, requested_partials=None):
    template = template or settings.DJANGOCMS_SPA_DEFAULT_TEMPLATE

    if requested_partials:
        # Transform the requested partials into a list
        requested_partials = url2pathname(requested_partials).split(',')
    else:
        requested_partials = []

    try:
        partials = settings.DJANGOCMS_SPA_TEMPLATES[template]['partials']
    except KeyError:
        try:
            default_template_path = settings.DJANGOCMS_SPA_DEFAULT_TEMPLATE
            partials = settings.DJANGOCMS_SPA_TEMPLATES[default_template_path]['partials']
        except KeyError:
            partials = []

    if get_all:
        return partials
    else:
        return [partial for partial in partials if partial in requested_partials]


def get_frontend_data_dict_for_partials(partials, request, editable=False, renderer=None):
    """
    We call global page elements that are used to render a template `partial`. The contents of a partial do not
    change from one page to another. In a django CMS project partials are implemented as static placeholders. But
    there are usually other parts (e.g. menu) that work pretty much the same way. Because we don't have a template
    that allows us to render template tags, we need to have a custom implementation for those needs. We decided to
    use a `callback` approach that allows developers to bring custom data into the partial list.

    To prevent infinite recursions when using callbacks we have the `renderer` parameter.
    """

    # Split static placeholders from partials that have a custom callback.
    static_placeholder_names = []
    custom_callback_partials = []
    for partial in partials:
        if partial in settings.DJANGOCMS_SPA_PARTIAL_CALLBACKS.keys():
            custom_callback_partials.append(partial)
        else:
            static_placeholder_names.append(partial)

    # Get the data of all static placeholders
    use_static_placeholder_draft = request.toolbar.edit_mode and request.user.has_perm('cms.edit_static_placeholder')
    static_placeholders = []
    for static_placeholder_name in static_placeholder_names:
        static_placeholders.append(get_static_placeholder(static_placeholder_name, use_static_placeholder_draft))

    partial_data = get_frontend_data_dict_for_placeholders(
        placeholders=static_placeholders,
        request=request,
        editable=editable
    )

    # Get the data of all partials that have a custom callback.
    for partial_settings_key in custom_callback_partials:
        dotted_function_module_path = settings.DJANGOCMS_SPA_PARTIAL_CALLBACKS[partial_settings_key]
        callback_function = get_function_by_path(dotted_function_module_path)
        partial_data[partial_settings_key] = callback_function(request, renderer)

    return partial_data


def get_static_placeholder(static_placeholder_slot_name, get_draft_data=False):
    static_placeholder = StaticPlaceholder.objects.get_or_create(
        code=static_placeholder_slot_name,
        defaults={'creation_method': StaticPlaceholder.CREATION_BY_TEMPLATE}
    )[0]

    if get_draft_data:
        return static_placeholder.draft
    else:
        return static_placeholder.public


def get_global_placeholder_data(placeholder_frontend_data_dict):
    """
    In some rare cases you need to post process the placeholder data and add additional, global data to the route
    object. Define your post-processor in the DJANGOCMS_SPA_VUE_JS_PLACEHOLDER_DATA_POST_PROCESSOR setting variable
    (e.g. `my_app.my_module.my_function` and return the data you need.
    """
    post_processer = settings.DJANGOCMS_SPA_PLACEHOLDER_DATA_POST_PROCESSOR
    if not post_processer:
        return {}

    func = get_function_by_path(post_processer)
    return func(placeholder_frontend_data_dict=placeholder_frontend_data_dict)
