from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^$', views.catalog, name='catalog_url'),
    url(r'^books/$', views.BookListView.as_view(), name='all_books_url'),
    url(r'^book/(?P<pk>\d+)$', views.book_detail_view, name='book_detail_url'),
    url(r'^book/$', views.isbn_page, name='book_isbn_url'),
    url(r'^(?P<pk_user>\d+)/mybooks/$', login_required(views.UsersBookListView.as_view()), name='users_books_url'),
    url(r'^(?P<pk_user>\d+)/mybooks/delete/(?P<pk>\d+)$', login_required(views.BookInstanceDelete.as_view()), name='users_books_delete_url'),
    url(r'^(?P<pk_user>\d+)/mybooks/edit/(?P<pk>\d+)$', login_required(views.BookInstanceUpdate.as_view()), name='users_books_update_url'),
    # url(r'^(?P<pk_user>\d+)/mybooks/create/$', views.BookInstanceCreate.as_view(), name='users_book_create_url'),
    url(r'^(?P<pk_user>\d+)/mybooks/create/$', views.create_book_instance, name='users_book_create_url'),
    url(r'^(?P<pk_user>\d+)/mybooks/createFromApi/$', views.create_book_from_api, name='users_book_create_from_api_url'),


]
