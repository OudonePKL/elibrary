# urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('register_member/', views.register_member, name='register_member'),
    path('register_employee/', views.register_employee, name='register_employee'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('download/<int:book_id>/', views.download_book, name='download_book'),

    # administrator page
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # employee management
    path('employee_list/', views.employee_list, name='employee_list'),
    path('employee_create/', views.employee_create, name='employee_create'),
    path('employee/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('employee/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    # member management
    path('member_list/', views.member_list, name='member_list'),
    path('member_create/', views.member_create, name='member_create'),
    path('member/<int:pk>/delete/', views.member_delete, name='member_delete'),
    path('member/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('approve_member/<int:member_id>/', views.approve_member, name='approve_member'),
    path('reject_member/<int:member_id>/', views.reject_member, name='reject_member'),
    # category management
    path('category_list/', views.category_list, name='category_list'),
    path('category_create/', views.category_create, name='category_create'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('category/<int:pk>/edit/', views.category_edit, name='category_edit'),
    # Book management
    path('book_list/', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book_create/', views.book_create, name='book_create'),
    path('booke/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),

]
