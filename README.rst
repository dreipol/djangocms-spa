=============
djangocms-spa
=============

Run your django CMS project as a single-page application (SPA) by using this collection of helpers together with
another package (e.g. `djangocms-spa-vue-js`).


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


Configure templates, the component names used by your frontend team and partial contents (e.g. static placeholders). You should cover all templates
of `CMS_TEMPLATES` and all of your custom views::

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

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
