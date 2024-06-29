from django.contrib import admin
from .models import Employee, Member, Category, Book, UploadBook, DownloadBook

admin.site.register(Employee)
admin.site.register(Member)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(UploadBook)
admin.site.register(DownloadBook)
