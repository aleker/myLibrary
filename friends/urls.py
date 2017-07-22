from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^$', views.friends, name='friends_url'),
    url(r'^delete/(?P<pk>\d+)/$', login_required(views.FriendDelete.as_view()), name='friend_delete_url'),

]



