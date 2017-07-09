from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # maps an empty string to  function views.index name is the name that will be used to identify the view
    # unused:
    # TODO deleting link:
    # url(r'^signup/$', views.signup, name='signup_url'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login_url'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout_url'),
    url(r'^profile/$', views.profile, name='profile_url'),
]
