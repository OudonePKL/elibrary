from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserModel
from library.models import Member

class UserRegistrationForm(UserCreationForm):
    address = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = UserModel
        fields = ['email', 'password1', 'password2', 'address', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Member.objects.create(
                user=user,
                address=self.cleaned_data['address'],
                phone_number=self.cleaned_data['phone_number']
            )
        return user

class UserLoginForm(AuthenticationForm):
    class Meta:
        model = UserModel
        fields = ['email', 'password']