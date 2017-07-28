import datetime
import googlebooks
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView, UpdateView, CreateView
from django.views import generic

from accounts.decorators import is_friend, is_me, is_friend2, is_me2
from catalog.filters import BookFilter, BookInstanceFilter
from catalog.models import BookInstance, Book, BookReadingHistory
from catalog.form import BookInstanceForm, FriendsBookInstanceForm, BookInstanceEditForm
from history.models import History
from myLibrary import settings


@login_required
def catalog(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available},
    )


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookCreate(CreateView):
    model = Book
    template_name_suffix = '_create_form'
    fields = ['title', 'author', 'genre', 'summary', 'isbn_13', 'cover_url']

    def get_success_url(self):
        return reverse('all_books_url')


class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'genre', 'summary', 'isbn_13', 'cover_url']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('all_books_url')


@login_required
def book_detail_view(request, pk):
    try:
        book_id = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        raise Http404("Book does not exist")
    return render(request, 'catalog/book_detail.html', context={'book': book_id,
                                                                'cover_url': settings.blank_cover_url, })


class UsersBookListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/users_book_list.html'
    paginate_by = 10

    # filter what you want to return:
    def get_queryset(self, **kwarg):
        pk_user = self.kwargs.get('pk_user', '')
        user = User.objects.get(id=pk_user)
        return BookInstance.objects.filter(book_owner=user).order_by('-status', 'book')

    @method_decorator(is_friend())
    def dispatch(self, *args, **kwargs):
        return super(UsersBookListView, self).dispatch(*args, **kwargs)


class BorrowedFromListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/borrowed_book_list.html'
    paginate_by = 10

    def get_queryset(self, **kwarg):
        pk_user = self.kwargs.get('pk_user', '')
        user = User.objects.get(id=pk_user)
        return BookInstance.objects.filter(book_holder=user).order_by('borrowed_day', 'book')

    @method_decorator(is_me())
    def dispatch(self, *args, **kwargs):
        return super(BorrowedFromListView, self).dispatch(*args, **kwargs)


@login_required
@is_friend2
def create_book_instance(request, *args, **kwargs):
    pk_user = kwargs['pk_user']
    user = User.objects.get(id=pk_user)
    if user == request.user:
        form = BookInstanceForm(initial={'book_owner': user, 'status': 'a'})
    else:
        form = FriendsBookInstanceForm(initial={'book_owner': user, 'status': 'a'})

    if request.method == 'POST':
        if 'sub_adding_by_book' in request.POST:
            requested_book_pk = request.POST['book_pk']
            requested_book = Book.objects.get(pk=requested_book_pk)
            form = BookInstanceForm(initial={'book_owner': user, 'status': 'a', 'book': requested_book})
            if form.is_valid():
                form.save()
                return redirect('users_books_url', pk_user=pk_user)
        elif 'sub_adding' in request.POST:
            if user == request.user:
                form = BookInstanceForm(request.POST, initial={'book_owner': user, 'status': 'a'})
            else:
                form = FriendsBookInstanceForm(request.POST, initial={'book_owner': user, 'status': 'a'})
            if form.is_valid():
                form.save()
                return redirect('users_books_url', pk_user=pk_user)
        elif 'sub_searching' in request.POST:
            api = googlebooks.Api()
            search_value = request.POST['search_value']
            search_type = request.POST['search_type']
            # langRestrict='en'
            found_books = api.list(search_type + ':' + search_value, maxResults=40, printType="books")
            return render(request, 'catalog/bookinstance_form.html',
                          {'form': form, 'found_books': found_books})
        elif 'add_outer' in request.POST:
            if user == request.user:
                form = BookInstanceForm(request.POST, initial={'book_owner': user, 'status': 'a'})
            else:
                form = FriendsBookInstanceForm(request.POST, initial={'book_owner': user, 'status': 'a'})
            return render(request, 'catalog/bookinstance_form.html', {'form': form})
    # for GET:
    return render(request, 'catalog/bookinstance_form.html', {'form': form})


class BookInstanceDelete(DeleteView):
    model = BookInstance
    template_name_suffix = '_delete_form'

    def get_success_url(self):
        return reverse('users_books_url', kwargs={'pk_user': self.kwargs.get('pk_user', '')})

    @method_decorator(is_friend())
    def dispatch(self, *args, **kwargs):
        return super(BookInstanceDelete, self).dispatch(*args, **kwargs)


class BookInstanceUpdate(UpdateView):
    model = BookInstance
    form_class = BookInstanceEditForm
    template_name_suffix = '_update_form'

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Book instance updated.")
        return reverse('users_books_url', kwargs={'pk_user': self.kwargs.get('pk_user', '')})

    @method_decorator(is_me())
    def dispatch(self, *args, **kwargs):
        return super(BookInstanceUpdate, self).dispatch(*args, **kwargs)

    def post(self, request, **kwargs):
        if request.POST['status'] == 'a':
            requested_book_instance = BookInstance.objects.filter(id=kwargs['pk']).first()
            if requested_book_instance and requested_book_instance.status != 'a':
                add_to_history(request, requested_book_instance)
            if requested_book_instance and requested_book_instance.status == 'a':
                add_now_reading(request, **kwargs)
        return super(BookInstanceUpdate, self).post(request, **kwargs)


def isbn_page(request):
    isbn_no = request.GET["isbn"]
    link = get_book_url_by_isbn(isbn_no)
    if link:
        return HttpResponseRedirect(link)
    return book_detail_view(request, request.GET["pk"])


def get_book_url_by_isbn(isbn):
    api = googlebooks.Api()
    book = api.list('isbn:' + isbn)
    if book and book["totalItems"] > 0:
        link = book["items"][0]["volumeInfo"]["canonicalVolumeLink"]
        return link
    return None


@login_required
@is_friend2
def create_book_from_api(request, *args, **kwargs):
    pk_user = kwargs["pk_user"]
    user = User.objects.get(id=pk_user)
    if request.method == 'POST':
        api = googlebooks.Api()
        isbn = request.POST["isbn"]
        comment = request.POST['comment']
        book = api.list('isbn:' + isbn)
        if book and book["totalItems"] > 0:
            try:
                title = book["items"][0]["volumeInfo"]["title"]
                author = book["items"][0]["volumeInfo"]["authors"][0]
                image_url = book["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
            except:
                messages.add_message(request, messages.WARNING, 'There is lack of information in chosen book.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            book_exists = Book.objects.filter(title=title, author=author).first()
            if book_exists is None:
                new_book = Book(title=title, author=author, isbn_13=isbn, cover_url=image_url)
                new_book.save()
                transaction.commit()
                book_exists = new_book
            else:
                book_instance_exists = BookInstance.objects.filter(book=book_exists, book_owner=user).first()
                if book_instance_exists is not None:
                    messages.add_message(request, messages.WARNING, 'This book already is in your library.')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            new_instance = BookInstance(book=book_exists, book_owner=user, comment=comment)
            new_instance.save()
            messages.add_message(request, messages.SUCCESS, 'Book added to library.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@is_me2
def give_book_back(request, *args, **kwargs):
    pk_user = kwargs["pk_user"]
    pk_book = kwargs["pk"]
    book_instance = BookInstance.objects.get(pk=pk_book)
    add_to_history(request, book_instance)
    try:
        book_instance.status = 'a'
        book_instance.book_holder = None
        book_instance.borrowed_day = None
        book_instance.save()
        messages.add_message(request, messages.SUCCESS, "Borrowed book is no longer in your library.")
    except:
        messages.add_message(request, messages.WARNING, 'Problem occurred when giving book back.')
    return redirect('borrowed_books_url', pk_user=pk_user)


@transaction.atomic
def add_to_history(request, book_instance):
    try:
        holder = 'outside'
        if book_instance.book_holder:
            holder = book_instance.book_holder.username
        todays_day = datetime.date.today()
        # create history:
        hist = History(book_instance=book_instance,
                       book_holder_name=holder,
                       book_owner_name=book_instance.book_owner.username,
                       borrowed_day=book_instance.borrowed_day,
                       returning_day=todays_day)
        # hist.save(force_insert=True)
        hist.save()
        messages.add_message(request, messages.SUCCESS, "New position added to book history.")
    except:
        messages.add_message(request, messages.WARNING, 'Problem occurred when adding new position to history.')


def search_book(request):
    book_list = Book.objects.all()
    book_filter = BookFilter(request.GET, queryset=book_list)
    return render(request, 'search/book_list.html', {'filter': book_filter})


@login_required
@is_friend2
def search_bookinstance(request, *args, **kwargs):
    pk_user = kwargs["pk_user"]
    user = User.objects.get(id=pk_user)
    book_list = BookInstance.objects.filter(book_owner=user)
    book_filter = BookInstanceFilter(request.GET, queryset=book_list)
    return render(request, 'search/bookinstance_list.html', {'filter': book_filter})


@login_required
@is_me2
def add_now_reading(request, **kwargs):
    pk_user = request.user.pk
    pk_book = kwargs["pk"]
    pk_owner = kwargs["pk_user"]
    reader = User.objects.get(pk=pk_user)
    book_instance = BookInstance.objects.get(pk=pk_book)
    add_now_reading_to_history(request, book_instance, reader)
    return redirect('borrowed_books_url', pk_user=pk_user)


@transaction.atomic
def add_now_reading_to_history(request, book_instance, reader):
    todays_day = datetime.date.today()
    try:
        hist = None
        if "now_reading" in request.POST:
            # if: exits hist when this bookinstance is reading now
            hist = BookReadingHistory.objects.filter(book_instance=book_instance,
                                                     reader=reader,
                                                     end_reading=None).first()
            if hist:
                return
            # else: create new hist
            hist = BookReadingHistory(book_instance=book_instance,
                                      reader=reader,
                                      start_reading=todays_day,
                                      end_reading=None)
            hist.save()
            messages.add_message(request, messages.SUCCESS, "New position added to reading history.")
        else:
            # if: exits hist when this bookinstance was reading until now
            hist = BookReadingHistory.objects.filter(book_instance=book_instance,
                                                     reader=reader,
                                                     end_reading=None).first()
            if not hist:
                return
            hist.end_reading = todays_day
            hist.save()
            messages.add_message(request, messages.SUCCESS, "Reading history updated.")
    except:
        messages.add_message(request, messages.WARNING, 'Problem occurred when adding new position to reading history.')


class BookReadingHistoryList(LoginRequiredMixin, generic.ListView):
    model = BookReadingHistory
    template_name_suffix = '_list_form'
    paginate_by = 10

    # filter what you want to return:
    def get_queryset(self, **kwarg):
        pk_book_instance = self.kwargs.get('pk')
        book_instance = BookInstance.objects.get(id=pk_book_instance)
        return BookReadingHistory.objects.filter(book_instance=book_instance).order_by('-start_reading')

    @method_decorator(is_friend())
    def dispatch(self, *args, **kwargs):
        return super(BookReadingHistoryList, self).dispatch(*args, **kwargs)
