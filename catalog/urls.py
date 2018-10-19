from django.urls import path
from catalog import views


urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(),
         name='author-detail'),
]
urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(),
         name='my-borrowed'),
]
urlpatterns += [
    path('allborrowed/', views.LoanedBooksByLibrarianListView.as_view(),
         name='all-borrowed'),
]
urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian,
         name='renew-book-librarian'),
]
urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author_create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(),
         name='author_update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(),
         name='author_delete'),
]
urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book_create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(),
         name='book_update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(),
         name='book_delete'),
]
urlpatterns += [
    path('book/<int:pk>/create/instance', views.BookInstanceCreate.as_view(),
         name='book_create_instance'),
    path('book/<uuid:pk>/update/instance', views.BookInstanceUpdate.as_view(),
         name='book_update_instance'),
    path('book/<uuid:pk>/delete/instance', views.BookInstanceDelete.as_view(),
         name='book_delete_instance'),
]
urlpatterns += [
    path('books/borrow', views.Borrow, name='book_borrow'),
    path('book/<uuid:pk>/borrow', views.reserve_book_library_member,
         name='book_reserve'),
    path('books/pending', views.reserved_list, name='book_reserved'),
    path('book/<uuid:pk>/collect', views.collect_book_library_member, name='book_collect'),
]
