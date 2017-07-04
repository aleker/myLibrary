from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^main/$', views.main_page, name='main_page_url'),
    url(r'', views.main_page),
]
