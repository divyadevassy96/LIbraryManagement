
from api.serializers import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from api.views import CreateNotification
from django.db.models import Q


# from AMZSteels.celery import app

class APIMixins:

    def __init__(self):
        pass

    def sort_books(self, book, sort_key, order, per_page_count, page):
        sort_string = "-" + sort_key if str(order) == '-1' else sort_key
        books = book.order_by(sort_string)
        paginator = Paginator(books, per_page_count)
        total_pages = paginator.num_pages
        count = len(books)
        try:
            book_list = paginator.page(page)
            books = book_list.object_list
        except PageNotAnInteger:
            book_list = paginator.page(1)
            books = book_list.object_list
        except EmptyPage:
            book_list = paginator.page(paginator.num_pages)
            books = book_list.object_list
        book_serializer = BookSerializer(books, many=True)
        book_data = book_serializer.data
        data = {"book_data": book_data, "total_pages": total_pages, 'count': count}
        return data