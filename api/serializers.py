from rest_framework import serializers
from api.models import Customer,Book,Borrower

class RegistrationSerializer(serializers.Serializer):
    password = serializers.CharField(label='password')
    email = serializers.CharField()
    phone = serializers.CharField()
    name = serializers.CharField()



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(label='password')


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    email = serializers.CharField()

class GetBookSerializer(serializers.Serializer):
    per_page_count = serializers.IntegerField()
    page_number = serializers.IntegerField()

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

class SearchFilterSortSerializer(serializers.Serializer):
    search = serializers.CharField(allow_blank=True)
    per_page_count = serializers.IntegerField()
    page_number = serializers.IntegerField()
    sort_key = serializers.CharField(default='id',allow_blank=True,allow_null=True)
    order = serializers.IntegerField(default=-1,allow_null=True)


    def validate_order(self, value):
        order = str(value)
        if order == '-1' or order == '1' or " ":
            pass
        else:
            raise serializers.ValidationError("Order can be only -1 or 1")
        return value

    def validate_sort_key(self, value):
        list = ['title', 'author','published_year','']
        if value not in list:
            raise serializers.ValidationError("Invalid Sort Key")
        return value

class BorrowReturnDataSerializer(serializers.Serializer):
    issue_date = serializers.DateTimeField()
    return_date = serializers.DateTimeField()
    per_page_count = serializers.IntegerField()
    page_number = serializers.IntegerField()
    search = serializers.CharField(allow_blank=True)

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields =["name","email"]

class BorrowerSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False)
    customer = CustomerSerializer(many=False)
    class Meta:
        model = Borrower
        fields = "__all__"