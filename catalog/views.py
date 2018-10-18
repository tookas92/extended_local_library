from django.shortcuts import render

# Create your views here.
from catalog.models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy

from catalog.forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Count, Q


def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    num_genres = Genre.objects.count()

    num_word = Book.objects.filter(title__contains='harry').count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_word': num_word,
        'num_visits': num_visits,

    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(
            borrower=self.request.user).filter(status__exact='o').order_by(
                                                'due_back')


class LoanedBooksByLibrarianListView(PermissionRequiredMixin,
                                     generic.ListView):
    """Generic class-based view listing books on loan to Librarian."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_users.html'
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.filter(
            status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request
        #  (binding):
        book_renewal_form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if book_renewal_form.is_valid():
            # process the data in form.cleaned_data as required
            # (here we just write it to the model due_back field)
            book_instance.due_back = book_renewal_form.cleaned_data[
                'renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today()
        + datetime.timedelta(weeks=3)
        book_renewal_form = RenewBookForm(
            initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': book_renewal_form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'


class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    model = BookInstance
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

    def get_initial(self):
        # You could even get the Book model using Book.objects.get here!
        return {
            'book': self.kwargs["pk"]
        }

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.book.pk})


class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    model = BookInstance
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.book.pk})


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.book.pk})


def Borrow(request):
    """View for books marked as Available"""
    available = Book.objects.annotate(
        count=Count('bookinstance', filter=Q(bookinstance__status__exact='a')))
    context = {
        'available': available
    }
    return render(request, 'catalog/borrow_list.html', context=context)
