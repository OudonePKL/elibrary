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

    # admin
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('employee/<int:pk>/delete/', views.delete_employee, name='delete_employee'),
    path('employee/<int:pk>/edit/', views.edit_employee, name='edit_employee'),
]
