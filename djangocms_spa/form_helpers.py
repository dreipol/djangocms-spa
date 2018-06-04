def get_placeholder_for_choices_field(field):
    choices = get_choices_for_field(field)
    for choice in choices:
        label = str(choice[1])
        value = str(choice[0])

        if not value:
            return label
    return '---------'


def get_serialized_choices_for_field(field):
    choices = get_choices_for_field(field)
    serialized_choices = []

    for choice in choices:
        label = str(choice[1])
        value = str(choice[0])

        if label and value:
            serialized_choices.append({
                'label': label,
                'val': value
            })

    return serialized_choices


def get_choices_for_field(field):
    try:
        return field.choices
    except AttributeError:
        try:
            return field.widget.choices
        except AttributeError:
            return []
