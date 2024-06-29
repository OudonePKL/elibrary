from django.db import models
from datetime import timedelta
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class CheckEmailQuerySet(models.QuerySet):
    """
    Class required to delete authentication number
    """

    def expired(self):
        return self.filter(expires_at__lt=timezone.now())

    def delete_expired(self):
        self.expired().delete()


class CheckEmail(models.Model):
    class Meta:
        verbose_name_plural = "2. Authentication code management"

    email = models.EmailField("Email for verification", max_length=100)
    code = models.CharField("Code for confirmation", max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    objects = CheckEmailQuerySet.as_manager()

    def __str__(self):
        return self.email

    def save(self, **kwargs):
        if not self.pk:  # Only set expires_at on initial save
            self.expires_at = timezone.now() + timedelta(minutes=3)
        super().save(**kwargs)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email=email, password=password)
        user.is_admin = True  # Indicates superuser status
        user.is_employee = True  # If all admins are employees
        user.save(using=self._db)
        return user


class UserModel(AbstractBaseUser):
    class Meta:
        verbose_name_plural = "1. User information"

    email = models.EmailField(verbose_name="Email Address", max_length=100, unique=True)
    profile_image = models.FileField(
        verbose_name="Profile image", null=True, blank=True, upload_to="profile"
    )
    is_employee = models.BooleanField(default=False, verbose_name="Employee")
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False, verbose_name="Administrator")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin  # Use is_admin to determine if user is staff
