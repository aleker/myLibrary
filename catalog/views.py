import googlebooks
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DeleteView, UpdateView

from catalog import models
from catalog.form import BookInstanceForm, BookFormFromAPI
from myLibrary import settings
from .models import Book, BookInstance
from django.views import generic


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
    #  the generic views look for templates in /application_name/theModelName_list.html
    # (catalog/book_list.html in this case) inside the application's /application_name/templates/ directory
    # (/catalog/templates/).
    model = Book
    paginate_by = 10

#
# class BookDetailView(generic.DetailView):
#     model = Book


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

    def get_queryset(self):
        return BookInstance.objects.filter(book_owner=self.request.user).order_by('due_back')


def create_book_instance(request):
    if request.method == 'POST':
        if 'sub_adding' in request.POST:
            form = BookInstanceForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('users_books_url')
        elif 'sub_searching' in request.POST:
            form = BookInstanceForm()
            api = googlebooks.Api()
            search_value = request.POST['search_value']
            search_type = request.POST['search_type']
            # langRestrict='en'
            found_books = api.list(search_type + ':' + search_value, maxResults=40, printType="books")
            return render(request, 'catalog/bookinstance_form.html',
                          {'form': form, 'found_books': found_books})
        else:
            form = BookInstanceForm(request.POST)
            return render(request, 'catalog/bookinstance_form.html', {'form': form})
    else:
        form = BookInstanceForm()
    return render(request, 'catalog/bookinstance_form.html', {'form': form})


class BookInstanceDelete(DeleteView):
    model = BookInstance
    template_name_suffix = '_delete_form'

    def get_success_url(self):
        return reverse('users_books_url')


class BookInstanceUpdate(UpdateView):
    model = BookInstance
    fields = ['status', 'due_back', 'book_holder', 'comment']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('users_books_url')


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


def create_book_from_api(request):
    if request.method == 'POST':
        api = googlebooks.Api()
        isbn = request.POST["isbn"]
        book = api.list('isbn:' + isbn)
        if book and book["totalItems"] > 0:
            title = book["items"][0]["volumeInfo"]["title"]
            author = book["items"][0]["volumeInfo"]["authors"][0]
            image_url = book["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
            book_exists = Book.objects.filter(title=title, author=author).first()
            if book_exists is None:
                new_book = models.Book(title=title, author=author, isbn_13=isbn, cover_url=image_url)
                new_book.save()
                transaction.commit()
                book_exists = new_book
            else:
                book_instance_exists = BookInstance.objects.filter(book=book_exists, book_owner=request.user).first()
                if book_instance_exists is not None:
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            new_instance = models.BookInstance(book=book_exists, book_owner=request.user)
            new_instance.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
