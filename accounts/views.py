from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from .models import *
import uuid


def login(request):
    if User.is_authenticated:
        dj_logout(request)
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST['user'],
                            password=request.POST['password'])
        if user:
            dj_login(request, user)
            return HttpResponseRedirect(reverse('articles:create'))
        else:
            context = {
                'error': 'Authentication failed. You may need to activate your user'}
            return render(request, 'accounts/login.html', context)

    return render(request, 'accounts/login.html')


@login_required
def logout(request):
    dj_logout(request)
    return HttpResponseRedirect(reverse('accounts:login'))


def signup(request):
    if User.is_authenticated:
        dj_logout(request)

    context = {}
    if request.method == 'POST':
        if request.POST['password'] == request.POST['confirm_password']:
            username = request.POST['user']

            if not User.objects.filter(username=username):
                email = request.POST['email']
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=request.POST['firstname'],
                    last_name=request.POST['lastname'],
                    password=request.POST['password'],
                    is_active=False)
                activation_key = str(uuid.uuid4())
                userActivation = UserActivation()
                userActivation.user = user
                userActivation.activation_key = activation_key
                userActivation.save()

                # send email with uuid for activation
                # send_mail(
                #     'Activation of your user for ToDo',
                #     'Click this link to activate your user <a href="localhost:8000/activation?username={{username}}&activation_key={{activation_key}}',
                #     'allowishus.nexus@gmail.com',
                #     ['{{email}}'],
                #     fail_silently=False,
                # )

                return HttpResponseRedirect(reverse('accounts:login'))
            else:
                context['error'] = 'User already exist'
        else:
            context['error'] = 'Password and confirmation did not match'

    return render(request, 'accounts/signup.html', context)


def activate(request):
    # localhost:8000/user/activate?username=jens&activation_key=5373405d-17de-443e-8346-dddea0d14c51
    context = {}
    if request.method == 'GET':
        username = request.GET['username']

        if User.objects.filter(username=username):
            user = User.objects.get(username=username)
            if user.is_active == False and UserActivation.objects.filter(user=user):

                userActivation = UserActivation.objects.get(user=user)
                if userActivation.activation_key == request.GET['activation_key']:
                    user.is_active = True
                    user.save()

                    userActivation.delete()
                else:
                    # activation key didn't match
                    context['error'] = 'User activation failed'
            else:
                context['error'] = 'User has already been activated'
        else:
            context['error'] = 'User activation failed'  # no such user

    return render(request, 'accounts/login.html', context)


def forgot_password(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['user']

        if User.objects.filter(username=username):
            user = User.objects.get(username=username)
            if user.is_active:
                # store uuid/user in UserActivation
                activation_key = str(uuid.uuid4())
                userActivation = UserActivation()
                userActivation.user = user
                userActivation.activation_key = activation_key
                userActivation.save()

                # send email with uuid for reset
                # send_mail(
                #     'Activation of your user for ToDo',
                #     'Click this link to reset your password <a href="localhost:8000/password_reset?username={{username}}&reset_key={{activation_key}}',
                #     'allowishus.nexus@gmail.com',
                #     ['{{email}}'],
                #     fail_silently=False,
                # )
            else:
                context['error'] = 'You need to activate your user'
        else:
            context['error'] = 'Password reset failed'

    return render(request, 'accounts/forgot_password.html', context)


def password_reset(request):
    # localhost:8000/user/password_reset?username=jens&reset_key=0a68dfcf-2c5e-487e-8df3-f052d4c326fc
    context = {}
    if request.method == 'GET':
        username = request.GET['username']

        if User.objects.filter(username=username):
            user = User.objects.get(username=username)
            userActivation = UserActivation.objects.get(user=user)
            if userActivation.activation_key == request.GET['reset_key']:
                userActivation.delete()
                dj_login(request, user)
        else:
            # activation key didn't match
            context['error'] = 'User activation failed'

    return render(request, 'accounts/password_reset.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        if new_password == request.POST['confirm_password']:
            user = request.user
            user.set_password(new_password)
            user.save()

            dj_login(request, user)
            return HttpResponseRedirect(reverse('articles:create'))
        else:
            context = {'error': 'Password and confirmation did not match'}
            return render(request, 'accounts/change_password.html', context)

    return render(request, 'accounts/change_password.html')
