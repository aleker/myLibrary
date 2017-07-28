from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from catalog.functionality import average_month_reading, currently_reading, currently_borrowed_from, currently_lend_to


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

    borrowed_from_count = currently_borrowed_from(request.user)
    lend_to_count = currently_lend_to(request.user)

    return render(request, "profile.html", {'last_month': last_month,
                                            'book_list': book_list,
                                            'book_count': book_count,
                                            'cur_book_list': cur_book_list,
                                            'cur_book_count': cur_book_count,
                                            'borrowed_count': borrowed_from_count,
                                            'lend_count': lend_to_count})




