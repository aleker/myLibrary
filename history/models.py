import datetime
from django.contrib.auth.models import User
from django.db import models


class History(models.Model):
    book_instance = models.ForeignKey('catalog.BookInstance', on_delete=models.CASCADE, null=False, blank=False)
    borrowed_day = models.DateField(null=False, blank=False, default=datetime.date.today)
    returning_day = models.DateField(null=True, blank=True, default=datetime.date.today)
    book_owner_name = models.TextField(null=False, blank=False, max_length=30)
    book_holder_name = models.TextField(null=False, blank=False, max_length=30)

    class Meta:
        ordering = ['-borrowed_day']
        # unique_together = (("book_instance", "borrowed_day", "returning_day"),)

    def __str__(self):
        if self.borrowed_day is not None and self.returning_day is not None:
            return '%s (%s - %s)' % (self.book_instance.book.title, self.borrowed_day, self.returning_day)
        elif self.borrowed_day is not None:
            return '%s (%s - now)' % (self.book_instance.book.title, self.borrowed_day)
        else:
            return '%s' % self.book_instance.book.title
