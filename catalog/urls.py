from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.catalog, name='catalog_url'),
    url(r'^books/$', views.BookListView.as_view(), name='all_books_url'),
    url(r'^book/(?P<pk>\d+)$', views.book_detail_view, name='book_detail_url'),
    url(r'^authors/$', views.AuthorListView.as_view(), name='all_authors_url'),
    url(r'^author/(?P<pk>\d+)$', views.author_detail_view, name='author_detail_url'),
    url(r'^mybooks/$', views.UsersBookListView.as_view(), name='users_books_url'),
    url(r'^mybooks/create/$', views.BookInstanceCreate.as_view(), name='users_book_create_url'),
]
