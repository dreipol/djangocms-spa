from django.urls import path, re_path

from .views import SpaCmsPageDetailApiView

app_name = 'djangocms_spa'
urlpatterns = [
    path('pages/', SpaCmsPageDetailApiView.as_view(), name='cms_page_detail_home'),
    re_path(r'^pages/(?P<path>.*)/$', SpaCmsPageDetailApiView.as_view(), name='cms_page_detail'),
]
