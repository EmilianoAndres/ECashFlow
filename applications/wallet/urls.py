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
from django.contrib import admin
from django.urls import path

from applications.wallet.views import *

urlpatterns = [
    #path('Transaction/', TransactionBase, name='TransactionBase'),
    path('CheckUserExistence/', CheckUserExistence, name='CheckUserExistence'),
    path('SendMoney/<int:contact_id>/', SendMoney, name='SendMoney'),
    path('startTransaction/', StartTransaction, name='StartTransaction'),
    path('Transaction/<int:contact_id>/', Transaction, name='Transaction'),
    path('SendMoneyFromBank/', SendMoneyFromBank, name='SendMoneyFromBank'),
    path('Deposit/', Deposit, name='Deposit'),
    path('FinishDeposit/', FinishDeposit, name='FinishDeposit'),
]
    

