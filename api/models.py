from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, TextField, Model
from django.contrib.auth.models import User
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    joining_date = models.DateTimeField(null=True, blank=True)
    last_updated_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name + "----" + str(self.email)

class Genre(models.Model):
    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)")

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=200,
                            help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        return self.name
def current_year():
    return datetime.date.today().year


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


class Book(models.Model):
    title = models.CharField(max_length=200)
    desc = TextField()
    author = models.CharField(max_length=100)
    publisher_name = CharField(max_length=256)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13 Character ISBN number')
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
    total_copies = models.IntegerField()
    available_copies = models.IntegerField()
    published_year =  models.PositiveIntegerField(
        default=current_year(), validators=[MinValueValidator(1984), max_value_current_year])


class Borrower(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    issue_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.customer.name + " borrowed " + self.book.title

# @receiver(post_save, sender=Borrower)
# def send_book_issue_request_notification_email(sender, instance, created, **kwargs):
#     book = Book.objects.get(pk=instance.book.pk)
#     customer = Customer.objects.get(id=instance.customer.id)
#     issue_date = instance.issue_date
#     return_date = instance.return_date
#     email = customer.email
#     if created:
#         subject = f'Book : Issue Request: {book} has been requested. '
#         message = f'Book : {book} has been requested to issue by {customer.name} on {issue_date}. \n Thanks!'
#
#         send_mail(
#             subject,
#             message,
#             email,
#             ['divya@gmail.com'],
#             fail_silently=False
#         )
#     else:
#         subject = f'Book : Return Request:{book} has been returned. '
#         message = f'Book : {book} has been returned to library by {customer.name} on {return_date}. \n Thanks!'
#
#         send_mail(
#             subject,
#             message,
#             email,
#             [email],
#             fail_silently=False
#         )
