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
        type_value = data.get('type')
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
        
        filter_dict = {}
        exclude_dict = {}
        content = False
        jsonToSend = []

        if start_date:
            filter_dict["created_date__gte"] = start_date

        if type_value == "sent":
            filter_dict["audit__customer_id"] = customer.id
            exclude_dict["destination_customer_id"] = customer.id
        
        elif type_value == "recieved":
            filter_dict["destination_customer_id"] = customer.id
            exclude_dict["audit__customer__id"] = customer.id
        
        elif type_value == "deposit":
            filter_dict["audit__customer_id"] = customer.id
            data = Audit_Deposit.objects.filter(Q(**filter_dict))
            for tx in data:
                content = True
                jsonToSend.append(
                {
                    'amount': '$'+tx.amount.__str__(),
                    'created_date': localtime(tx.created_date).strftime('%d %b. %Y %H:%M'),
                }
            )
        
        elif type_value == "myaccounts":
            filter_dict["destination_customer_id"] = customer.id
            filter_dict["audit__customer__id"] = customer.id

        if type_value != "deposit":
            data = Audit_Tx.objects.filter(Q(**filter_dict) & ~Q(**exclude_dict))
            for tx in data:
                content = True
                destination = ""
                if (tx.destination_acc is not None):
                    destination = "CA $$ "+tx.destination_acc.cvu.__str__() if str.startswith(tx.destination_acc.cvu, NUMERO_DE_ENTIDAD_BANCARIA) else "ECashFlow"
                jsonToSend.append(
                    {
                        'origin_customer_id': tx.origin_acc.customer.name + " " + tx.origin_acc.customer.last_name,
                        'destination_customer_id': tx.destination_customer.name+" "+tx.destination_customer.last_name if tx.destination_customer is not None else tx.destination_vendor.name,
                        'origin': "CA $$ "+tx.origin_acc.cvu.__str__() if str.startswith(tx.origin_acc.cvu, NUMERO_DE_ENTIDAD_BANCARIA) else "ECashFlow",
                        'destination': destination,
                        'amount': '$'+tx.amount.__str__(),
                        'created_date': localtime(tx.created_date).strftime('%d %b. %Y %H:%M'),
                    }
                )

        return JsonResponse({'sent': jsonToSend, 'content': content})

    return JsonResponse({'error': 'Invalid request'}, status=400)