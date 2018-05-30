class BaseFormField(object):
    def __init__(self, id, label='', val=''):
        self.id = id
        self.component = ''
        self.state = {'required': True}
        self.label = label
        self.val = val


class CheckboxField(BaseFormField):
    def __init__(self, items, **kwargs):
        super().__init__(**kwargs)
        self.val = []
        self.component = 'cmp-form-field-bool'
        self.type = 'checkbox'
        self.multiline = True
        self.items = items


class EmailField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.component = 'cmp-form-field-input'
        self.type = 'email'


class InputField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.component = 'cmp-form-field-input'
        self.type = 'text'
        self.autocomplete = 'off'


class RadioField(BaseFormField):
    def __init__(self, items, **kwargs):
        super().__init__(**kwargs)
        self.component = 'cmp-form-field-bool'
        self.type = 'radio'
        self.multiline = True
        self.items = items


class TextareaField(BaseFormField):
    def __init__(self, maxlength=None, **kwargs):
        super().__init__(**kwargs)
        self.component = 'cmp-form-field-textarea'

        if maxlength:
            self.maxlength = maxlength
