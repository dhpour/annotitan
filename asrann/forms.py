from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=2000, label="آدرس ایمیل")
    password = forms.CharField(max_length=65, widget=forms.PasswordInput, label="کلمه عبور")

class RegisterForm(UserCreationForm):
    password1 = forms.CharField(max_length=65, widget=forms.PasswordInput, label="کلمه عبور")
    password2 = forms.CharField(max_length=65, widget=forms.PasswordInput, label="تکرار کلمه")
    email = forms.EmailField(max_length=200, help_text='Required', label='آدرس ایمیل')  
    class Meta:
        model=User
        #username = forms.CharField(max_length=65, label="نام کاربری")
        #email = forms.CharField(max_length=65, widget=forms.EmailInput, label='پست الکترونیک')
        
        fields = ['email']
        labels = {
            #'username': _('نام کاربری'),
            #'email': _('پست الکترونیک'),
            #'password1': _('رمز عبور'),
            #'password2': _('تکرار رمز')
        }
        
#from https://www.pythontutorial.net/django-tutorial/django-login/
#from https://www.pythontutorial.net/django-tutorial/django-registration/