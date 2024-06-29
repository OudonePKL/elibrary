# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import UserModel
from .models import Book, UploadBook, Member

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'employee', 'is_public']

class UploadBookForm(forms.ModelForm):
    class Meta:
        model = UploadBook
        fields = ['file', 'cover']

class CombinedBookUploadForm(forms.Form):
    book_form = BookForm()
    upload_book_form = UploadBookForm()


# class CombinedBookUploadForm(forms.ModelForm):
#     class Meta:
#         model = Book  # Use Book model since we're combining BookForm and UploadBookForm
#         fields = ['title', 'author', 'category', 'employee', 'is_public', 'file', 'cover']



class UserRegistrationForm(UserCreationForm):
    address = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = UserModel
        fields = ['email', 'profile_image', 'password1', 'password2', 'address', 'phone_number']

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

