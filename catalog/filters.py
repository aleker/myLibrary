import django_filters

from catalog.models import Book, BookInstance


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Book
        fields = ['title', 'author', ]


class BookInstanceFilter(django_filters.FilterSet):
    book__title = django_filters.CharFilter(lookup_expr='icontains')
    book__author = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = BookInstance
        fields = ['book__title', 'book__author', ]
