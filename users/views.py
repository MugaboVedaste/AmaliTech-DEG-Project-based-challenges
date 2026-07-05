from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['POST'])
def register(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"}, status=201)

    return Response(serializer.errors, status=400)


@api_view(['POST'])
def login(request):

    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(username=email, password=password)

    if user is None:
        return Response({"error": "Invalid credentials"}, status=401)

    refresh = RefreshToken.for_user(user)

    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    })


def web_login(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')

        error = 'Invalid email or password.'

    return render(request, 'users/login.html', {'error': error})


def web_logout(request):

    auth_logout(request)
    return redirect('login')