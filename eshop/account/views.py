from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status

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