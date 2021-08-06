from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm, Form
from django import forms
from accounts.models import CustomUser
from accounts import settings
from phonenumber_field.formfields import PhoneNumberField
from django.core.validators import EmailValidator


class UserLoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField()
    next = forms.CharField()

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        # if email and password:
        #     user = authenticate(email=email, password=password)
        #     if not user:
        #         raise forms.ValidationError("User does not exist.")
        #     if not user.is_active:
        #         raise forms.ValidationError("User is no longer active.")
        return super(UserLoginForm, self).clean(*args, **kwargs)



class SignUpForm(UserCreationForm):
    phone_number = PhoneNumberField(error_messages={
        'required': 'Поле "Номер телефона" обязательно для заполнения',
        'invalid': 'Введите действующий номер телефона(Формат: +79999999999)',
        'unique': 'Пользователь с таким номером уже зарегестрирован'})
    email = forms.EmailField(error_messages = {
        'required': 'Поле "E-mail" обязательно для заполнения',
        'invalid': 'Неверный E-mail адрес',
        'unique': 'Пользователь с таким E-mail уже зарегестрирован'})
    error_messages = {'password_mismatch': 'Пароли не совпадают'}
    class Meta:
        model = CustomUser
        fields = ("phone_number", 'password1', 'password2', 'email')

    def __init__(self, *args, **kwargs):
        self.field_order = ['phone_number', 'email']
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].widget.attrs.update({
            'class': 'forms_field-input',
            'required': 'required',
            'placeholder': 'Введите номер телефона'
            })
        self.fields['email'].widget.attrs.update({
            'class': 'forms_field-input',
            'required': 'required',
            'placeholder': 'Введите E-mail'
            })


class PhoneNumberForm(forms.Form):
    phone_number = PhoneNumberField(error_messages={
        'required': 'Поле "Номер телефона" обязательно для заполнения',
        'invalid': 'Введите действующий номер телефона(Формат: +79999999999)',
        })

    def __init__(self, *args, **kwargs):
        self.field_order = ['phone_number']
        super(PhoneNumberForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].widget.attrs.update({
            'class': 'forms_field-input',
            'required': 'required',
            'placeholder': 'Введите номер телефона',
            'id': 'phone_number'
            })


class SmsConfirmForm(forms.Form):
    new_code = forms.IntegerField(min_value=1000, max_value=10000,
        error_messages={
            "min_value": "Код из смс должен быть 4х значным числом",
            "max_value": "Код из смс должен быть 4х значным числом",
            "required": "Введите код из смс",
            "invalid": "Неверный код!"
            })

    def __init__(self, *args, **kwargs):
        self.field_order = ['new_code']
        super(SmsConfirmForm, self).__init__(*args, **kwargs)
        self.fields['new_code'].widget.attrs.update({
            'class': 'forms_field-input',
            'required': 'required',
            'placeholder': 'Введите код из СМС'
            })
