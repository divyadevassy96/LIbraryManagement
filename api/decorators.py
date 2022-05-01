import json

from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken


def is_token_valid(function):
    def wrap(request, self=None, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization')
            token = AccessToken(access_token)
            user_obj = User.objects.filter(id=token.payload.get('user_id'))
            if user_obj:
                user = user_obj.first().id
                token_user = token.payload.get('user_id')
                if user == token_user:
                    return function(request, *args, **kwargs)
                else:
                    raise AuthenticationFailed
            raise AuthenticationFailed
        except Exception as e:
            print(e,'case1')
            if str(e) == 'Token is invalid or expired' or str(e) == 'Incorrect authentication credentials.' or str(e)=='Token has wrong type':
                raise AuthenticationFailed
            else:
                print(e,'case2')
                raise e

    return wrap



