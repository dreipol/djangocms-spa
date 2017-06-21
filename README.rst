=============
djangocms-spa
=============

Run your django CMS project as a single-page application (SPA). This package provides a REST-API that returns all
page contents serialized as JSON. A couple of helpers and base classes can be used to create API endpoints for
custom views. ``djangocms-spa`` was build to use it together with a concrete implementation:

* `djangocms-spa-vue-js`_

.. _`djangocms-spa-vue-js`: https://github.com/dreipol/djangocms-spa-vue-js


Quickstart
----------

Install djangocms_spa::

    pip install djangocms-spa

Add it to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'djangocms_spa',
        ...
    )

Add the Locale middleware (if it isn't already):

.. code-block:: python

    MIDDLEWARE = (
    ...
    'django.middleware.locale.LocaleMiddleware',
    )


Set your default template:

.. code-block:: python

    DJANGOCMS_SPA_DEFAULT_TEMPLATE = 'pages/content.html'


The settings variable ``DJANGOCMS_SPA_TEMPLATES`` expects a dictionary of templates. It should cover all templates
of ``CMS_TEMPLATES`` and use the path as key. The frontend component name and a list of partials
(e.g. static placeholders) are valid options.

.. code-block:: python

    DJANGOCMS_SPA_TEMPLATES = {
        'pages/content.html': {
            'frontend_component_name': 'content',
            'partials': ['menu', 'meta', 'footer']
        },
        'pages/content_with_section_navigation.html': {
            'frontend_component_name': 'content-with-section-navigation',
            'partials': ['menu', 'meta', 'footer']
        },
    }


Configure your custom partials:

.. code-block:: python

    DJANGOCMS_SPA_PARTIAL_CALLBACKS = {
        'menu': 'djangocms_spa.partial_callbacks.get_cms_menu_data_dict'
    }


Plugins
-------

Your plugins don't need a rendering template but a ``render_spa`` method that returns a dictionary. To have a clean
structure, we usually put the context inside a `content` key of the dictionary:

.. code-block:: python

    class TextPlugin(JsonOnlyPluginBase):
        name = _('Text')
        model = TextPluginModel
        frontend_component_name = 'cmp-text'
        def render_spa(self, request, context, instance):
            context = super(TextPlugin, self).render_spa(request, context, instance)
            context['content']['text']. = instance.text
            return context

    plugin_pool.register_plugin(TextPlugin)


Settings
--------

``CACHE_TIMEOUT`` (**default**: ``60 * 10``)

If you are using a caching backend, the API responses are cached.


``DJANGOCMS_SPA_DEFAULT_TEMPLATE`` (**default**: ``'index.html'``)


``DEFAULT_LIST_CONTAINER_NAME`` (**default**: ``'object_list'``)

The list view uses this key to group its data.


``CMS_PAGE_DATA_POST_PROCESSOR`` (**default**: ``None``)

This hook allows you to post process the data of a CMS page by defining a module path.


``PLACEHOLDER_DATA_POST_PROCESSOR`` (**default**: ``None``)

This hook allows you to post process the data of a placeholder by defining a module path.


Partials
--------

We call global page elements that are used to render a template "partial". The contents of a partial do not
change from one page to another. In a django CMS project partials are implemented as static placeholders. Because we
don't render any HTML templates, we need to configure the static placeholders for each template in
``DJANGOCMS_SPA_TEMPLATES`` as partials. To edit your placeholder and static placeholder data, you need to render both
in the edit mode::

    {% if request.toolbar.edit_mode %}
        {% placeholder "main" %}
        {% static_placeholder "footer" %}
    {% endif %}

Usually there are other parts like the menu or any other template tag that work pretty much like static placeholders.
Because we don't have a template that allows us to render template tags, we need to have a custom implementation for
those needs. We decided to use a `callback` approach that allows developers to bring custom data into the partial
list. Define your callbacks in ``DJANGOCMS_SPA_PARTIAL_CALLBACKS`` by adding a partial key and the module path of the
callback function. You will find an example in `djangocms_spa/partial_callbacks.py`_. Your function should return a
dictionary like this::

    {
        'type': 'generic',
        'content': {
            'my_var': 1
        }
    }

.. _`djangocms_spa/partial_callbacks.py`: https://github.com/dreipol/djangocms-spa/blob/master/djangocms_spa/partial_callbacks.py

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
