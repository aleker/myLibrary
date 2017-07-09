from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
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


class BookDetailView(generic.DetailView):
    model = Book

    def book_detail_view(request, pk):
        try:
            book_id = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise Http404("Book does not exist")
        return render(request, 'catalog/book_detail.html', context={'book': book_id, })
