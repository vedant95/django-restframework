from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status

from django.core.mail import send_mail

from django.utils.crypto import get_random_string

from rest_framework.permissions import IsAuthenticated

from .serializers import SingUpSerializer, UserSerializer
# Create your views here.

@api_view(['POST'])
def register(request):
    data = request.data

    user = SingUpSerializer(data=data)

    if user.is_valid():
        if not User.objects.filter(username=data['email']).exists():

            user = User.objects.create(
                first_name = data['first_name'],
                last_name = data['last_name'],
                email = data['email'],
                username = data['email'],
                password = make_password(data['password']),
            )

            return Response({'details': 'User registered'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(user.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):

    user = UserSerializer(request.user, many=False)

    return Response(user.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request):

    user = request.user
    data = request.data

    user.first_name = data['first_name'] if 'first_name' in data else user.first_name
    user.last_name = data['last_name'] if 'last_name' in data else user.last_name
    user.username = data['username'] if 'username' in data else user.username
    user.email = data['email'] if 'email' in data else user.email
    user.password = make_password(data['password']) if 'password' in data else user.password

    user.save()

    serialiser = UserSerializer(user, many=False)

    return Response(serialiser.data)


def get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/".format(protocol=protocol,host=host)

@api_view(['POST'])
def forgot_password(request):
    data = request.data

    user = get_object_or_404(User, email=data['email'])

    token = get_random_string(40)
    expire_date = datetime.now() + timedelta(minutes=30)

    user.profile.reset_password_token = token
    user.profile.reset_password_expire = expire_date

    user.profile.save()

    host = get_current_host(request)

    link = "{host}api/reset_password/{token}".format(host=host, token=token)
    body = "Your password reset link is: {link}".format(link=link)

    send_mail(
        "Password reset for eShop",
        body,
        "noreply@eshop.com",
        [data['email']]
    )

    return Response({'Details': 'Password reset mail sent to: {email}'.format(email=data['email'])})


@api_view(['POST'])
def reset_password(request, token):
    data = request.data

    user = get_object_or_404(User, profile__reset_password_token=token)

    if user.profile.reset_password_expire.replace(tzinfo=None) < datetime.now():
        return Response({'error': 'Token is expired'}, status=status.HTTP_400_BAD_REQUEST)

    if data['password'] != data['confirmPassword']:
        return Response({'error': 'Passworda are not same'}, status=status.HTTP_400_BAD_REQUEST)

    user.password = make_password(data['password'])
    user.profile.reset_password_token = ""
    user.profile.reset_password_expire = None

    user.profile.save()
    user.save()

    return Response({'Details': 'Password reset successful'})