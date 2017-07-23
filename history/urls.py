from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^(?P<pk>\d+)$', login_required(views.HistoryListView.as_view()), name='books_history_url'),

]
