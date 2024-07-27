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
from django.utils import timezone
import logging

from django.urls import reverse

logger = logging.getLogger(__name__)

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
            messages.error(request, 'ອີເມວນີ້ມີຢູ່ແລ້ວ.')
        elif form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  
            user.save()
            Member.objects.create(user=user, address=form.cleaned_data['address'], phone=form.cleaned_data['phone'])
            messages.success(request, 'ການລົງທະບຽນສຳເລັດແລ້ວ! ບັນຊີຂອງທ່ານຕ້ອງໄດ້ຮັບການອະນຸມັດຈາກຜູ້ເບິ່ງແຍງລະບົບກ່ອນທີ່ທ່ານຈະສາມາດເຂົ້າສູ່ລະບົບໄດ້.')
            return redirect('login')
        else:
            messages.error(request, 'ເກີດຄວາມຜິດພາດໃນການສະໝັກສະມາຊິກ. ກະລຸນາຕື່ມຂໍ້ມູນໃຫ້ຄົບ.')
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
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'ຕ້ອງການອີເມລ໌ ແລະລະຫັດຜ່ານ.')
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
                    messages.warning(request, 'ບັນຊີສະມາຊິກຂອງທ່ານຍັງບໍ່ທັນໄດ້ຮັບການອະນຸມັດຈາກຜູ້ເບິ່ງແຍງລະບົບເທື່ອ.')
            elif hasattr(user, 'employee'):
                login(request, user)
                return redirect('home')  # Redirect to a success page.
            else:
                messages.error(request, 'ບັນຊີຂອງທ່ານບໍ່ໄດ້ເຊື່ອມໂຍງກັບສະມາຊິກ ຫຼືໂປຣໄຟລ໌ພະນັກງານໃດໆ.')
        else:
            messages.error(request, 'ອີເມວ ຫຼື ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ.')
    
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def download_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    upload = book.uploads.first()  # Adjust this query based on your logic

    if not upload or not upload.file:
        return HttpResponse("ບໍ່ພົບໄຟລ໌.", status=404)

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
        return HttpResponse("ບໍ່ພົບໄຟລ໌.", status=404)
    

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
            messages.success(request, 'ເພີ່ມຂໍ້ມູນປຶ້ມສຳເລັດແລ້ວ!')
            return redirect('book_create')
        else:
            messages.error(request, 'ເກີດຄວາມຜິດພາດໃນການເພີ່ມຂໍ້ມູນປຶ້ມ. ກະລຸນາຕື່ມຂໍ້ມູນໃຫ້ຄົບ.')
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
            messages.success(request, 'ແກ້ໄຂຂໍ້ມູນປຶ້ມສຳເລັດແລ້ວ!')
            return redirect('book_list')
        else:
            messages.error(request, 'ເກີດຄວາມຜິດພາດໃນການແກ້ໄຂຂໍ້ມູນປຶ້ມ. ກະລຸນາຕື່ມຂໍ້ມູນໃຫ້ຄົບ.')
    else:
        form = BookForm(instance=book)
        if book.publication_date:
            form.initial['publication_date'] = book.publication_date.strftime('%Y-%m-%d')

    return render(request, 'admin/book/book_edit.html', {'form': form, 'book': book})

@staff_member_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete() 
    messages.success(request, 'ລຶບຂໍ້ມູນປຶ້ມສຳເລັດແລ້ວ!')
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
        form = AdminEmployeeCreationForm(request.POST)
        email = request.POST.get('email')
        if UserModel.objects.filter(email=email).exists():
            messages.error(request, 'ອີເມວນີ້ມີຢູ່ແລ້ວ.')
        elif form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'ເພີ່ມຂໍ້ມູນພະນັກງານສຳເລັດແລ້ວ!')
                return redirect('employee_list')  # Redirect to the employee list or detail page
            except Exception as e:
                messages.error(request, f'ເກີດຄວາມຜິດພາດໃນການເພີ່ມຂໍ້ມູນພະນັກງານ: {e}')
        else:
            messages.error(request, 'ເກີດຄວາມຜິດພາດໃນການເພີ່ມຂໍ້ມູນພະນັກງານ. ກະລຸນາຕື່ມຂໍ້ມູນໃຫ້ຄົບ.')
    else:
        form = AdminEmployeeCreationForm()
    
    return render(request, 'admin/employee/employee_create.html', {'form': form})

@staff_member_required
def employee_list(request):
    employees = Employee.objects.all().order_by('-id')
    return render(request, 'admin/employee/employee_list.html', {'employees': employees})

@staff_member_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.user.delete()  # This will also delete the employee due to the OneToOne relationship
    messages.success(request, 'ລຶບຂໍ້ມູນພະນັກງານສຳເລັດແລ້ວ!')
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
            messages.success(request, 'ແກ້ໄຂຂໍ້ມູນພະນັກງານສຳເລັດແລ້ວ!')
            return redirect('employee_list')
            # return redirect('employee_edit', pk=user.pk)
        else:
            messages.error(request, 'ເກີດຄວາມຜິດພາດໃນການແກ້ໄຂຂໍ້ມູນພະນັກງານ. ກະລຸນາຕື່ມຂໍ້ມູນໃຫ້ຄົບ.')
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
            messages.error(request, 'ອີເມວນີ້ມີຢູ່ແລ້ວ.')
        elif form.is_valid():
            form.save()
            messages.success(request, 'ເພີ່ມຂໍ້ມູນສະມາຊິກສຳເລັດແລ້ວ!')
            return redirect('employee_create')  # Redirect to the member list page for admin
        else:
            messages.error(request, 'ເກີດຄວາມຜິດພາດໃນການເພີ່ມຂໍ້ມູນສະມາຊິກ. ກະລຸນາຕື່ມຂໍ້ມູນໃຫ້ຄົບ.')
    else:
        form = AdminMemberCreationForm()
    
    return render(request, 'admin/member/member_create.html', {'form': form})

@staff_member_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    member.user.delete()  # This will also delete the member due to the OneToOne relationship
    messages.success(request, 'ລຶບຂໍ້ມູນສະມາຊິກສຳເລັດແລ້ວ!')
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
            messages.success(request, 'ແກ້ໄຂຂໍ້ມູນສະມາຊິກສຳເລັດແລ້ວ!')
            return redirect('member_list')
        else:
            messages.error(request, 'ເກີດຄວາມຜິດພາດໃນການແກ້ໄຂຂໍ້ມູນສະມາຊິກ. ກະລຸນາຕື່ມຂໍ້ມູນໃຫ້ຄົບ.')
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
    messages.success(request, f'{member.user.email} ໄດ້ຮັບການອະນຸມັດ.')
    return redirect('member_list')

@staff_member_required
def reject_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.is_approved = False
    member.user.is_active = False  # Make the user inactive
    member.user.save()
    member.save()
    messages.success(request, f'{member.user.email} ໄດ້ຖືກປະຕິເສດ.')
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
            messages.success(request, 'ເພີ່ມຂໍ້ມູນໝວດໝູ່ສຳເລັດແລ້ວ!')
            return redirect('category_create')  
        else:
            messages.error(request, 'ເກີດຄວາມຜິດພາດໃນການເພີ່ມຂໍ້ມູນໝວດໝູ່. ກະລຸນາຕື່ມຂໍ້ມູນໃຫ້ຄົບ.')
    else:
        form = CategoryForm()
    return render(request, 'admin/category/category_create.html', {'form': form})

@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()  
    messages.success(request, 'ລຶບຂໍ້ມູນໝວດໝູ່ສຳເລັດແລ້ວ!')
    return redirect(reverse('category_list'))

@staff_member_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.save()
        messages.success(request, 'ແກ້ໄຊຂໍ້ມູນໝວດໝູ່ສຳເລັດແລ້ວ!')
        return redirect(reverse('category_list'))
    else:
        messages.error(request, 'Error updating category. Please check the form.')
    return render(request, 'admin/category/category_edit.html', {'category': category})

