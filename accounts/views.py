from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from catalog.functionality import average_month_reading, currently_reading


@login_required
def profile(request, *args, **kwargs):
    (last_month, book_list) = average_month_reading(request.user)
    book_count = 0
    if book_list:
        book_count = len(book_list)

    cur_book_list = currently_reading(request.user)
    cur_book_count = 0
    if cur_book_list:
        cur_book_count = len(cur_book_list)

    return render(request, "profile.html", {'last_month': last_month,
                                            'book_list': book_list,
                                            'book_count': book_count,
                                            'cur_book_list': cur_book_list,
                                            'cur_book_count': cur_book_count})




