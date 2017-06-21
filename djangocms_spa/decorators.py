from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.template.response import ContentNotRenderedError
from django.utils.decorators import available_attrs


def cache_view(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view_func(view, *args, **kwargs):
        request = view.request
        language_code = request.LANGUAGE_CODE
        cache_key = '{path}:{lang}'.format(path=request.get_full_path(), lang=language_code)
        cached_response = cache.get(cache_key)

        if cached_response and not request.user.is_authenticated():
            return cached_response

        response = view_func(view, *args, **kwargs)

        if response.status_code == 200 and not request.user.is_authenticated():
            try:
                set_cache_after_rendering(cache_key, response, settings.DJANGOCMS_SPA_CACHE_TIMEOUT)
            except ContentNotRenderedError:
                response.add_post_render_callback(
                    lambda r: set_cache_after_rendering(cache_key, r, settings.DJANGOCMS_SPA_CACHE_TIMEOUT)
                )

        return response

    return _wrapped_view_func


def set_cache_after_rendering(cache_key, response, timeout):
    cache.set(cache_key, response, timeout)
