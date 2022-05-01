from api.views import *
from django.urls import path

urlpatterns = [
    path("registration/", CustomerRegistration.as_view()),
    path("login/", CustomerLogin.as_view()),
    path("logout/", CustomerLogout.as_view()),
    path("get_book_details/", GetBookDetails.as_view()),
    path("filter_search_sort_book/", FilterSearchSortBook.as_view()),
    path("book_borrow_return_data/", BorrowReturnData.as_view())
]