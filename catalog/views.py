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
from django.views.generic.edit import ModelFormMixin

from accounts.decorators import is_friend
from catalog.models import BookInstance, Book
from catalog.form import BookInstanceForm, FriendsBookInstanceForm
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
        return BookInstance.objects.filter(book_owner=user).order_by('due_back')

    @method_decorator(is_friend())
    def dispatch(self, *args, **kwargs):
        return super(UsersBookListView, self).dispatch(*args, **kwargs)


@login_required
# @method_decorator(is_friend())
def create_book_instance(request, pk_user):
    # TODO co z dekoratorem
    user = User.objects.get(id=pk_user)
    if user == request.user:
        form = BookInstanceForm(initial={'book_owner': user, 'status': 'a'})
    else:
        form = FriendsBookInstanceForm(initial={'book_owner': user, 'status': 'a'})

    if request.method == 'POST':
        if 'sub_adding' in request.POST:
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
        return reverse('users_books_url')

    @method_decorator(is_friend())
    def dispatch(self, *args, **kwargs):
        return super(BookInstanceDelete, self).dispatch(*args, **kwargs)


class BookInstanceUpdate(UpdateView):
    model = BookInstance
    fields = ['status', 'due_back', 'book_holder', 'comment']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('users_books_url')

    @method_decorator(is_friend())
    def dispatch(self, *args, **kwargs):
        return super(BookInstanceUpdate, self).dispatch(*args, **kwargs)


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
# @method_decorator(is_friend())
def create_book_from_api(request, pk_user):
    # TODO co z dekoratorem
    user = User.objects.get(id=pk_user)
    if request.method == 'POST':
        api = googlebooks.Api()
        isbn = request.POST["isbn"]
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
            new_instance = BookInstance(book=book_exists, book_owner=user)
            new_instance.save()
            messages.add_message(request, messages.SUCCESS, 'Book added to library.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
