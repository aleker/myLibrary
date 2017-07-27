import datetime

from catalog.models import BookReadingHistory


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



