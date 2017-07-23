from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views import generic

from accounts.decorators import is_friend
from catalog.models import BookInstance
from history.models import History


class HistoryListView(LoginRequiredMixin, generic.ListView):
    model = History
    template_name_suffix = '_list_form'
    paginate_by = 10

    # filter what you want to return:
    def get_queryset(self, **kwarg):
        pk_book_instance = self.kwargs.get('pk')
        book_instance = BookInstance.objects.get(id=pk_book_instance)
        return History.objects.filter(book_instance=book_instance).order_by('borrowed_day')

    @method_decorator(is_friend())
    def dispatch(self, *args, **kwargs):
        return super(HistoryListView, self).dispatch(*args, **kwargs)
