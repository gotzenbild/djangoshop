# -*- coding: utf-8 -*-

from django import forms
from django.forms import DateField
from django.utils import timezone
from django.contrib.auth.models import User
from main.models import Sticers



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
        self.fields['username'].label = 'Логін'
        self.fields['username'].help_text = 'Обов\'язкове поле. Не боліше 150 символів. Тільки букви, цифри і символи @/./+/-/_.'
        self.fields['password'].label = 'Пароль'
        self.fields['password_check'].label = 'Повторіть пароль'
        self.fields['password_check'].help_text = 'Паролі мають збігатися'
        self.fields['first_name'].label = 'Ім\'я'
        self.fields['last_name'].label = 'Прізвище'
        self.fields['phone'].label = 'Контактний номер'
        self.fields['email'].label = 'E-MAIL'
        self.fields['email'].help_text = 'Будьласка, укажіть реальну електронну адресу та номер телефону'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        password_check = self.cleaned_data['password_check']


        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Користувач з таким логіном уже зареєстрирований')
        if len(username) < 5:
            raise forms.ValidationError('Логін не може містити менше 5-ти символів')
        if password != password_check:
            raise forms.ValidationError('Паролі не співпадають')
        if len(password) < 6:
            raise forms.ValidationError('Пароль не може містити менше 6-ти символів')

class EditEmail(forms.Form):

    email = forms.EmailField()

    def __init__ (self, *args, **kwargs ):
        super(EditEmail, self).__init__(*args,**kwargs)
        self.fields['email'].label = 'Email'
        self.fields['email'].help_text = 'Будьласка, укажіть реальну електронну адресу та номер телефону'

    def clean(self):
        cleaned_data = super(EditEmail, self).clean()
        email = cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Користувач з цією почтовою адресою вже зареєстрований')

class EditForm(forms.Form):

    first_name = forms.CharField()
    last_name = forms.CharField()
    phone = forms.CharField()
    def __init__ (self, *args, **kwargs ):
        super(EditForm, self).__init__(*args,**kwargs)
        self.fields['first_name'].label = 'Ім\'я'
        self.fields['last_name'].label = 'Прізвище'
        self.fields['phone'].label = 'Телефон'


class EditPassForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    password_check = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(EditPassForm, self).__init__(*args, **kwargs)

        self.fields['password'].label = 'Новий пароль'
        self.fields['password_check'].label = 'Повторіть пароль'
        self.fields['password_check'].help_text = 'Паролі мають співпадати'
    def clean(self):
        cleaned_data = super(EditPassForm, self).clean()
        password = cleaned_data['password']
        password_check =cleaned_data['password_check']
        if password != password_check:
            raise forms.ValidationError('Паролі не співпадають')
        if len(password) < 6:
            raise forms.ValidationError('Пароль не може містити меньше 6-ти символів')


class LoginForm(forms.Form):

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Логін'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('Користувача з цим логіном не знайдено')
        user = User.objects.get(username=username)
        if user and not user.check_password(password):
            raise forms.ValidationError('Невірний пароль')


CHOICES_PAYMENT = (('Повна', 'Повна'), ('Часткова', 'Часткова'),)
CHOICES_STICKER = ((j.slug, j) for j in Sticers.objects.all())



class OrderForm(forms.Form):
    name = forms.CharField()
    last_name = forms.CharField(required=False)
    phone = forms.CharField()
    address = forms.CharField()
    comments = forms.CharField(widget=forms.Textarea,required=False)
    datep = forms.CharField()
    payment = forms.ChoiceField(choices=CHOICES_PAYMENT)
    sticker = forms.ChoiceField(choices=CHOICES_STICKER)
    def __init__ (self, *args, **kwargs):
        super(OrderForm, self).__init__(*args,**kwargs)
        self.fields['name'].label = 'Ім\'я'
        self.fields['last_name'].label = 'Прізвище'
        self.fields['phone'].label = 'Контактний номер'
        self.fields['address'].label = 'Адрес доставки'
        self.fields['address'].help_text = 'Обов\'язково укажіть місто, назву та відділення почти'
        self.fields['comments'].label = 'Комемнтарі до заказу'
        self.fields['payment'].label = 'Спосіб оплати'
        self.fields['sticker'].label = 'Наліпка'
        self.fields['datep'].label = 'Дата доставки'







