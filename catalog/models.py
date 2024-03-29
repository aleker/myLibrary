import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse     # Used to generate URLs by reversing the URL patterns
import datetime

alphanumeric = RegexValidator(r'^[a-zA-Z ]+$', 'Only alphanumeric characters are allowed.')


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
    genre = models.ManyToManyField(Genre, blank=True, help_text="Select a genre for this book")
    isbn_13 = models.CharField('ISBN', max_length=13, null=True, blank=True,
                               help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    cover_url = models.URLField(null=True, blank=True)

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
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('l', 'Loaned to'),
        ('o', 'Outside'),
        ('a', 'Available'),
    )
    status = models.CharField(max_length=1, choices=LOAN_STATUS, null=False, blank=False, default='a')
    borrowed_day = models.DateField(null=True, blank=True, default=datetime.date.today)
    book_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="owned_books")
    book_holder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="held_books")
    comment = models.TextField(null=True, blank=True, max_length=1000)
    now_reading = models.BooleanField(null=False, blank=False, default=False)

    class Meta:
        ordering = ["-status", "book"]
        unique_together = (("book", "book_owner"),)

    def __str__(self):
        """
        String for representing the Model object
        """
        if self.book is None:
            return '%s (%s)' % (None, self.book_owner.username)
        else:
            return '%s (%s)' % (self.book.title, self.book_owner.username)

    def clean(self):
        if self.status == 'a':
            self.borrowed_day = None
            self.book_holder = None

        if self.status == 'l' or self.status == 'o':
            if self.borrowed_day is None:
                raise ValidationError('"Borrowed day" is required if status is not "Available".')
            if self.now_reading:
                raise ValidationError("You can't read book and lend it to someone at the same time.")

        if self.status == 'o':
            self.book_holder = None

        if self.status == 'l' and self.book_holder is None:
            raise ValidationError('"Book holder" is required if status is "Loaned to".')

        if self.book_owner == self.book_holder:
            raise ValidationError("You can't lean book to yourself ;_;")


class BookReadingHistory(models.Model):
    book_instance = models.ForeignKey(BookInstance, on_delete=models.CASCADE, null=False, blank=False)
    reader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    start_reading = models.DateField(null=False, blank=False, default=datetime.date.today)
    end_reading = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-start_reading", "book_instance"]
        # unique_together = (("book_instance", "reader", "start_reading"),)

    def __str__(self):
        """
        String for representing the Model object
        """
        if self.book_instance and self.start_reading and self.end_reading:
            return '%s (%s - %s)' % (self.book_instance, self.start_reading, self.end_reading)
        elif self.book_instance and self.start_reading:
            return '%s (%s - now)' % (self.book_instance, self.start_reading)
        else:
            return '%s' % self.book_instance


# from tutorial: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models
