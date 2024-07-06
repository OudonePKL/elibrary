# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import UserModel
from .models import Book, UploadBook, Member, Employee, Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'position', 'date_of_birth', 'phone']

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['address', 'phone']
        
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'employee', 'is_public', 'publication_date']

class UploadBookForm(forms.ModelForm):
    class Meta:
        model = UploadBook
        fields = ['file', 'cover']

class BookUploadForm(forms.Form):
    title = forms.CharField(max_length=200)
    author = forms.CharField(max_length=200)
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())
    is_public = forms.BooleanField(required=False)
    publication_date = forms.DateField(required=False)
    file = forms.FileField()
    cover = forms.ImageField(required=False)


class UserRegistrationForm2(UserCreationForm):
    address = forms.CharField(max_length=255, required=False)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = UserModel
        fields = ['email', 'profile_image', 'password1', 'password2', 'address', 'phone']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Member.objects.create(
                user=user,
                address=self.cleaned_data['address'],
                phone=self.cleaned_data['phone']
            )
        return user

class MemberRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    address = forms.CharField(required=False)
    phone = forms.CharField(required=False)

    class Meta:
        model = UserModel
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(MemberRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Member.objects.create(user=user, address=self.cleaned_data['address'], phone=self.cleaned_data['phone'])
        return user
    

class EmployeeRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    phone = forms.CharField(required=True)
    position = forms.ChoiceField(choices=Employee.POSITION_CHOICES, required=True)

    class Meta:
        model = UserModel
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(EmployeeRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_employee = True
        if commit:
            user.save()
            Employee.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                phone=self.cleaned_data['phone'],
                position=self.cleaned_data['position']
            )
        return user
    
class UserLoginForm(AuthenticationForm):
    class Meta:
        model = UserModel
        fields = ['email', 'password']

