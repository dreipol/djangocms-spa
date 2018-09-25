from collections import OrderedDict

from cms.models import CMSPlugin, Page, Placeholder
from django.conf import settings
from rest_framework import serializers

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
    # TODO: add partials
    placeholders = PlaceholderSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = ('placeholders',)

    def to_representation(self, instance):
        representation = super().to_representation(instance=instance)
        representation['containers'] = representation.pop('placeholders')
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
