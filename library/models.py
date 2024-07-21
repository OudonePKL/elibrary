from django.db import models
from django.core.validators import RegexValidator
from users.models import UserModel

class Employee(models.Model):
    POSITION_CHOICES = [
        ("GENERAL", "General"),
        ("DIRECTOR", "Director"),
    ]
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, choices=POSITION_CHOICES, default="GENERAL")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )

    def __str__(self):
        return self.user.email

class Member(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    membership_date = models.DateField(auto_now_add=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        null=True, blank=True
    )
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='books')
    is_public = models.BooleanField(default=True)
    publication_date = models.DateField(null=True, blank=True)
    ispn = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class UploadBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='uploads')
    file = models.FileField(upload_to='books/')
    cover = models.ImageField(upload_to='covers/', null=True, blank=True)
    upload_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.book.title

class DownloadBook(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    download_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.book.title} downloaded by {self.user.email}'
