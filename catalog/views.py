from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView

from .models import Book, Author, BookInstance
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
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors},
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
    return render(request, 'catalog/book_detail.html', context={'book': book_id, })


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


# class AuthorDetailView(generic.DetailView):
#     model = Author


def author_detail_view(request, pk):
    try:
        author_id = Author.objects.get(pk=pk)
        authors_books = get_books_by_author(pk)
    except Author.DoesNotExist:
        raise Http404("Author does not exists")
    return render(request, 'catalog/author_detail.html',
                  context={'author': author_id, 'book_list': authors_books})


def get_books_by_author(author):
    return Book.objects.filter(author=author)


class UsersBookListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/users_book_list.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(book_owner=self.request.user).order_by('due_back')


class BookInstanceCreate(CreateView):
    model = BookInstance
    fields = ('book', 'status', 'due_back', 'book_owner', 'book_holder')
    # TODO przypisać initial!
    # initial = {'book_owner': CreateView}
    success_url = reverse_lazy('users_books_url')


class BookInstanceDelete(DeleteView):
    model = BookInstance
    success_url = reverse_lazy('users_books_url')


