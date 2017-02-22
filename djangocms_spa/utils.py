from importlib import import_module

from django.conf import settings
from django.core.urlresolvers import resolve


def get_function_by_path(dotted_function_module_path):
    """
    Returns the function for a given path (e.g. 'my_app.my_module.my_function').
    """
    # Separate the module path from the function name.
    module_path, function_name = tuple(dotted_function_module_path.rsplit('.', 1))

    module = import_module(module_path)
    return getattr(module, function_name)


def get_frontend_component_name_by_template(template_path):
    try:
        return settings.DJANGOCMS_SPA_TEMPLATES[template_path]['frontend_component_name']
    except AttributeError:
        return settings.DJANGOCMS_SPA_TEMPLATES[settings.DJANGOCMS_SPA_DEFAULT_TEMPLATE]['frontend_component_name']


def get_template_path_by_frontend_component_name(frontend_component_name):
    for template_path in settings.DJANGOCMS_SPA_TEMPLATES:
        try:
            name = settings.DJANGOCMS_SPA_TEMPLATES[template_path]['frontend_component_name']
        except AttributeError:
            name = ''

        if name == frontend_component_name:
            return template_path

    return settings.DJANGOCMS_SPA_TEMPLATES[settings.DJANGOCMS_SPA_DEFAULT_TEMPLATE]['frontend_component_name']


def get_view_from_url(url):
    resolved_url = resolve(url)
    view_module_path = resolved_url._func_path  # e.g. my_app.views.views.MyListView
    view = get_function_by_path(view_module_path)
    return view
