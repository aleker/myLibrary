from django.forms import ModelForm
from catalog.models import BookInstance, Book


class BookInstanceForm(ModelForm):
    class Meta:
        model = BookInstance
        fields = ('book', 'status', 'due_back', 'book_holder')


class FriendsBookInstanceForm(ModelForm):
    class Meta:
        model = BookInstance
        fields = ('book',)


class BookFormFromAPI(ModelForm):
    class Meta:
        model = Book
        fields = ('isbn_13',)
