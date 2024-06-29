# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Book

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm
from django.core.paginator import Paginator
from django.contrib import messages

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



def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to home page or profile page
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

# def login_view(request):
#     if request.method == 'POST':
#         form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('home')  # Redirect to home page or profile page
#     else:
#         form = UserLoginForm()
#     return render(request, 'login.html', {'form': form})


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
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

