from rest_framework import serializers

from .fields import CheckboxField, EmailField, InputField, RadioField, TextareaField


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
