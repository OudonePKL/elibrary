# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from .models import Employee, Member, Category, Book, UploadBook, DownloadBook
from django.db import models

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import MemberRegistrationForm, EmployeeRegistrationForm, EmployeeForm, BookUploadForm, MemberForm, CategoryForm
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
import os

from django.urls import reverse

def home(request):
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
    else:
        books = Book.objects.all().prefetch_related('uploads')

    # Pagination
    paginator = Paginator(books, 10)  # Show 10 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'home.html', {'page_obj': page_obj})

def book_detail(request, book_id):
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
    else:
        books = Book.objects.all().prefetch_related('uploads')
    book = get_object_or_404(Book, pk=book_id)

    uploads = book.uploads.all()

    # Pagination
    paginator = Paginator(books, 10)  # Show 10 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'book_detail.html', {'book': book, 'uploads': uploads, 'page_obj': page_obj})

def register_member(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to a home page or any other page after registration
    else:
        form = MemberRegistrationForm()
    return render(request, 'registration/register_member.html', {'form': form})

def register_employee(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to a home page or any other page after registration
    else:
        form = EmployeeRegistrationForm()
    return render(request, 'registration/register_employee.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to a success page.
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'registration/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def download_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    upload = book.uploads.first()  # Adjust this query based on your logic

    if not upload or not upload.file:
        return HttpResponse("File not found.", status=404)

    # Log the download
    DownloadBook.objects.create(user=request.user, book=book)

    # Serve the file
    file_path = os.path.join(settings.MEDIA_ROOT, upload.file.name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{book.title}.pdf"'
            return response
    else:
        return HttpResponse("File not found.", status=404)
    

# ================ Dashboard ================
# Book management 
def book_list(request):
    books = Book.objects.all()
    return render(request, 'admin/book_list.html', {'books': books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    uploads = UploadBook.objects.filter(book=book)
    return render(request, 'admin/book_detail.html', {'book': book, 'uploads': uploads})

def book_create(request):
    if request.method == "POST":
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            book = Book(
                title=form.cleaned_data['title'],
                author=form.cleaned_data['author'],
                category=form.cleaned_data['category'],
                employee=form.cleaned_data['employee'],
                is_public=form.cleaned_data['is_public'],
                publication_date=form.cleaned_data['publication_date'],
            )
            book.save()
            upload = UploadBook(
                book=book,
                file=form.cleaned_data['file'],
                cover=form.cleaned_data['cover'],
            )
            upload.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookUploadForm()
    return render(request, 'admin/book_create.html', {'form': form})

def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    upload = get_object_or_404(UploadBook, book=book)
    if request.method == "POST":
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            book.title = form.cleaned_data['title']
            book.author = form.cleaned_data['author']
            book.category = form.cleaned_data['category']
            book.employee = form.cleaned_data['employee']
            book.is_public = form.cleaned_data['is_public']
            book.publication_date = form.cleaned_data['publication_date']
            book.save()
            upload.file = form.cleaned_data['file']
            upload.cover = form.cleaned_data['cover']
            upload.save()
            return redirect('book_detail', pk=book.pk)
    else:
        initial_data = {
            'title': book.title,
            'author': book.author,
            'category': book.category,
            'employee': book.employee,
            'is_public': book.is_public,
            'publication_date': book.publication_date,
            'file': upload.file,
            'cover': upload.cover,
        }
        form = BookUploadForm(initial=initial_data)
    return render(request, 'books/book_detail.html', {'form': form})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.delete()
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

# Employee management
@staff_member_required
def admin_dashboard(request):
    employee_count = Employee.objects.count()
    member_count = Member.objects.count()
    category_count = Category.objects.count()
    book_count = Book.objects.count()

    top_downloaded_books = (
        DownloadBook.objects.values('book__title')
        .annotate(download_count=models.Count('id'))
        .order_by('-download_count')[:10]
    )

    context = {
        'employee_count': employee_count,
        'member_count': member_count,
        'category_count': category_count,
        'book_count': book_count,
        'top_downloaded_books': top_downloaded_books,
    }
    
    return render(request, 'admin/dashboard.html', context)

@staff_member_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('employee_list')  # Redirect to a home page or any other page after registration
    else:
        form = EmployeeRegistrationForm()
    return render(request, 'admin/employee/employee_create.html', {'form': form})

@staff_member_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'admin/employee/employee_list.html', {'employees': employees})

@staff_member_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.user.delete()  # This will also delete the employee due to the OneToOne relationship
    return redirect(reverse('employee_list'))

@staff_member_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect(reverse('employee_list'))
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'admin/employee/employee_edit.html', {'form': form})


# Member management
@staff_member_required
def member_list(request):
    members = Member.objects.all()
    return render(request, 'admin/member/member_list.html', {'members': members})

@staff_member_required
def member_create(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('member_list')  # Redirect to a home page or any other page after registration
    else:
        form = MemberRegistrationForm()
    return render(request, 'admin/member/member_create.html', {'form': form})

@staff_member_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    member.user.delete()  # This will also delete the member due to the OneToOne relationship
    return redirect(reverse('member_list'))

@staff_member_required
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect(reverse('member_list'))
    else:
        form = MemberForm(instance=member)
    return render(request, 'admin/member/member_edit.html', {'form': form})


# Category management
@staff_member_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'admin/category/category_list.html', {'categories': categories})

@staff_member_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            return redirect('category_list')  # Redirect to a home page or any other page after registration
    else:
        form = CategoryForm()
    return render(request, 'admin/category/category_create.html', {'form': form})

@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()  # This will also delete the category due to the OneToOne relationship
    return redirect(reverse('category_list'))

@staff_member_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect(reverse('category_list'))
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin/category/category_edit.html', {'form': form})

# Book management
# @staff_member_required
# def book_list(request):
#     books = Book.objects.all()
#     return render(request, 'admin/book_list.html', {'books': books})

# def book_detail(request, pk):
#     book = get_object_or_404(Book, pk=pk)
#     return render(request, 'books/book_detail.html', {'book': book})

# @staff_member_required
# def book_delete(request, pk):
#     book = get_object_or_404(Book, pk=pk)
#     book.employee.delete()  # This will also delete the book due to the OneToOne relationship
#     return redirect(reverse('book_list'))

# @staff_member_required
# def book_edit(request, pk):
#     book = get_object_or_404(Book, pk=pk)
#     if request.method == 'POST':
#         form = BookForm(request.POST, instance=book)
#         if form.is_valid():
#             form.save()
#             return redirect(reverse('book_list'))
#     else:
#         form = BookForm(instance=book)
#     return render(request, 'admin/book_edit.html', {'form': form})
