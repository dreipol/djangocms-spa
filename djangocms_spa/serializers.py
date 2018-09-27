from collections import OrderedDict

from cms.models import CMSPlugin, Page, Placeholder
from django.conf import settings
from django.utils.translation import get_language
from rest_framework import serializers
from rest_framework.fields import empty

from .content_helpers import (get_custom_partial_data, get_partial_names_for_template, get_static_placeholder,
                              split_static_placeholders_and_custom_partials)
from .fields import CheckboxField, EmailField, InputField, RadioField, TextareaField


class GenericPluginSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = None

    def get_fields(self):
        fields = super(GenericPluginSerializer, self).get_fields()

        # Don't expose fields of the CMSPlugin class.
        fields_to_exclude = [field.name for field in CMSPlugin._meta.get_fields()]
        filtered_fields = OrderedDict()
        for key, value in fields.items():
            if key not in fields_to_exclude:
                filtered_fields[key] = value

        return filtered_fields

    def to_representation(self, instance):
        representation = super(GenericPluginSerializer, self).to_representation(instance=instance)
        try:
            representation = instance.spa_data(data=representation)
        except AttributeError:
            pass
        return representation


class PluginSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    plugins = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = CMSPlugin
        fields = ('content', 'type', 'plugins')

    @staticmethod
    def get_type(obj):
        return obj.get_plugin_class().frontend_component_name

    @staticmethod
    def get_content(obj):
        instance, plugin = obj.get_plugin_instance()
        try:
            serializer_class = instance.get_serializer()
        except AttributeError:
            return {}

        return serializer_class(instance=instance).data

    @staticmethod
    def get_plugins(obj):
        instance, plugin = obj.get_plugin_instance()
        if not plugin.parse_child_plugins:
            return []

        serializer = PluginSerializer(instance=obj.get_children(), many=True)
        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance=instance)
        if representation.get('plugins') == list():
            representation.pop('plugins')
        return representation


class PlaceholderSerializer(serializers.ModelSerializer):
    plugins = PluginSerializer(many=True, read_only=True, source='cmsplugin_set')
    type = serializers.SerializerMethodField()

    class Meta:
        model = Placeholder
        fields = ('plugins', 'type')

    @staticmethod
    def get_type(obj):
        return settings.DJANGOCMS_SPA_COMPONENT_PREFIX + obj.slot


class PageSerializer(serializers.ModelSerializer):
    partials = serializers.SerializerMethodField()
    placeholders = serializers.SerializerMethodField()

    is_draft_mode = False
    requested_partials = None

    class Meta:
        model = Page
        fields = ('partials', 'placeholders')

    def __init__(self, instance=None, data=empty, request=empty, **kwargs):
        self.request = request
        self.is_draft_mode = (hasattr(self.request, 'toolbar') and self.request.toolbar.edit_mode and
                              self.request.user.has_perm('cms.edit_static_placeholder'))
        super(PageSerializer, self).__init__(instance=instance, data=data, **kwargs)

    def get_placeholders(self, obj):
        placeholders = {}
        for placeholder in obj.placeholders.all():
            placeholders[placeholder.slot] = PlaceholderSerializer(instance=placeholder).data
        return placeholders

    def get_partials(self, obj):
        requested_partials = self.request.GET.get('partials')
        partial_names = get_partial_names_for_template(template=obj.get_template(), get_all=False,
                                                       requested_partials=requested_partials)

        partials = {}
        static_placeholders_names, custom_callbacks_names = split_static_placeholders_and_custom_partials(partial_names)
        for slot in static_placeholders_names:
            static_placeholder = get_static_placeholder(slot, self.is_draft_mode)
            partials[static_placeholder.slot] = PlaceholderSerializer(instance=static_placeholder).data

        partials.update(get_custom_partial_data(custom_callbacks_names, self.request))

        return partials

    def to_representation(self, instance):
        representation = super().to_representation(instance=instance)
        representation['containers'] = representation.pop('placeholders')

        page_title = instance.title_set.get(language=get_language())
        representation['meta'] = {
            'title': page_title.title,
            'description': page_title.meta_description,
            'languages': {code: instance.get_absolute_url(language=code) for code, path in settings.LANGUAGES}
        }
        return representation


class FieldItemSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.CharField()

    def to_representation(self, obj):
        return {
            'val': obj[0],
            'label': str(obj[1])
        }


class BaseFormFieldSerializer(serializers.Serializer):
    id = serializers.CharField()
    component = serializers.CharField()
    state = serializers.DictField()
    label = serializers.CharField()
    val = serializers.CharField()
    facet = serializers.CharField()


class CheckboxFieldSerializer(BaseFormFieldSerializer):
    val = serializers.ListField()
    type = serializers.CharField()
    facet = serializers.CharField()
    items = FieldItemSerializer(many=True)


class EmailFieldSerializer(BaseFormFieldSerializer):
    type = serializers.CharField()


class FileFieldSerializer(BaseFormFieldSerializer):
    type = serializers.CharField()


class InputFieldSerializer(BaseFormFieldSerializer):
    type = serializers.CharField()
    autocomplete = serializers.CharField()


class RadioFieldSerializer(BaseFormFieldSerializer):
    type = serializers.CharField()
    items = FieldItemSerializer(many=True)


class TextareaFieldSerializer(BaseFormFieldSerializer):
    maxlength = serializers.IntegerField(required=False)


class GenericSerializerFormField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, CheckboxField):
            serializer = CheckboxFieldSerializer(value)
        elif isinstance(value, EmailField):
            serializer = EmailFieldSerializer(value)
        elif isinstance(value, InputField):
            serializer = InputFieldSerializer(value)
        elif isinstance(value, RadioField):
            serializer = RadioFieldSerializer(value)
        elif isinstance(value, TextareaField):
            serializer = TextareaFieldSerializer(value)
        else:
            raise Exception('Unexpected field type: %s' % type(value))
        return serializer.data
