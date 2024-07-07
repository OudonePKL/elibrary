# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from .models import Employee, Member, Category, Book, UploadBook, DownloadBook
from django.db import models
from django.forms import modelformset_factory

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import MemberRegistrationForm, EmployeeRegistrationForm, EmployeeForm, BookForm, UploadBookFormSet, MemberForm, CategoryForm
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

# def book_create(request):
#     if request.method == 'POST':
#         form = BookForm(request.POST, request.FILES)
#         if form.is_valid():
#             book = form.save()
#             messages.success(request, 'Book created successfully!')
#             return redirect('book_create')
#         else:
#             messages.error(request, 'Error creating book. Please check the form.')
#     else:
#         form = BookForm()

#     return render(request, 'admin/book/book_create.html', {'form': form})

def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            file = form.cleaned_data['file']
            cover = form.cleaned_data['cover']
            if file or cover:
                UploadBook.objects.create(book=book, file=file, cover=cover)
            messages.success(request, 'Book created successfully!')
            return redirect('book_create')
        else:
            messages.error(request, 'Error creating book. Please check the form.')
    else:
        form = BookForm()

    return render(request, 'admin/book/book_create.html', {'form': form})



def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    try:
        upload = book.uploads.get()
    except UploadBook.DoesNotExist:
        upload = None
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()
            file = form.cleaned_data['file']
            cover = form.cleaned_data['cover']
            if upload:
                if file:
                    upload.file = file
                if cover:
                    upload.cover = cover
                upload.save()
            else:
                if file or cover:
                    UploadBook.objects.create(book=book, file=file, cover=cover)
            messages.success(request, 'Book updated successfully!')
            return redirect('book_list')
        else:
            messages.error(request, 'Error updating book. Please check the form.')
    else:
        form = BookForm(instance=book)

    return render(request, 'admin/book/book_edit.html', {'form': form, 'book': book})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete() 
    messages.success(request, 'Book deleted successfully!')
    return redirect(reverse('book_list'))

def book_list(request):
    books = Book.objects.all()
    return render(request, 'admin/book/book_list.html', {'books': books})

# def book_detail(request, book_id):
#     book = get_object_or_404(Book, pk=book_id)
#     return render(request, 'admin/book/book_detail.html', {'book': book})

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
            messages.success(request, 'Employee created successfully!')
            return redirect('employee_create')
        else:
            messages.error(request, 'Error creating employee. Please check the form.')
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
    messages.success(request, 'Employee deleted successfully!')
    return redirect(reverse('employee_list'))

@staff_member_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, id=pk)
    
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST, instance=employee)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.date_of_birth = form.cleaned_data['date_of_birth']
            user.phone = form.cleaned_data['phone']
            user.position = form.cleaned_data['position']
            user.save()
            
            messages.success(request, 'Employee updated successfully!')
            return redirect('employee_edit', pk=employee.id)  # Redirect to the same page or another view
        else:
            messages.error(request, 'Error updating employee. Please check the form.')
    else:
        form = EmployeeRegistrationForm(instance=employee)
    
    return render(request, 'admin/employee/employee_edit.html', {'form': form, 'employee': employee})


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
            messages.success(request, 'Member created successfully!')
            return redirect('member_create')
        else:
            messages.error(request, 'Error creating member. Please check the form.')
    else:
        form = MemberRegistrationForm()
    return render(request, 'admin/member/member_create.html', {'form': form})

@staff_member_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    member.user.delete()  # This will also delete the member due to the OneToOne relationship
    messages.success(request, 'Member deleted successfully!')
    return redirect(reverse('member_list'))

@staff_member_required
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member edited successfully!')
            return redirect(reverse('member_list'))
        else:
            messages.error(request, 'Error updating member. Please check the form.')
    else:
        form = MemberForm(instance=member)
    return render(request, 'admin/member/member_edit.html', {'form': form})


# Category management
@staff_member_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'admin/category/category_list.html', {'categories': categories})

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return render(request, 'admin/category/category_detail.html', {'category': category})

@staff_member_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_create')  
        else:
            messages.error(request, 'Error creating category. Please check the form.')
    else:
        form = CategoryForm()
    return render(request, 'admin/category/category_create.html', {'form': form})

@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()  
    messages.success(request, 'Category deleted successfully!')
    return redirect(reverse('category_list'))

@staff_member_required
def category_edit2(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect(reverse('category_list'))
        else:
            messages.error(request, 'Error updating category. Please check the form.')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin/category/category_create.html', {'form': form})

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect(reverse('category_list'))
    else:
        messages.error(request, 'Error updating category. Please check the form.')
    return render(request, 'admin/category/category_edit.html', {'category': category})

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
