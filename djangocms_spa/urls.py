from django.conf import settings
from django.conf.urls import url

from .views import PageDetailAPIView, SpaCmsPageDetailApiView

if settings.DJANGOCMS_SPA_USE_SERIALIZERS:
    urlpatterns = [
        url(r'^pages/(?P<path>.*)/$', PageDetailAPIView.as_view(), name='cms_page_detail'),
    ]
else:
    urlpatterns = [
        url(r'^pages/$', SpaCmsPageDetailApiView.as_view(), name='cms_page_detail_home'),
        url(r'^pages/(?P<path>.*)/$', SpaCmsPageDetailApiView.as_view(), name='cms_page_detail'),
    ]
