
from django.urls import path
from .views import *

urlpatterns = [
    path('administrator/dashboard/', AdminDashboard, name="AdminDashboard"),
    path('administrator/dashboard/customers', AdminDashboardCustomers, name="AdminDashboardCustomers"),
    path('administrator/dashboard/vendors', AdminDashboardVendors, name="AdminDashboardVendors"),
    path('administrator/dashboard/transactions', AdminDashboardTransactions, name="AdminDashboardTransactions")
]