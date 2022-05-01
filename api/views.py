import datetime
import json

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import *
from rest_framework.permissions import AllowAny
import requests
import os
from django.contrib.auth.models import User
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from api.models import Book,Borrower
from api.serializers import BookSerializer,BorrowerSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from api.mixins import APIMixins
from django.utils.decorators import method_decorator
from .decorators import is_token_valid

class CustomerRegistration(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    '''Customer Registration'''

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            if data:
                message = ""
                email = serializer.data.get('email')
                if serializer.data.get('name'):
                    name = serializer.data.get('name').capitalize()
                    first_name = serializer.data.get('name').capitalize()
                password = serializer.data.get('password')

                customer, customer_created = Customer.objects.get_or_create(email=email)
                user, created = User.objects.get_or_create(email=serializer.data.get('email'), username=name)
                customer.user = user
                customer.name = name
                customer.phone = serializer.data.get('phone')
                customer.joining_date = datetime.datetime.now()
                customer.last_updated_on = datetime.datetime.now()
                customer.save()
                print("customer saved")
                user.first_name = first_name
                user.set_password(password)
                user.save()
                # https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html
                refresh = RefreshToken.for_user(user)
                if customer_created:
                    message = "User created successfully"
                else:
                    message: "User Already Exists"
                print(refresh)
                print(type(refresh))
                payload = {
                    "status": True,
                    "message": message,
                    "data": serializer.data,
                    'refresh': str(refresh),
                    'access_token': str(refresh.access_token),
                }
            else:
                payload = {"status": False, "message": "Please Provide required credentials"}
        else:
            payload = {
                "status": False,
                "message": serializer.errors,
            }
        return Response(payload, status=status.HTTP_200_OK)


class CustomerLogin(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    '''Customer Login'''

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            if data:
                password = data.get("password")
                email = data.get("email")
                user = User.objects.filter(email=email, password=password)
                print(user)
                if user is not None:
                    user_obj, created = User.objects.get_or_create(email=email)
                    refresh = RefreshToken.for_user(user_obj)
                    payload = {
                        "status": True,
                        "message": "user exists and logged in successfully",
                        "email": email,
                        'refresh': str(refresh),
                        'access_token': str(refresh.access_token),
                        'user_id': user_obj.id
                    }
                else:
                    payload = {
                        "status": False,
                        "message": "Incorrect User Data"
                    }
            else:
                payload = {
                    "status": False,
                    "message": "No data found"
                }
        else:
            payload = {
                "status": False,
                "message": serializer.errors,
            }
        return Response(payload, status=status.HTTP_200_OK)


class CustomerLogout(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LogoutSerializer
    '''Customer Logout'''

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
            ot = OutstandingToken.objects.filter(token=request.data.get('refresh_token'))
            if ot:
                try:
                    user = ot.first().user
                    customer = Customer.objects.get(customer_user=user)

                except Exception as e:
                    customer = Customer.objects.get(email=serializer.data.get('email'))
                # https://axya.co/en/how-to-blacklist-json-web-tokens-in-django/
                refresh_token = request.data.get("refresh_token")
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as e:
                    pass
                payload = {
                    "status": True,
                    "message": "logged out successfully",
                }
            else:
                payload = {
                    "status": False,
                    "message": "Refresh token doesn't exist",
                }
        else:
            payload = {
                "status": False,
                "message": serializer.errors,
            }
        return Response(payload, status=status.HTTP_200_OK)


class GetBookDetails(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = GetBookSerializer
    '''To get all book details with pagination'''

    @method_decorator(is_token_valid, name='dispatch')
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            per_page_count = data.get("per_page_count")
            page = data.get("page_number")

            book = Book.objects.all()
            if book:
                serializer = BookSerializer(book, many=True)
                book_data = serializer.data
                paginator = Paginator(book_data, per_page_count)
                total_pages = paginator.num_pages
                try:
                    book_list = paginator.page(page)
                    book_obj = book_list.object_list
                except PageNotAnInteger:
                    book_list = paginator.page(1)
                    book_obj = book_list.object_list
                except EmptyPage:
                    book_list = paginator.page(paginator.num_pages)
                    book_obj = book_list.object_list
                except Exception as e:
                    print(e, 'case3')
                payload = {
                    "status": True,
                    "message": 'Data Fetched Successfully.',
                    "total_pages": total_pages,
                    "total_count": len(book_data),
                    "data": book_obj,
                    "page_num": book_list.number
                }
            else:
                payload = {
                    "status": False,
                    "message": 'No Books Found.'
                }
        else:
            payload = {
                "status": False,
                "message": serializer.errors
            }
        return Response(payload, status=status.HTTP_200_OK)

class FilterSearchSortBook(GenericAPIView,APIMixins):
    permission_classes = (AllowAny,)
    serializer_class = SearchFilterSortSerializer
    '''Filter,search,sort books'''

    @method_decorator(is_token_valid, name='dispatch')
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            page = data.get('page_number')
            per_page_count = data.get('per_page_count') if data.get('per_page_count') else 10
            book = Book.objects.all().order_by('-id')
            search = data.get('search')
            if search:
                book = book.filter(Q(title__icontains=search) | Q(
                    author__icontains=search) | Q(published_year__icontains=search)).order_by('-id')
            sort_key = data.get('sort_key') if data.get('sort_key') else "id"
            order = data.get('order') if data.get('order') else -1
            data = []
            if sort_key:
                print("sort key")
                data = self.sort_books(book, sort_key, order, per_page_count, page)
                total_pages = data.get('total_pages')
                count = data.get('count')
                data = data.get('book_data')
                payload = {
                    "status": True,
                    "data": data,
                    "total_pages": total_pages,
                    "count": count
                }
        else:
            payload = {
                "status": False,
                "message": serializer.errors,
            }
        return Response(payload, status=status.HTTP_200_OK)

class BorrowReturnData(GenericAPIView,APIMixins):
    permission_classes = (AllowAny,)
    serializer_class = BorrowReturnDataSerializer
    '''Filter,search books'''

    @method_decorator(is_token_valid, name='dispatch')
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            page = data.get('page_number')
            per_page_count = data.get('per_page_count') if data.get('per_page_count') else 10
            borrower = Borrower.objects.all().order_by('-id')
            issue_date = data.get('issue_date')
            return_date = data.get('return_date')
            search = data.get('search')
            if search:
                borrower = borrower.filter(Q(book__title__icontains=search) | Q(
                    book__author__icontains=search) | Q(book__published_year__icontains=search)).order_by('-id')
            if issue_date and return_date:
                borrower = borrower.filter(Q(issue_date__gte=issue_date) & Q(
                    return_date__lte=return_date)).order_by('-id')
            if borrower:
                borrowser_serializer = BorrowerSerializer(borrower, many=True)
                book_data = borrowser_serializer.data
                paginator = Paginator(book_data, per_page_count)
                total_pages = paginator.num_pages
                try:
                    book_list = paginator.page(page)
                    book_obj = book_list.object_list
                except PageNotAnInteger:
                    book_list = paginator.page(1)
                    book_obj = book_list.object_list
                except EmptyPage:
                    book_list = paginator.page(paginator.num_pages)
                    book_obj = book_list.object_list
                except Exception as e:
                    print(e, 'case3')

                payload = {
                    "status": True,
                    "data": book_obj,
                    "total_pages": total_pages,
                    "count": len(book_obj)
                }
            else:
                payload = {
                    "status": True,
                    "data": [],
                    "total_pages": 0,
                    "count": 0
                }

        else:
            payload = {
                "status": False,
                "message": serializer.errors,
            }
        return Response(payload, status=status.HTTP_200_OK)

