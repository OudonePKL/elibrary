from django.contrib import admin
from .models import Employee, Member, Category, Book, UploadBook, DownloadBook

admin.site.register(Employee)
# admin.site.register(Member)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(UploadBook)
admin.site.register(DownloadBook)

class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved', 'address', 'phone')
    list_filter = ('is_approved',)
    search_fields = ('user__email', 'address', 'phone')
    actions = ['approve_members']

    def approve_members(self, request, queryset):
        queryset.update(is_approved=True)
    approve_members.short_description = "Approve selected members"

admin.site.register(Member, MemberAdmin)
