import uuid

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse     # Used to generate URLs by reversing the URL patterns
from datetime import date


alphanumeric = RegexValidator(r'^[a-zA-Z ]+$', 'Only alphanumeric characters are allowed.')


@property
def is_overdue(book_instance):
    if book_instance.due_back and date.today() > book_instance.due_back:
        return True
    return False


class Genre(models.Model):
    """
    Model representing a book genre.
    """
    name = models.CharField(max_length=200, help_text="Enter a book genre.")

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name


class Book(models.Model):
    """
    Model representing a book (but not a specific copy of a book).
    """
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, validators=[alphanumeric])
    summary = models.TextField(null=True, blank=True, max_length=1000, help_text="Enter a brief description of the book")
    genre = models.ManyToManyField(Genre, null=True, blank=True, help_text="Select a genre for this book")
    isbn_13 = models.CharField('ISBN', max_length=13, null=True, blank=True,
                               help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    class Meta:
        ordering = ["title"]
        unique_together = (("title", "author"),)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.title

    def get_absolute_url(self):
        """
        Returns the url to access a particular book instance.
        """
        return reverse('book_detail_url', args=[str(self.id)])


class BookInstance(models.Model):
    """
    Model representing a specific copy of a book (i.e. that can be borrowed from the library).
    """
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)

    LOAN_STATUS = (
        ('b', 'Borrowed from'),
        ('f', 'From outside'),
        ('l', 'Loaned to'),
        ('o', 'On outside'),
        ('a', 'Available'),
    )
    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=False, default='a', help_text='Book availability')
    due_back = models.DateField(null=True, blank=True)
    book_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="owned_books")
    book_holder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="held_books")

    class Meta:
        ordering = ['book_owner', 'book']
        unique_together = (("book", "book_owner"),)

    def __str__(self):
        """
        String for representing the Model object
        """
        if self.book is None:
            return '%s (%s)' % (None, self.book_owner.username)
        else:
            return '%s (%s)' % (self.book.title, self.book_owner.username)


# from tutorial: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models
