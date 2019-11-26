from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

import datamodel

from django.contrib.auth.models import User

from datamodel.models import Move


class UserForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        data = super(UserForm, self).clean()
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError("Username/password is not valid")

        return self.cleaned_data

    class Meta:
        model = User
        fields = ('username', 'password')


class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        data = super(SignupForm, self).clean()
        pwd = data.get("password")

        validate_password(pwd)
        repeat_pwd = data.get("password2")

        if pwd != repeat_pwd:
            raise forms.ValidationError(
                "Password and Repeat password are not the same")

        return self.cleaned_data

    class Meta:
        model = User
        fields = ('username', 'password')


class MoveForm(forms.ModelForm):

    class Meta:
        model = Move
        fields = ('origin', 'target')
