"""
URL configuration for ecashflow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from .views import *

urlpatterns = [
    path('register/', Register, name="Register"),
    path('update-email', UpdateEmail, name="UpdateEmail"),
    path('update-password', UpdatePassword, name="UpdatePassword"),
    path('change-password', ChangePassword, name="ChangePassword"),
    path('forgot-password', ForgotPasswordChange, name="ForgotPassword"),
    path('register-dni/', UploadDni, name="UploadDni"),
    path('login/', Login, name="Login"),
    path('logout/', Logout, name="Logout"),
    path('validateEmail', ValidateEmail, name="ValidateEmail"),
    path('bankaccount/', BankAccount, name="BankAccount"),
    path('createbankaccount/', CreateBankAccount, name="CreateBankAccount"),
    path('dashboard/', Dashboard, name="Dashboard"), 
    path('contact/', Contact_list, name="ContactList"),
    path('add_contact/', add_contact, name='AddContact'),
    path('delete_contact/<int:contact_id>/', delete_contact, name='DeleteContact'),
    path('add_favorite/<int:contact_id>/', AddFavorite, name='AddFavorite'),
    path('delete_favorite/<int:contact_id>/', DeleteFavorite, name='DeleteFavorite'),
]
