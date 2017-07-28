import datetime

from catalog.models import BookReadingHistory, BookInstance


def average_month_reading(user):
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = (first - datetime.timedelta(days=1)).replace(day=1)
    book_reading_history = BookReadingHistory.objects.filter(
        reader=user,
        end_reading__gte=last_month
    ).order_by('-end_reading', '-start_reading')
    return last_month, book_reading_history


def currently_reading(user):
    book_reading_history = BookReadingHistory.objects.filter(
        reader=user,
        end_reading=None
    )
    return book_reading_history


def currently_borrowed_from(user):
    borrowed_books = BookInstance.objects.filter(book_holder=user)
    return len(borrowed_books)


def currently_lend_to(user):
    borrowed_books = BookInstance.objects.filter(book_owner=user).exclude(status='a')
    return len(borrowed_books)


