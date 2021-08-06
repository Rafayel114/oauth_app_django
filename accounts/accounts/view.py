from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from oauth2_provider.views.generic import ProtectedResourceView
from oauth2_provider.models import Grant, AccessToken
from accounts.models import CustomUser, CustomApplication, UserGroup
from accounts.forms import SignUpForm, UserLoginForm, PhoneNumberForm, SmsConfirmForm
from django.urls import reverse
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib import messages
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from djangoredsmsapp.utils import createAndSendSmsWithIdType
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser
import requests
import random


def user_login(request):
    if request.user.is_authenticated:
        return redirect(reverse('home'))
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        print(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            if CustomUser.objects.filter(email=email).exists():
                user = auth.authenticate(username=email, password=password)
                if user is not None and user.is_active:
                    auth.login(request, user)
                    if form.cleaned_data.get('next') == "/":
                        return redirect(reverse('home'))
                    else:
                        return redirect(form.cleaned_data.get('next'))
                else:
                    messages.error(request, 'Неверный адрес электронной почты или пароль!')
            else:
                messages.error(request, 'Пользователя с таким E-mail не существует')
        else:
            messages.error(request, 'Заполните нужные поля!')
    form = UserLoginForm()
    next = request.GET.get('next', "/")
    return render(request, 'registration/login.html', {"form": form, "next": next})


def logout_view(request):
    logout(request)
    request.session.flush()
    request.user = AnonymousUser()
    return redirect('home')


@login_required(login_url='/login')
def home(request):
    user = CustomUser.objects.get(email=request.user.email)
    helpdesk = CustomApplication.objects.get(id=4)
    if request.user.is_superuser:
        auth_apps = CustomApplication.objects.all()
    else:
        default_apps = CustomApplication.objects.filter(hidden=False)
        trial_app_pks = user.userapp_set.all().values_list("application", flat=True)
        trial_apps = CustomApplication.objects.filter(pk__in=trial_app_pks)
        auth_apps = default_apps.union(trial_apps)
    return render(request, 'accounts/account.html', {"user": user, "auth_apps": auth_apps, "helpdesk": helpdesk})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        print(request.POST)
        print(type(request.POST.get('group')))
        if form.is_valid():
            username = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            form.save(commit=True)
            user = auth.authenticate(username=username, password=raw_password)
            auth.login(request, user)
            new_user = CustomUser.objects.get(email=username)
            if int(request.POST.get('group')) == 4:
                new_user.setUserGroup(new_user, group='Courier')
            else:
                new_user.setUserGroup(new_user, group='Client')
            return redirect(reverse('home'))
        else:
            messages.error(request, 'Заполните нужные поля для регистрации!')
    else:
        form = SignUpForm()
    next = request.GET.get('next', "/")
    return render(request, 'registration/login.html', {'form': form})



def api(request):
    print(request)
    print(request.GET.get('token'))
    token = request.GET.get('token')
    if not token:
        return HttpResponse('Empty token')
    atoken = AccessToken.objects.get(token = token)
    user = CustomUser.objects.get(email=atoken.user.email)
    # try:
    #     user_group = UserGroup.objects.get(user=user)
    #     group_name = user_group.group.name
    # except ObjectDoesNotExist:
    #     group_name = "Client"
    return JsonResponse({'success':True, 'data':{'user':{'username': atoken.user.email,
                                                        'id':atoken.user.id}}})


def send_sms(phone, text, userId):
    createAndSendSmsWithIdType(phone, text, str(userId), 'passCodeRestore')

def sms_login(request):
    if request.method == "POST":
        form = PhoneNumberForm(request.POST)
        print(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get("phone_number")
            if CustomUser.objects.filter(phone_number=phone_number).exists():
                user = CustomUser.objects.get(phone_number=phone_number)
                create_sms_code(user.phone_number.as_e164)
                return redirect('confirm_sms', phone_number=user.phone_number.as_e164)
            else:
                messages.error(request, 'Пользователь с таким тел. номером не зарегестрирован!')
        else:
            messages.error(request, 'Введите действующий номер телефона(Формат: +79999999999)')
    else:
        form = PhoneNumberForm()
    # next = request.GET.get('next', "/")
    return render(request, "registration/login_mobile.html", {"form": form})


def create_sms_code(phone_number):
    user = CustomUser.objects.get(phone_number=phone_number)
    new_code = random.randint(1000, 10000)
    user.sms_code = new_code
    user.save()
    print("------", new_code, "------")
    send_sms(phone_number, new_code, user.id)


def confirm_sms(request, phone_number):
    user = CustomUser.objects.get(phone_number=phone_number)
    if request.method == "POST":
        form = SmsConfirmForm(request.POST)
        if form.is_valid():
            new_code = form.cleaned_data.get("new_code")
            if new_code == user.sms_code:
                auth.login(request, user)
                return redirect(reverse('home'))
        else:
            messages.error(request, "Введите код из СМС")
    else:
        form = SmsConfirmForm()
    if "re_sms" in request.GET:
        create_sms_code(phone_number)
    return render(request, "registration/confirm_sms.html", {"form": form, "phone_number": phone_number})
