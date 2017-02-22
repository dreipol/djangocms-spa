from django.conf.urls import url

from .views import SpaCmsPageDetailApiView

urlpatterns = [
    url(r'^(?P<language_code>[\w-]+)/pages/$', SpaCmsPageDetailApiView.as_view(), name='cms_page_detail_home'),
    url(r'^(?P<language_code>[\w-]+)/pages/(?P<path>.*)/$', SpaCmsPageDetailApiView.as_view(), name='cms_page_detail'),
]
