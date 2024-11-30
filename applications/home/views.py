from django.shortcuts import render
from django.shortcuts import redirect
from types import SimpleNamespace

from ..administrators.models import Administrator
from ..administrators.views import AdminDashboard
from ..users.models import Customer
from ..audit.models import Audit_Tx, Audit_Deposit
from django.http import JsonResponse
from datetime import timedelta
from django.utils.timezone import localtime
from django.utils import timezone
import json

from ..const import *

from ..wallet.models import Wallet

from django.db.models import Q

# Create your views here.

def Home(request):
    if request.user.is_authenticated:
        c = request.user

        # check for admin:
        admin = Administrator.objects.filter(email=c.email).first()
        if admin is not None:
            return redirect(AdminDashboard)

        customer = Customer.objects.get(email=c.email)
        wallets = Wallet.objects.filter(customer=customer)
        wallet = wallets.filter(cvu__startswith = NUMERO_DE_ENTIDAD_VIRTUAL).first()
        bankAcc = wallets.filter(cvu__startswith = NUMERO_DE_ENTIDAD_BANCARIA).first()
        hasBankAcc = False
        if bankAcc is not None:
            hasBankAcc = True
        print(hasBankAcc)
        request.session["hasBankAcc"] = hasBankAcc
        request.session.modified = True
        obj = SimpleNamespace(customer=customer.name, balance=wallet.balance)
        customer = Customer.objects.filter(email = request.user.email)
        historialTxEntrante = Audit_Tx.objects.filter(destination_customer_id = customer[0].id)
        historialTxSaliente = Audit_Tx.objects.filter(audit__customer__id = customer[0].id)
        return render(request, 'home/home.html', {'customerWithBalance': obj, 'historialSent': historialTxSaliente,
                                                  'historialRecieved': historialTxEntrante})
    return redirect("Login")

def filter_history(request):
    if request.method == 'POST' and request.user.is_authenticated:
        #locale.setlocale(locale.LC_TIME, 'es_AR.UTF-8') #En caso de quererlo en español al mes de la fecha creacion
        data = json.loads(request.body.decode('utf-8'))
        filter_value = data.get('filter')
        customer = Customer.objects.get(email=request.user.email)
        today = timezone.now()  # This is timezone-aware

        # Adjust your deltas accordingly
        if filter_value == 'today':
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        elif filter_value == '3days':
            start_date = today - timedelta(days=3)
        elif filter_value == '1week':
            start_date = today - timedelta(days=7)
        else:  # 'all'
            start_date = None

        if start_date:
            historialTxEntrante = Audit_Tx.objects.filter(Q(destination_customer_id=customer.id, created_date__gte=start_date) & ~Q(audit__customer__id=customer.id))
            historialTxSaliente = Audit_Tx.objects.filter(Q(audit__customer_id = customer.id, created_date__gte=start_date) & ~Q(destination_customer_id=customer.id))
        else:
            historialTxEntrante = Audit_Tx.objects.filter(Q(destination_customer_id=customer.id) & ~Q(audit__customer__id=customer.id))
            historialTxSaliente = Audit_Tx.objects.filter(Q(audit__customer_id = customer.id) & ~Q(destination_customer_id=customer.id))

        historialDepositos = Audit_Deposit.objects.filter(audit__customer_id = customer.id)

        historialMisCuentas = Audit_Tx.objects.filter(Q(destination_customer_id=customer.id) & Q(audit__customer__id=customer.id))

        # Format data to return as JSON
        # TODO Refactor code and take into account Deposits too.
        sent_history = []
        received_history = []
        deposit_history = []
        myaccounts_history = []
        sent_content = False
        received_content = False
        deposit_content = False
        myaccounts_content = False

        for myAccountTx in historialMisCuentas:
            myaccounts_content = True
            myaccounts_history.append(
                {
                    'origin': "CA $$ "+myAccountTx.origin_acc.cvu.__str__() if str.startswith(myAccountTx.origin_acc.cvu, NUMERO_DE_ENTIDAD_BANCARIA) else "ECashFlow",
                    'destination': "CA $$ "+myAccountTx.destination_acc.cvu.__str__() if str.startswith(myAccountTx.destination_acc.cvu, NUMERO_DE_ENTIDAD_BANCARIA) else "ECashFlow",
                    'amount': '$'+myAccountTx.amount.__str__(),
                    'created_date': localtime(myAccountTx.created_date).strftime('%d %b. %Y %H:%M'),
                }
            )

        for deposit in historialDepositos:
            deposit_content = True
            deposit_history.append(
                {
                    'amount': '$' + deposit.amount.__str__(),
                    'created_date': localtime(deposit.created_date).strftime('%d %b. %Y %H:%M'),
                }
            )

        for tx in historialTxSaliente:
            sent_content = True
            sent_history.append({
                'destination_customer_id': tx.destination_customer.name+" "+tx.destination_customer.last_name if tx.destination_customer is not None else
                tx.destination_vendor.name,
                'amount': '$' + tx.amount.__str__(),
                'created_date': localtime(tx.created_date).strftime('%d %b. %Y %H:%M'),
            })

        for tx in historialTxEntrante:
            received_content = True
            received_history.append({
                'origin_customer_id': tx.audit.customer.name+" "+tx.audit.customer.last_name,
                'amount': '$' + tx.amount.__str__(),
                'created_date': localtime(tx.created_date).strftime('%d %b %Y %H:%M'),
            })
        return JsonResponse({'sent': sent_history, 'received': received_history, 'deposit': deposit_history, 'myaccounts': myaccounts_history, 'sent_content': sent_content, 'received_content':received_content, 'deposit_content': deposit_content, 'myaccounts_content': myaccounts_content})

    return JsonResponse({'error': 'Invalid request'}, status=400)