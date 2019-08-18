# -*- coding: utf-8 -*-

from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from main.models import Category



class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_check = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField()

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'password_check',
            'first_name',
            'last_name',
            'phone',
            'email'
        ]

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
        self.fields['password_check'].label = 'Повторите пароль'
        self.fields['password_check'].help_text = 'Пароли должны совпадать'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['phone'].label = 'Контактный номер'
        self.fields['email'].label = 'E-MAIL'
        self.fields['email'].help_text = 'Пожалуйста, указывайте реальный електронный адрес, и номер телефона'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        password_check = self.cleaned_data['password_check']
        email = self.cleaned_data['email']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с данным логином уже зарегестрирован')
        if len(username) < 5:
            raise forms.ValidationError('Логин не может содержать меньше 5-ти символов')
        if password != password_check:
            raise forms.ValidationError('Пароли не совпадают')
        if len(password) < 6:
            raise forms.ValidationError('Пароль не может содержать меньше 6-ти символов')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с данным почтовым адресом уже зарегестрирован')

class EditEmail(forms.Form):

    email = forms.EmailField()

    def __init__ (self, *args, **kwargs ):
        super(EditEmail, self).__init__(*args,**kwargs)
        self.fields['email'].label = 'Email'
        self.fields['email'].help_text = 'Пожалуйста, указывайте реальный електронный адрес, и номер телефона'

    def clean(self):
        cleaned_data = super(EditEmail, self).clean()
        email = cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с данным почтовым адресом уже зарегестрирован')

class EditForm(forms.Form):

    first_name = forms.CharField()
    last_name = forms.CharField()
    phone = forms.CharField()
    def __init__ (self, *args, **kwargs ):
        super(EditForm, self).__init__(*args,**kwargs)
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['phone'].label = 'Телефон'


class EditPassForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    password_check = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(EditPassForm, self).__init__(*args, **kwargs)

        self.fields['password'].label = 'Новый пароль'
        self.fields['password_check'].label = 'Повторите пароль'
        self.fields['password_check'].help_text = 'Пароли должны совпадать'
    def clean(self):
        cleaned_data = super(EditPassForm, self).clean()
        password = cleaned_data['password']
        password_check =cleaned_data['password_check']
        if password != password_check:
            raise forms.ValidationError('Пароли не совпадают')
        if len(password) < 6:
            raise forms.ValidationError('Пароль не может содержать меньше 6-ти символов')


class LoginForm(forms.Form):

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с данным логином не зарегистрирован')
        user = User.objects.get(username=username)
        if user and not user.check_password(password):
            raise forms.ValidationError('Неверный пароль')

class OrderForm(forms.Form):

    name = forms.CharField()
    last_name = forms.CharField(required=False)
    phone = forms.CharField()
    address = forms.CharField(required=False)
    comments = forms.CharField(widget=forms.Textarea,required=False)
    def __init__ (self, *args, **kwargs):
        super(OrderForm, self).__init__(*args,**kwargs)
        self.fields['name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['phone'].label = 'Контактный телефон'
        self.fields['address'].label = 'Адрес доставки'
        self.fields['address'].help_text = 'Обезательно указывайте город, название и отделение почты'
        self.fields['comments'].label = 'Комемнтарии к заказу'





