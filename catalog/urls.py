from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.catalog, name='catalog_url'),
    url(r'^books/$', views.BookListView.as_view(), name='all_books_url'),
    url(r'^book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name='book_detail_url'),

]
