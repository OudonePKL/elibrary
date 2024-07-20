# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import UserModel
from .models import Book, UploadBook, Member, Employee, Category
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


# User manaement
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'position', 'date_of_birth', 'phone']

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['address', 'phone']
        
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

# class MemberRegistrationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     address = forms.CharField(required=False)
#     phone = forms.CharField(required=False)

#     class Meta:
#         model = UserModel
#         fields = ('email', 'password1', 'password2')

#     def save(self, commit=True):
#         user = super(MemberRegistrationForm, self).save(commit=False)
#         user.email = self.cleaned_data['email']
#         if commit:
#             user.save()
#             Member.objects.create(user=user, address=self.cleaned_data['address'], phone=self.cleaned_data['phone'])
#         return user

class AdminMemberCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    address = forms.CharField(required=False)
    phone = forms.CharField(required=False)

    class Meta:
        model = UserModel
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(AdminMemberCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = True  # Automatically activate user
        if commit:
            user.save()
            Member.objects.create(
                user=user,
                address=self.cleaned_data['address'],
                phone=self.cleaned_data['phone'],
                is_approved=True  # Automatically approve member
            )
        return user

class MemberRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    address = forms.CharField(required=False)
    phone = forms.CharField(required=False)

    class Meta:
        model = UserModel
        fields = ('email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserModel.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        user = super(MemberRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Member.objects.create(user=user, address=self.cleaned_data['address'], phone=self.cleaned_data['phone'])
        return user
    
class MemberEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    address = forms.CharField(required=True)
    phone = forms.CharField(required=True)

    class Meta:
        model = UserModel
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance and hasattr(instance, 'member'):
            initial = {
                'email': instance.email,
                'address': instance.member.address,
                'phone': instance.member.phone,
            }
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super(MemberEditForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            if hasattr(user, 'member'):
                member = user.member
                member.address = self.cleaned_data['address']
                member.phone = self.cleaned_data['phone']
                member.save()
            else:
                Employee.objects.create(
                    user=user,
                    address=self.cleaned_data['address'],
                    phone=self.cleaned_data['phone'],
                )
        return user

class EmployeeRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    phone = forms.CharField(required=True)
    position = forms.ChoiceField(choices=Employee.POSITION_CHOICES, required=True)

    class Meta:
        model = UserModel
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = {
                'email': instance.user.email,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'date_of_birth': instance.date_of_birth,
                'phone': instance.phone,
                'position': instance.position,
            }
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super(EmployeeRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            if hasattr(user, 'employee'):
                employee = user.employee
                employee.first_name = self.cleaned_data['first_name']
                employee.last_name = self.cleaned_data['last_name']
                employee.date_of_birth = self.cleaned_data['date_of_birth']
                employee.phone = self.cleaned_data['phone']
                employee.position = self.cleaned_data['position']
                employee.save()
            else:
                Employee.objects.create(
                    user=user,
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name'],
                    date_of_birth=self.cleaned_data['date_of_birth'],
                    phone=self.cleaned_data['phone'],
                    position=self.cleaned_data['position']
                )
        return user


class EmployeeEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    phone = forms.CharField(required=True)
    position = forms.ChoiceField(choices=Employee.POSITION_CHOICES, required=True)

    class Meta:
        model = UserModel
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance and hasattr(instance, 'employee'):
            initial = {
                'email': instance.email,
                'first_name': instance.employee.first_name,
                'last_name': instance.employee.last_name,
                'date_of_birth': instance.employee.date_of_birth,
                'phone': instance.employee.phone,
                'position': instance.employee.position,
            }
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super(EmployeeEditForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            if hasattr(user, 'employee'):
                employee = user.employee
                employee.first_name = self.cleaned_data['first_name']
                employee.last_name = self.cleaned_data['last_name']
                employee.date_of_birth = self.cleaned_data['date_of_birth']
                employee.phone = self.cleaned_data['phone']
                employee.position = self.cleaned_data['position']
                employee.save()
            else:
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


# Book management
class BookForm(forms.ModelForm):
    file = forms.FileField(required=True)
    cover = forms.ImageField(required=True)

    class Meta:
        model = Book
        fields = ['title', 'author', 'ispn', 'category', 'employee', 'is_public', 'publication_date']

class UploadBookForm(forms.ModelForm):
    class Meta:
        model = UploadBook
        fields = ['file', 'cover']

UploadBookFormSet = inlineformset_factory(Book, UploadBook, form=UploadBookForm, extra=1)
