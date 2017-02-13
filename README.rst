=============
djangocms-spa
=============

Run your django CMS project as a single-page application (SPA). This is is just a collection of helpers. It is was build to use it together with a concrete implementation e.g.

 * [djangocms-spa-vue-js](https://github.com/dreipol/djangocms-spa-vue-js)

Quickstart
----------

Install djangocms_spa::

    pip install djangocms-spa

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'djangocms_spa',
        ...
    )


Settings
--------

Set your default template::

    DJANGOCMS_SPA_DEFAULT_TEMPLATE = 'pages/content.html'


Configure templates, the component names used by your frontend team and partial contents (e.g. static placeholders).
You should cover all templates of `CMS_TEMPLATES` and all of your custom views::

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


Configure custom partials::

    DJANGOCMS_SPA_PARTIAL_CALLBACKS = {
        'menu': 'djangocms_spa.partial_callbacks.get_cms_menu_data_dict'
    }


Partials
--------

We call global page elements that are used to render a template `partial`. The contents of a partial do not
change from one page to another. In a django CMS project partials are implemented as static placeholders. Because we
don't render any HTML templates, we need to configure the static placeholders per template in `DJANGOCMS_SPA_TEMPLATES`
as partials. To edit your placeholder and static placeholder data, you need to render both in the edit mode::

    {% if request.toolbar.edit_mode %}
        {% placeholder "main" %}
        {% static_placeholder "footer" %}
    {% endif %}

Usually there are other parts (e.g. menu) that work pretty much like static placeholders. Because we don't have a
template that allows us to render template tags, we need to have a custom implementation for those needs. We decided to
use a `callback` approach that allows developers to bring custom data into the partial list. Define your callbacks
in `DJANGOCMS_SPA_PARTIAL_CALLBACKS` by added a partial key and the module path of the callback function. You will find
an example in `djangocms_spa/partial_callbacks.py`. Your function should return a dictionary like this::

    {
        'type': 'generic',
        'content': {
            'my_var': 1
        }
    }


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
