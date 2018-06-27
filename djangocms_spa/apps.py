from django.apps import AppConfig


class DjangoCmsSpaConfig(AppConfig):
    name = 'djangocms_spa'

    def ready(self):
        from django.forms import CheckboxInput, RadioSelect, Select, SelectMultiple
        from .form_helpers import get_placeholder_for_choices_field, get_serialized_choices_for_field

        CheckboxInput.render_spa = lambda self, field, initial=None: {
            'items': get_serialized_choices_for_field(field=field),
            'type': 'checkbox',
            'multiline': True,
        }

        RadioSelect.render_spa = lambda self, field, initial=None: {
            'items': get_serialized_choices_for_field(field=field),
            'type': 'radio',
            'multiline': True,
        }

        Select.render_spa = lambda self, field, initial=None: {
            'items': get_serialized_choices_for_field(field=field),
            'placeholder': get_placeholder_for_choices_field(field)
        }

        SelectMultiple.render_spa = lambda self, field, initial=None: {
            'items': get_serialized_choices_for_field(field=field),
        }
