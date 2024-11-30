from datetime import datetime
from types import SimpleNamespace

from django.core.paginator import Paginator
from django.shortcuts import render

from applications.users.models import Customer
from applications.vendors.models import Vendor, VendorType
from applications.wallet.models import Wallet, EscrowWallet
from django.db.models import Sum
from django.utils import timezone

from ..audit.models import Audit_Tx
from ..const import NUMERO_DE_SUCURSAL_ECASHFLOW, NUMERO_DE_SUCURSAL_BANCO, NUMERO_DE_ENTIDAD_VIRTUAL, \
    NUMERO_DE_ENTIDAD_BANCARIA
from django.db.models import Q

# Create your views here.

def AdminDashboard(request):
    totalCustomers = Customer.objects.count()
    totalVendors = Vendor.objects.count()
    totalCustomerFunds = Wallet.objects.filter(Q(cvu__startswith=NUMERO_DE_ENTIDAD_VIRTUAL) & Q(is_active=True)).aggregate(balance=Sum('balance'))['balance']
    if totalCustomerFunds is not None:
        totalCustomerFunds = round(totalCustomerFunds, 2)
    else:
        totalCustomerFunds = 0
    totalVendorFunds = EscrowWallet.objects.filter(is_active=True).aggregate(balance=Sum('balance'))['balance']
    if totalVendorFunds is not None:
        totalVendorFunds = round(totalVendorFunds, 2)
    else:
        totalVendorFunds = 0
    # Last 6 transactions
    totalTx = list(Audit_Tx.objects.filter(is_active=True)
                   .order_by('created_date')
                   .values_list('audit__customer__full_name', 'destination_customer__full_name', 'destination_vendor__name', 'amount', 'created_date')
                   [:6])
    obj = SimpleNamespace(totalCustomers=totalCustomers, totalVendors=totalVendors, totalVendorFunds=totalVendorFunds, totalCustomerFunds=totalCustomerFunds)
    return render(request, 'admin/dashboard.html', {'data': obj, 'tx': totalTx})

def AdminDashboardCustomers(request):
    search_query = request.GET.get('search')
    customer_id = request.GET.get('customer_id')
    wallet_id = request.GET.get('wallet_id')
    bank_account_id = request.GET.get('bank_account_id')
    action = request.GET.get('action')


    if customer_id is not None:
        customer = Customer.objects.filter(id=customer_id).first()
        if customer is not None:
            wallets = Wallet.objects.filter(customer=customer)
            wallet = wallets.filter(cvu__startswith=NUMERO_DE_ENTIDAD_VIRTUAL).first()
            bankAccs = wallets.filter(cvu__startswith=NUMERO_DE_ENTIDAD_BANCARIA)

            if wallet_id is None and bank_account_id is None:
                if action == 'disable':
                    customer.is_active = False
                    wallet.is_active = False
                    for bankAcc in bankAccs:
                        bankAcc.is_active = False
                        bankAcc.save()
                    customer.remove_all_sessions()

                elif action == 'enable':
                    customer.is_active = True
                    wallet.is_active = True
                    for bankAcc in bankAccs:
                        bankAcc.is_active = True
                        bankAcc.save()

                customer.save()
                wallet.save()
                return render(request, 'admin/customers.html',
                              {'customer': customer, 'wallet': wallet, 'bank_accounts': bankAccs})

            if wallet_id is not None:
                account = Wallet.objects.filter(id=wallet_id).first()
            else:
                account = Wallet.objects.filter(id=bank_account_id).first()

            if account is not None:
                if action == 'disable':
                    account.is_active = False
                elif action == 'enable':
                    account.is_active = True
                account.save()
                return render(request, 'admin/customers.html',
                              {'customer': customer, 'wallet': wallet, 'bank_accounts': bankAccs})

    # Filter customers based on the search query
    customers = Customer.objects.all()

    if not search_query:
        return render(request, 'admin/customers.html')

    customer = customers.filter(
            Q(email__icontains=search_query) |
            Q(cuit__icontains=search_query)
        ).first()

    wallets = Wallet.objects.filter(customer=customer)
    wallet = wallets.filter(cvu__startswith=NUMERO_DE_ENTIDAD_VIRTUAL).first()
    bankAccs = wallets.filter(cvu__startswith=NUMERO_DE_ENTIDAD_BANCARIA)

    return render(request, 'admin/customers.html', {'customer': customer, 'wallet': wallet, 'bank_accounts': bankAccs})

def AdminDashboardVendors(request):
    search_query = request.GET.get('search')

    vendors = Vendor.objects.all()

    if not search_query:
        return render(request, 'admin/vendors.html')

    vendor = vendors.filter(
        Q(code__icontains=search_query) |
        Q(cuit__icontains=search_query) |
        Q(name__icontains=search_query)
    ).first()

    if vendor is None:
        return render(request, 'admin/vendors.html')

    escrowWallet = EscrowWallet.objects.filter(vendor=vendor).first()
    return render(request, 'admin/vendors.html', {'wallet': escrowWallet, 'vendor': vendor, "vendor_type": vendor.vendor_type})

def AdminDashboardTransactions(request):
    # Getting query params
    account_holder1 = request.GET.get('account_holder1')
    account_holder2 = request.GET.get('account_holder2')
    is_origin1 = request.GET.get('is_origin1')  # Will be None if not checked
    is_origin2 = request.GET.get('is_origin2')  # Will be None if not checked
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')
    time_filter = request.GET.get('time_filter')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    transactions = Audit_Tx.objects.all()

    if account_holder1:
        if is_origin1:
            transactions = transactions.filter(Q(audit__customer__email=account_holder1) | Q(audit__customer__cuit=account_holder1))
        else:
            transactions = transactions.filter(Q(destination_customer__email=account_holder1) | Q(destination_customer__cuit=account_holder1))

    if account_holder2:
        if is_origin2:
            transactions = transactions.filter(Q(audit__customer__email=account_holder2) | Q(audit__customer__cuit=account_holder2))
        else:
            transactions = transactions.filter(Q(destination_customer__email=account_holder2) | Q(destination_customer__cuit=account_holder2))

    if min_amount:
        transactions = transactions.filter(amount__gte=min_amount)

    if max_amount:
        transactions = transactions.filter(amount__lte=max_amount)

    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            transactions = transactions.filter(created_date__range=(start_date, end_date))
        except ValueError:
            return render(request, 'admin/transactions.html')

    elif start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            transactions = transactions.filter(created_date__gte=start_date)
        except ValueError:
            return render(request, 'admin/transactions.html')

    elif end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            transactions = transactions.filter(created_date__lte=end_date)
        except ValueError:
            return render(request, 'admin/transactions.html')

    elif time_filter:
        # Handle time_filter logic here (example: filter based on predefined time frames)
        if time_filter == '15_min':
            transactions = transactions.filter(created_date__gte=timezone.now() - timezone.timedelta(minutes=15))
        elif time_filter == '1_hour':
            transactions = transactions.filter(created_date__gte=timezone.now() - timezone.timedelta(hours=1))
        elif time_filter == '12_hours':
            transactions = transactions.filter(created_date__gte=timezone.now() - timezone.timedelta(hours=12))
        # Add more time filter options as needed

    # Pagination logic
    paginator = Paginator(transactions.order_by('created_date'), 5)  # Show 5 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/transactions.html', {'page_obj': page_obj})