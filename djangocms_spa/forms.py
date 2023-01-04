import requests
import six
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import ALL_FIELDS, BaseModelForm, forms
from django.forms.models import ModelFormMetaclass
from django.utils.translation import gettext_lazy as _

from .renderer import SPAFormFieldWidgetRenderer

DEFAULT_VALIDATION_ERROR = _('Invalid data')
NO_COOKIE_MESSAGE = _('Please activate cookies to submit the form.')
SUBMIT_BUTTON_LABEL = _('Submit')


class SpaApiForm(forms.Form):
    api_url = ''
    default_validation_error = DEFAULT_VALIDATION_ERROR
    submit_button_label = SUBMIT_BUTTON_LABEL
    show_general_error_message = True
    uses_recaptcha = True

    def get_api_url(self):
        return str(self.api_url)

    def get_spa_data_dict(self):
        """
        Returns a dictionary that is used to render the form.
        """
        data_dict = self.get_form_state_and_messages_dict()
        data_dict['url'] = self.get_api_url()
        data_dict['fields'] = self.get_fields_data_dict()
        return data_dict

    def get_fields_data_dict(self):
        fields = [self.get_form_field_data_dict(name=name, field=field) for name, field in self.fields.items()]
        fields.append(self.get_submit_button())
        return fields

    def get_form_state_and_messages_dict(self):
        data_dict = {
            'state': {
                'error': bool(self.errors)
            }
        }

        error_messages = []
        if self.errors and self.show_general_error_message:
            error_messages.append(str(self.default_validation_error))
        non_field_errors = self.errors.get(ALL_FIELDS)
        if non_field_errors:
            error_messages.extend(non_field_errors)
        if error_messages:
            data_dict['messages'] = {
                'error': error_messages
            }

        return data_dict

    def get_form_field_data_dict(self, name, field):
        renderer = SPAFormFieldWidgetRenderer(form=self, field=field, name=name)
        field_data = renderer.render()
        return field_data

    def get_submit_button_label(self):
        return self.submit_button_label

    def get_submit_button(self):
        data = {
            'component': 'cmp-form-submit',
            'label': str(self.get_submit_button_label()),
            'useGrecaptcha': False,
        }
        return data

    def get_api_response_data_dict(self):
        """
        Returns a dictionary with state and messages for the form and all its fields.
        """
        data_dict = self.get_form_state_and_messages_dict()
        fields = []

        for field_name, field in self.fields.items():
            field_has_errors = field_name in self.errors.keys()
            field_data = {
                'id': field_name,
                'state': {
                    'error': bool(field_has_errors),
                }
            }

            if field_has_errors:
                field_data['messages'] = {
                    'error': self.errors[field_name]
                }

            fields.append(field_data)

        data_dict['fields'] = fields

        return data_dict


class ReCaptchaFormMixin(object):
    invalid_recaptcha = _('Invalid reCAPTCHA')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ReCaptchaFormMixin, self).__init__(*args, **kwargs)

    def clean(self):
        if settings.RECAPTCHA_IS_ACTIVE:
            self.verify()
        return super(ReCaptchaFormMixin, self).clean()

    def verify(self):
        try:
            remote_ip = self.request._request.META.get('REMOTE_ADDR')
        except AttributeError:
            raise ValueError('ReCaptchaFormMixin has no request specified.')

        try:
            recaptcha_form_value = self.request.data['g-recaptcha-response']
        except:
            raise ValidationError(self.invalid_recaptcha)

        response = requests.post(
            url=settings.RECAPTCHA_URL,
            data={
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': recaptcha_form_value,
                'remoteip': remote_ip
            }
        )

        if response.status_code == 200:
            response_json_data = response.json()
            if response_json_data.get('success'):
                return True

        raise ValidationError(self.invalid_recaptcha)

    def get_submit_button(self):
        data = super(ReCaptchaFormMixin, self).get_submit_button()
        data['useGrecaptcha'] = True
        data['recaptcha_sitekey'] = settings.RECAPTCHA_SITE_KEY
        return data


class SpaApiModelForm(six.with_metaclass(ModelFormMetaclass, BaseModelForm)):
    default_validation_error = DEFAULT_VALIDATION_ERROR
    no_cookie_message = NO_COOKIE_MESSAGE
    submit_button_label = SUBMIT_BUTTON_LABEL
    show_general_error_message = True

    def get_api_url(self):
        return ''

    def get_spa_data_dict(self):
        """
        Returns a dictionary that is used to render the form.
        """
        data_dict = self._get_form_state_and_messages_dict()
        data_dict['url'] = self.get_api_url()
        data_dict['no_cookie_message'] = str(self.no_cookie_message)
        data_dict['fields'] = self.get_fields_data_dict()
        return data_dict

    def get_api_response_data_dict(self):
        """
        Returns a dictionary with state and messages for the form and all its fields.
        """
        data_dict = self._get_form_state_and_messages_dict()
        fields = []

        for field_name, field in self.fields.items():
            field_has_errors = field_name in self.errors.keys()
            field_data = {
                'id': field_name,
                'state': {
                    'error': field_has_errors,
                }
            }

            if field_has_errors:
                field_data['messages'] = {
                    'error': self.errors[field_name]
                }

            fields.append(field_data)

        data_dict['fields'] = fields

        return data_dict

    def get_fields_data_dict(self):
        fields = [self._get_form_field_data_dict(name=name, field=field) for name, field in self.fields.items()]
        fields.append(self.get_submit_button())
        return fields

    def get_submit_button(self):
        return {
            'component': 'cmp-form-submit',
            'label': str(self.submit_button_label),
        }

    def _get_form_state_and_messages_dict(self):
        data_dict = {
            'state': {
                'error': bool(self.errors)
            }
        }

        error_messages = []
        if self.errors and self.show_general_error_message:
            error_messages.append(str(self.default_validation_error))
        non_field_errors = self.errors.get(ALL_FIELDS)
        if non_field_errors:
            error_messages += non_field_errors
        if error_messages:
            data_dict['messages'] = {
                'error': error_messages
            }

        return data_dict

    def _get_form_field_data_dict(self, name, field):
        renderer = SPAFormFieldWidgetRenderer(form=self, field=field, name=name)
        field_data = renderer.render()
        return field_data


class SpaApiFieldsetModelForm(SpaApiModelForm):
    def get_spa_data_dict(self):
        data_dict = self._get_form_state_and_messages_dict()
        data_dict['url'] = self.get_api_url()
        data_dict['no_cookie_message'] = str(self.no_cookie_message)
        data_dict['fieldsets'] = self.get_fieldset_data_dict()
        return data_dict

    def get_fieldset_data_dict(self):
        fieldsets = []

        for fieldset in self.fieldsets:
            fieldset_name = str(fieldset[0])
            fieldset_fields = fieldset[1].get('fields')
            fieldset_data = {
                'name': fieldset_name,
                'fields': []
            }

            for field_name in fieldset_fields:
                field = self.fields.get(field_name)
                fieldset_data['fields'].append(self._get_form_field_data_dict(name=field_name, field=field))

            fieldsets.append(fieldset_data)

        fieldsets[-1]['fields'].append(self.get_submit_button())

        return fieldsets
