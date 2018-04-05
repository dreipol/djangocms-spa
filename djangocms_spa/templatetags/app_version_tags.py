from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def app_version():
    try:
        return settings.GIT_COMMIT_HASH
    except AttributeError:
        return ''
