# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from .models import Employee, Member, Category, Book, UploadBook, DownloadBook
from django.db import models
from django.forms import modelformset_factory
from users.models import UserModel

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import MemberRegistrationForm, MemberEditForm, EmployeeRegistrationForm, EmployeeEditForm, EmployeeForm, BookForm, UploadBookFormSet, MemberForm, CategoryForm, AdminMemberCreationForm, AdminEmployeeCreationForm
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
        email = request.POST.get('email')
        
        if UserModel.objects.filter(email=email).exists():
            messages.error(request, 'This email already exist.')
        elif form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  
            user.save()
            Member.objects.create(user=user, address=form.cleaned_data['address'], phone=form.cleaned_data['phone'])
            messages.success(request, 'Registration successful! Your account needs to be approved by an admin before you can log in.')
            return redirect('login')
        else:
            messages.error(request, 'Error creating member. Please check the form.')
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

# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#         user = authenticate(request, username=email, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('home')  # Redirect to a success page.
#         else:
#             messages.error(request, 'Invalid email or password.')
#     return render(request, 'registration/login.html')

# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#         user = authenticate(request, username=email, password=password)
#         print(user)
#         if user is not None:
#             try:
#                 if user.member.is_approved:
#                     login(request, user)
#                     return redirect('home')  # Redirect to a success page.
#                 else:
#                     messages.warning(request, 'Your account is not yet approved by an admin.')
#             except Member.DoesNotExist:
#                 messages.error(request, 'Invalid email or password.')

#             # login(request, user)
#             # return redirect('home')  # Redirect to a success page.
#         else:
#             messages.error(request, 'Invalid email or password.')
#     return render(request, 'registration/login.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'registration/login.html')
        
        user = authenticate(request, username=email, password=password)
        print(user)
        if user is not None:
            if hasattr(user, 'member'):
                # Handle member-specific logic
                if user.member.is_approved:
                    login(request, user)
                    return redirect('home')  # Redirect to a success page.
                else:
                    messages.warning(request, 'Your member account is not yet approved by an admin.')
            elif hasattr(user, 'employee'):
                # Handle employee-specific logic
                login(request, user)
                return redirect('home')  # Redirect to a success page.
            else:
                messages.error(request, 'Your account is not associated with any member or employee profile.')
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
@staff_member_required
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

@staff_member_required
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
        if book.publication_date:
            form.initial['publication_date'] = book.publication_date.strftime('%Y-%m-%d')

    return render(request, 'admin/book/book_edit.html', {'form': form, 'book': book})

@staff_member_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete() 
    messages.success(request, 'Book deleted successfully!')
    return redirect(reverse('book_list'))

@staff_member_required
def book_list(request):
    books = Book.objects.all().order_by('-id')
    return render(request, 'admin/book/book_list.html', {'books': books})


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
        email = request.POST.get('email')
        
        if UserModel.objects.filter(email=email).exists():
            messages.error(request, 'This email already exist.')
        elif form.is_valid():
            # user = form.save()
            # login(request, user)
            
            user = form.save(commit=False)
            user.is_admin = True
            user.save()
            messages.success(request, 'Employee created successfully!')
            return redirect('employee_create')  # Redirect to a home page or any other page after registration
        else:
            messages.error(request, 'Error creating employee. Please check the form.')
    else:
        form = EmployeeRegistrationForm()
    return render(request, 'admin/employee/employee_create.html', {'form': form})

@staff_member_required
def employee_list(request):
    employees = Employee.objects.all().order_by('-id')
    return render(request, 'admin/employee/employee_list.html', {'employees': employees})

@staff_member_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.user.delete()  # This will also delete the employee due to the OneToOne relationship
    messages.success(request, 'Employee deleted successfully!')
    return redirect(reverse('employee_list'))

@staff_member_required
def employee_edit(request, pk):
    user = get_object_or_404(UserModel, pk=pk)  # Ensure this matches the UserModel's primary key field
    employee = get_object_or_404(Employee, user=user)
    print(pk)
    print(user)
    if request.method == 'POST':
        form = EmployeeEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('employee_list')
            # return redirect('employee_edit', pk=user.pk)
        else:
            messages.error(request, 'Error updating employee. Please check the form.')
    else:
        form = EmployeeEditForm(instance=user)
        if employee.date_of_birth:
            form.initial['date_of_birth'] = employee.date_of_birth.strftime('%Y-%m-%d')
    return render(request, 'admin/employee/employee_edit.html', {'form': form})


# Member management
@staff_member_required
def member_list(request):
    members = Member.objects.all().order_by('-id')
    return render(request, 'admin/member/member_list.html', {'members': members})

@staff_member_required
def member_create(request):
    if not request.user.is_staff:
        return redirect('home')  # Only allow staff to access this view

    if request.method == 'POST':
        form = AdminMemberCreationForm(request.POST)
        email = request.POST.get('email')
        
        if UserModel.objects.filter(email=email).exists():
            messages.error(request, 'This email already exist.')
        elif form.is_valid():
            form.save()
            messages.success(request, 'Member added successfully!')
            return redirect('employee_create')  # Redirect to the member list page for admin
        else:
            messages.error(request, 'Error adding member. Please check the form.')
    else:
        form = AdminMemberCreationForm()
    
    return render(request, 'admin/member/member_create.html', {'form': form})

@staff_member_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    member.user.delete()  # This will also delete the member due to the OneToOne relationship
    messages.success(request, 'Member deleted successfully!')
    return redirect(reverse('member_list'))

@staff_member_required
def member_edit(request, pk):
    user = get_object_or_404(UserModel, pk=pk)  # Ensure this matches the UserModel's primary key field
    print(pk)
    print(user)
    if request.method == 'POST':
        form = MemberEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member updated successfully!')
            return redirect('member_list')
            # return redirect('member_edit', pk=user.pk)
        else:
            messages.error(request, 'Error updating member. Please check the form.')
    else:
        form = MemberEditForm(instance=user)
    return render(request, 'admin/member/member_edit.html', {'form': form})

@staff_member_required
def approve_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.is_approved = True
    member.user.is_active = True  # Make the user active
    member.user.save()
    member.save()
    messages.success(request, f'{member.user.email} has been approved.')
    return redirect('member_list')

@staff_member_required
def reject_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.is_approved = False
    member.user.is_active = False  # Make the user inactive
    member.user.save()
    member.save()
    messages.success(request, f'{member.user.email} has been rejected.')
    return redirect('member_list')


# Category management
@staff_member_required
def category_list(request):
    categories = Category.objects.all().order_by('-id')
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

