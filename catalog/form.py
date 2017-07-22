from django import forms
from django.forms import ModelForm
from catalog.models import BookInstance, Book

from functools import partial
DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class BookInstanceForm(ModelForm):
    class Meta:
        model = BookInstance
        fields = ('book', 'book_owner', 'status', 'borrowed_day', 'due_back', 'book_holder', 'comment')
        widgets = {
            'due_back': forms.DateInput(attrs={'class': 'datepicker'}),
            'borrowed_day': forms.DateInput(attrs={'class': 'datepicker'}),
        }

    def __init__(self, *args, **kwargs):
        super(BookInstanceForm, self).__init__(*args, **kwargs)
        try:
            self.fields['book_owner'].widget = forms.HiddenInput()
        except:
            pass


class FriendsBookInstanceForm(ModelForm):
    class Meta:
        model = BookInstance
        fields = ('book', 'book_owner', 'status', 'comment')

    def __init__(self, *args, **kwargs):
        super(FriendsBookInstanceForm, self).__init__(*args, **kwargs)
        try:
            self.fields['book_owner'].widget = forms.HiddenInput()
            self.fields['status'].widget = forms.HiddenInput()
        except:
            pass


class BookFormFromAPI(ModelForm):
    class Meta:
        model = Book
        fields = ('isbn_13',)
