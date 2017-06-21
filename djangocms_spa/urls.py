from django.conf.urls import url

from .views import SpaCmsPageDetailApiView

urlpatterns = [
    url(r'^pages/$', SpaCmsPageDetailApiView.as_view(), name='cms_page_detail_home'),
    url(r'^pages/(?P<path>.*)/$', SpaCmsPageDetailApiView.as_view(), name='cms_page_detail'),
]
