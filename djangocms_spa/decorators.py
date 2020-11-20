from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.template.response import ContentNotRenderedError


def cache_view(view_func):
    @wraps(view_func)
    def _wrapped_view_func(view: 'CachedApiView', *args, **kwargs):
        request = view.request

        cache_key = view.get_cache_key()
        if not cache_key:
            cache_key = request.get_full_path()

        if view.add_language_code:
            try:
                language_code = request.LANGUAGE_CODE
            except AttributeError:
                language_code = settings.LANGUAGE_CODE
            cache_key += ':%s' % language_code

        cached_response = cache.get(cache_key)

        if cached_response and not request.user.is_authenticated:
            return cached_response

        response = view_func(view, *args, **kwargs)

        if response.status_code == 200 and not request.user.is_authenticated:
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
