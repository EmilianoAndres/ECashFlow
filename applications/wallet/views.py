from django.db.transaction import atomic
from django.shortcuts import render, redirect
from django.db.models import Q

from applications.audit.models import Audit, Audit_Tx, Audit_Deposit
from applications.const import NUMERO_DE_ENTIDAD_VIRTUAL, NUMERO_DE_ENTIDAD_BANCARIA
from applications.users.models import Customer
from applications.users.views import BankAccount
from applications.wallet.models import Wallet, Contact, Deposit as DepositModel
from django.contrib import messages

from types import SimpleNamespace
import json
from decimal import *
import logging
import qrcode
import binascii
from os import urandom
from io import BytesIO
from base64 import b64encode
from re import search


def clear_messages(request):
    storage = messages.get_messages(request)
    storage.used = True

# Create your views here.
def TransactionBase(request):
    balance = request.session['userBalance']
    c = request.user
    obj = SimpleNamespace(customer=c, balance=balance)
    return render(request, 'wallet/transaction.html', {'customerWithBalance': obj})

def CheckUserExistence(request):
    if not request.user.is_authenticated:
        return redirect("Login")
    if request.method == 'POST':
        user = Customer.objects.filter(email=request.user.email).first()
        userWallet = Wallet.objects.get(Q(customer=user) & Q(cvu__startswith=NUMERO_DE_ENTIDAD_VIRTUAL))
        data = request.POST.get("contactData")
        if not ((str.isnumeric(data) and len(data) == 22) or alias_regex(data)):
            
            errorContact = "Invalid input."
            messages.add_message(request, messages.ERROR, errorContact)
            return redirect('StartTransaction')

        walletContact = Wallet.objects.filter( Q(cvu=data) | Q(alias=data)).first()

        if str.startswith(walletContact.cvu, NUMERO_DE_ENTIDAD_BANCARIA):
            if walletContact.customer == user:
                existingContact = Contact.objects.filter(Q(customer=user) & Q(wallet=walletContact)).first()

                if existingContact != None:
                    return render(request, 'wallet/transaction.html', {"contact_id": existingContact.id})

                newContact = Contact()
                newContact.wallet = walletContact
                newContact.customer = user
                newContact.is_own_bank_acc = True
                newContact.save()

                return render(request, 'wallet/transaction.html', {"contact_id": newContact.id})
            errorContact = "No puedes enviar dinero a una cuenta de banco no propia."
            messages.add_message(request, messages.ERROR, errorContact)
            return redirect('StartTransaction')
            
        if walletContact == None:
            errorContact = "No encontramos un usuario registrado con esos datos."
            messages.add_message(request, messages.ERROR, errorContact)
            return redirect('StartTransaction')

        if walletContact == userWallet:
            messages.add_message(request, messages.ERROR, "No te podés enviar dinero a vos mismo.")
            return redirect('StartTransaction')

        existingContact = Contact.objects.filter(Q(customer=user) & Q(wallet=walletContact)).first()

        if existingContact != None:
            return render(request, 'wallet/transaction.html' , {"contact_id":existingContact.id})

        newContact = Contact()
        newContact.wallet = walletContact
        newContact.customer = userWallet.customer
        newContact.save()        
        
        return render(request, 'wallet/transaction.html' , {"contact_id":newContact.id})

    return redirect("Home")

def StartTransaction(request):
    return render(request, 'wallet/startTransaction.html')

def Transaction(request, contact_id): 
    if not request.user.is_authenticated:
        return redirect("Login")
    if request.method == 'POST':
        if SendMoney(request, contact_id):
            return redirect("Home")
        else:
            return render(request, 'wallet/transaction.html' , {"contact_id":contact_id})
    return render(request, 'wallet/transaction.html' , {"contact_id":contact_id})

def Deposit(request):
    if not request.user.is_authenticated:
        return redirect("Login")

    if request.method == 'POST':
        token = generate_validation_token(50)
        amount = request.POST.get("deposit")

        decimalAmount = Decimal(0)
        try:
            decimalAmount = Decimal(amount)
        except:
            messages.add_message(request, messages.ERROR, "Por favor ingrese un monto válido")
            return render(request, 'wallet/deposit.html', {'qr_image_data': None , 'token': ""})

        if Decimal.is_zero(decimalAmount) or decimalAmount < 0:
            messages.add_message(request, messages.ERROR, "Por favor ingrese un monto válido")
            return render(request, 'wallet/deposit.html', {'qr_image_data': None, 'token': ""})

        loggedUser = Customer.objects.filter(email=request.user.email)[0]
        usersWallet = Wallet.objects.filter(Q(customer=loggedUser.id) & Q(cvu__startswith='000'))[0]
        deposit = DepositModel()
        deposit.wallet = usersWallet
        deposit.amount = decimalAmount
        deposit.token = token
        deposit.save()

        url_with_token = request.build_absolute_uri(f'/FinishDeposit/?token={token}')
        qr = qrcode.make(url_with_token)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        img_base64 = b64encode(buffer.getvalue()).decode('utf-8')

        return render(request, 'wallet/deposit.html', {'qr_image_data': img_base64, 'token': url_with_token})
    
    return render(request, 'wallet/deposit.html', {'qr_image_data': None , 'token': ""})

def FinishDeposit(request):
    if not request.user.is_authenticated:
        return redirect("Login")
    
    token = request.GET.get('token', None)
    if not token:
        return render(request, 'wallet/finishDeposit.html', {"permission": False})

    loggedUser = Customer.objects.filter(email=request.user.email).first()
    if not loggedUser:
        return render(request, 'wallet/finishDeposit.html', {"permission": False})
    
    usersWallet = Wallet.objects.filter(Q(customer=loggedUser.id) & Q(cvu__startswith='000')).first()
    if not usersWallet:
        return render(request, 'wallet/finishDeposit.html', {"permission": False})
    
    deposit = DepositModel.objects.filter(Q(wallet=usersWallet.id) & Q(token=token) & Q(is_used = False)).first()
    if not deposit:
        return render(request, 'wallet/finishDeposit.html', {"permission": False})
    
    ImpactDeposit(deposit, usersWallet)

    return render(request, 'wallet/finishDeposit.html', {"permission": True})

@atomic
def ImpactDeposit(deposit, usersWallet):
    usersWallet.balance = usersWallet.balance + deposit.amount
    usersWallet.save()

    deposit.is_used = True
    deposit.save()
    SaveAuditDeposit(usersWallet, deposit.amount)
    return True

def SendMoney(request, contact_id):
    clear_messages(request)
    sender = Customer.objects.filter(email=request.user.email).first()
    senderWallet = Wallet.objects.filter(Q(customer=sender.id) & Q(cvu__startswith=NUMERO_DE_ENTIDAD_VIRTUAL)).first()
    contact = Contact.objects.filter(Q(id = contact_id) & Q(wallet__cvu__startswith=NUMERO_DE_ENTIDAD_VIRTUAL)).first()
    if contact is not None and senderWallet == contact.wallet:
        messages.add_message(request, messages.ERROR, "No te podés enviar dinero a vos mismo.")
        return False
    amount = request.POST.get("amount")
    try:
        Decimal(amount)
    except:
        messages.add_message(request, messages.ERROR, "Por favor ingrese un monto válido")
        return render(request, 'wallet/deposit.html', {'qr_image_data': None, 'token': ""})
    decimalAmount = convertToDecimal(amount)
    if Decimal.is_zero(decimalAmount) or decimalAmount < 0:
        messages.add_message(request, messages.ERROR, "Por favor ingresá un monto válido")
        return False
    infoOwnAcc = ""
    if contact is None:
        contact = Contact.objects.filter(Q(customer=sender) & Q(wallet__cvu__startswith=NUMERO_DE_ENTIDAD_BANCARIA)).first()
        infoOwnAcc = f"Enviaste ${decimalAmount} a tu cuenta de banco!"
        if contact is None:
            # This should never happen
            messages.add_message(request, messages.ERROR, "Hubo un error interno del servidor!")
            return False
    infoMessage = f"Enviaste ${decimalAmount} a {contact.customer.full_name}"
    receiverWallet = contact.wallet
    success = SendMoneyAtomic(decimalAmount, senderWallet, receiverWallet, request)
    if not success:
        return False
    request.session['userBalance'] = str(senderWallet.balance)
    SaveAuditTx(senderWallet, receiverWallet, decimalAmount)
    messages.add_message(request, messages.INFO, infoMessage if infoOwnAcc == "" else infoOwnAcc)
    return True

def SendMoneyFromBank(request):
    clear_messages(request)
    sender = Customer.objects.filter(email=request.user.email)[0]
    account = request.POST.get("selected_account_cbu")
    bankAcc = sender.wallet_set.filter(Q(cvu=account) & Q(customer__email=request.user.email)).first()
    if bankAcc is None:
        messages.add_message(request, messages.ERROR, "Hubo un Error! Intentá nuevamente.")
        return redirect(BankAccount)
    wallet = sender.wallet_set.filter(cvu__startswith='000')[0]
    obj = SimpleNamespace(customer=sender.name+" "+sender.last_name, balance=bankAcc.balance, cuit=sender.cuit, cbu=bankAcc.cvu, alias=bankAcc.alias)
    amount = request.POST.get("amount")
    try:
        amount = Decimal(amount)
    except InvalidOperation:
        messages.add_message(request, messages.ERROR, "Por favor ingresá un monto válido.")
        return redirect(BankAccount)
    if Decimal.is_zero(amount) or amount < 0:
        messages.add_message(request, messages.ERROR, "Por favor ingresá un monto válido")
        return redirect(BankAccount)
    success = SendMoneyAtomic(amount, bankAcc, wallet, request)
    if not success:
        return redirect(BankAccount)
    SaveAuditTx(bankAcc, wallet, amount)
    messages.add_message(request, messages.INFO, f"Enviaste exitosamente ${amount} desde tu Caja de Ahorro CA $$ {account} a tu billetera")
    request.session['userBalance'] = str(wallet.balance)
    logging.info(f"successfully sent {amount} between the same user's bank account: {bankAcc.cvu} and their wallet: {wallet.cvu}")
    return redirect(BankAccount)
    

@atomic
def SendMoneyAtomic(amount: Decimal, senderWallet: Wallet, receiverWallet: Wallet, request):
    if senderWallet.balance < amount:
        messages.add_message(request, messages.ERROR, "Saldo insuficiente.")
        return False
    senderWallet.balance -= amount
    receiverWallet.balance += amount
    senderWallet.save()
    receiverWallet.save()
    return True

def SaveAuditDeposit(customerWallet, amount):
    newAudit = Audit()
    newAudit.customer = customerWallet.customer
    newAuditDeposit = Audit_Deposit()
    newAudit.save()
    newAuditDeposit.audit = newAudit
    newAuditDeposit.amount = amount
    newAuditDeposit.save()

def SaveAuditTx(sender, receiver, amount):
    newAudit = Audit()
    newAudit.customer = sender.customer
    newAuditTx = Audit_Tx()
    newAudit.save()
    newAuditTx.audit = newAudit
    newAuditTx.origin_customer_id = sender.customer.id
    newAuditTx.destination_customer_id = receiver.customer.id
    newAuditTx.origin_acc = sender
    newAuditTx.destination_acc = receiver
    newAuditTx.amount = amount
    newAuditTx.save()

def generate_validation_token(length: int):
    return binascii.hexlify(urandom(length // 2)).decode()

def alias_regex(alias: str) -> bool:
    # Pattern to match three words (alphanumeric or alphabetic) separated by periods, with total length between 6 and 20
    pattern = r'^(?=.{6,20}$)([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)$'
    match = search(pattern, alias)
    return True if match else False

def convertToDecimal(amount):
    match len(amount):
        case 1:
            return Decimal("0.0"+amount)
        case 2:
            return Decimal("0."+amount)
        case _:
            decimals = amount[-2:]
            number = amount[:-2]
            return Decimal(number + '.' + decimals)
