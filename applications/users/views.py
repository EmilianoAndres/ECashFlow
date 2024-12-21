import binascii
import os
from datetime import datetime
from types import SimpleNamespace

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import redirect

from .forms import CustomerForm
from applications.wallet.models import Wallet
from django.contrib import messages # type: ignore


from applications.home.views import Home
from django.contrib.auth import logout 

from .models import Customer, CustomerDataChange, CustomerRegister
from applications.wallet.models import Contact
from django.db.models import Q

from ..administrators.models import Administrator
from ..administrators.views import AdminDashboard
from ..const import NUMERO_DE_SUCURSAL_ECASHFLOW, NUMERO_DE_SUCURSAL_BANCO, NUMERO_DE_ENTIDAD_VIRTUAL, \
    NUMERO_DE_ENTIDAD_BANCARIA, NOMBRE_BANCO_FICTICIO, NOMBRE_BANCO_ECASHFLOW
from ..documents.forms import DocumentForm
from ..helpers import cuenta_unica_generator, alias_generator, createUserActivityAudit

import decimal
from random import uniform, randint

from django.core.mail import send_mail

from PIL import Image
from pdf417decoder import PDF417Decoder

import logging

import re


# Create your views here.

def clear_messages(request):
    storage = messages.get_messages(request)
    storage.used = True


def UploadDni(request):
    clear_messages(request)
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            validated, error, token = handle_uploaded_dni(request.FILES["file"])
            if not validated:
                messages.add_message(request, messages.ERROR, error)
                return render(request, "users/upload_dni.html", {"form": form})
            messages.add_message(request, messages.INFO, "Tu DNI fue validado! Por favor, llená el resto de tu información.")
            form = CustomerForm()
            return render(request, "users/register.html", {"token": token, "form": form})
        pass
    form = DocumentForm()
    return render(request, "users/upload_dni.html", {"form": form})


def Register(request):
    clear_messages(request)
    if request.user.is_authenticated:
        return redirect(Home)
    
    if request.method == "POST":
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            token = request.POST.get('token')
            register_record = CustomerRegister.objects.filter(Q(validation_token=token) & Q(is_validated=False)).first()
            if register_record is None:
                messages.add_message(request, messages.ERROR,
                                     "Hubo un error al completar el registro. Por favor, intenta nuevamente.")
                return redirect(Home)
            cuit = register_record.cuit
            register_record.is_validated = True
            password = request.POST.get('password')
            email = request.POST.get('email')
            newWallet = Wallet()
            existing_user = User.objects.filter(username=email)
            if len(existing_user) != 0:
                messages.add_message(request, messages.ERROR, 'Hubo un error al completar el registro. Por favor, intenta nuevamente.')
                return render(request, "users/register.html", {"form": form})
            user = User.objects.create_user(email,
                                            email,
                                            password)
            user.save()
            cvu = cuenta_unica_generator(NUMERO_DE_SUCURSAL_ECASHFLOW, cuit+'0', True)
            newWallet.cvu = cvu
            newAlias = alias_generator()
            while Wallet.objects.filter(alias=newAlias).exists():
                newAlias = alias_generator()
            newWallet.alias = newAlias
            newWallet.bank_name = NOMBRE_BANCO_ECASHFLOW
            customer = form.save(commit=False)
            # we need password to be in the customer model for the form to work,
            # but it's stored as plain text so we ought to remove it from this model
            customer.password = ''
            customer.cuit = cuit
            customer.name = register_record.name
            customer.last_name = register_record.last_name
            customer.full_name = register_record.name + ' ' + register_record.last_name
            customer.birth_date = register_record.birth_date
            customer.save()
            newWallet.customer_id = customer.id
            newWallet.save()
            messages.add_message(request, messages.INFO, "Te Registraste exitosamente! Por favor, loguéate para utilizar la aplicación.")
            return redirect("Login")
        messages.add_message(request, messages.ERROR, "El formulario no es válido.")
    form = CustomerForm()

    return render(request, "users/register.html", {"form": form})


def Login(request):
    clear_messages(request)
    if request.user.is_authenticated:
        return redirect(Home)

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            admin = Administrator.objects.filter(email=username).first()
            if admin is not None:
                messages.add_message(request, messages.INFO, f"Bienvenido Administrador: {username}")
                login(request, user)
                return redirect(AdminDashboard)
            customer = Customer.objects.get(email=user.email)
            if not customer.is_active:
                messages.add_message(request, messages.ERROR, "Ocurrió un problema. Contáctese con soporte.")
                return render(request, "users/login.html")
            wallets = Wallet.objects.filter(customer=customer)
            wallet = wallets.filter(cvu__startswith=NUMERO_DE_ENTIDAD_VIRTUAL).first()
            bankAcc = wallets.filter(cvu__startswith=NUMERO_DE_ENTIDAD_BANCARIA).first()
            if bankAcc is not None:
                request.session['hasBankAccount'] = True
            login(request, user)
            request.session['userBalance'] = str(wallet.balance)
            return redirect(Home)
        
        messages.add_message(request, messages.ERROR, "Credenciales Inválidas")
        return render(request, "users/login.html")
    
    return render(request, "users/login.html")

def Logout(request):
    logout(request)
    return redirect("Login")

def ForgotPasswordChange(request):
    clear_messages(request)

    if request.method == "POST":
        token = request.POST.get('token', 'default')
        existingToken = CustomerDataChange.objects.filter(Q(validation_token=token) & Q(is_validated=False)).first()
        if existingToken is None:
            email = request.POST.get('email')
            if email is not None:
                existingCustomer = Customer.objects.filter(email=email).first()
                if existingCustomer is not None:
                    forgotCustomerPassword(email)
            messages.add_message(request, messages.INFO,
                                 "Hemos enviado un Email para iniciar el cambio de contraseña.")
            return render(request, 'users/password_forget.html')

        email = request.POST.get('email')
        newPassword = request.POST.get('new-password')
        if newPassword is not None:
            if email is None:
                messages.add_message(request, messages.ERROR,
                                     "Hubo un error con el cambio de contraseña. Por favor, intenta nuevamente.")
                return redirect(Home)
            existingCustomer = Customer.objects.filter(email=email).first()
            if existingCustomer is None:
                messages.add_message(request, messages.ERROR,
                                     "Hubo un error con el cambio de contraseña. Por favor, intenta nuevamente.")
                return redirect(Home)
            user = User.objects.filter(email=email).first()
            user.set_password(newPassword)
            user.save()
            existingToken.is_validated = True
            existingToken.save()
            messages.add_message(request, messages.INFO,
                                 "Has cambiado tu contraseña exitosamente! Por favor, logueate.")
            return redirect(Home)

        return render(request, "users/password_forget.html")

    token = request.GET.get('token', 'default')
    existingToken = CustomerDataChange.objects.filter(Q(validation_token=token) & Q(is_validated=False)).first()
    if existingToken is None:
        return render(request, 'users/password_forget.html')

    return render(request, 'users/password_forget.html', {"tokenValidated": True})

def UpdatePassword(request):
    clear_messages(request)
    if not request.user.is_authenticated:
        return redirect(Login)

    customer = Customer.objects.filter(email=request.user.email).first()
    if customer is not None:
        updateCustomerPassword(customer.email)
        messages.add_message(request, messages.INFO, "Te hemos enviado un mail con los pasos para cambiar tu contraseña.")

    return redirect(Dashboard)

def ChangePassword(request):
    clear_messages(request)
    if not request.user.is_authenticated:
        return redirect(Login)

    if request.method == "POST":
        token = request.POST.get('token', 'default')
        existingToken = CustomerDataChange.objects.filter(Q(validation_token=token) & Q(is_validated=False)).first()
        if existingToken is None:
            messages.add_message(request, messages.ERROR,
                                 "Hubo un error al intentar cambiar la contraseña. Intenta Nuevamente.")
            return redirect(Home)
        oldPassword = request.POST.get("old-password")
        newPassword = request.POST.get("new-password")
        existingUser = User.objects.filter(email=request.user.email).first()
        if not existingUser.check_password(oldPassword):
            messages.add_message(request, messages.ERROR,
                                 "Hubo un error al intentar cambiar la contraseña. Intenta Nuevamente.")
            return redirect(Home)
        existingUser.set_password(newPassword)
        existingUser.save()
        existingToken.is_validated=True
        existingToken.save()
        messages.add_message(request, messages.INFO,
                             "Has cambiado tu contraseña exitosamente! Por favor, vuelve a loguearte")
        logout(request)
        return redirect(Home)

    token = request.GET.get('token', 'default')
    existingToken = CustomerDataChange.objects.filter(Q(validation_token=token) & Q(is_validated=False)).first()
    if existingToken is None:
        return redirect(Home)

    return render(request, "users/password_change.html")
def UpdateEmail(request):
    clear_messages(request)
    if not request.user.is_authenticated:
        return redirect(Login)

    customer = Customer.objects.get(email=request.user.email)

    if request.method == "POST":
        newEmail = request.POST.get("email")
        existingUser = User.objects.filter(email=newEmail).first()
        if existingUser is None:
            oldEmail = request.user.email
            updateCustomerEmail(oldEmail, newEmail)
        messages.add_message(request, messages.INFO, "Te hemos enviado un correo con un link para finalizar tu cambio de email")
        return redirect(UpdateEmail)

    return render(request, "users/email_change.html", {"email": customer.email})
def Dashboard(request):
    clear_messages(request)
    if not request.user.is_authenticated:
        return redirect(Login)

    if request.method == "POST":
        newEmail = request.POST.get("email")
        existingUser = User.objects.filter(email=newEmail).first()
        if existingUser is None:
            oldEmail = request.user.email
            updateCustomerEmail(oldEmail, newEmail)
        messages.add_message(request, messages.INFO, "Te hemos enviado un correo con un link para finalizar tu cambio de email")
        return redirect(Dashboard)

    customer = Customer.objects.get(email = request.user.email)
    wallet = Wallet.objects.get(Q(customer=customer) & Q(cvu__startswith=NUMERO_DE_ENTIDAD_VIRTUAL))
    customerWithAlias = SimpleNamespace(customer=customer, alias=wallet.alias, cvu=wallet.cvu)
    return render(request, 'users/dashboard.html', {"customerWithAlias": customerWithAlias, "customerFullName": customer.name +" "+customer.last_name})

def Contact_list(request):
    clear_messages(request)
    customer = Customer.objects.filter(email = request.user.email).first()
    loggedUserContacts = Contact.objects.filter(customer=customer)
    favorites = loggedUserContacts.filter(is_favorite=True)
    return render(request, 'users/contactlist.html', {"contacts": loggedUserContacts, "favorites":favorites})

def add_contact(request):
    if not request.user.is_authenticated:
        return redirect(Login)
    
    clear_messages(request)
    if request.method == 'POST':
        search_query: str = request.POST.get('contactData')
        if not search_query:
            return redirect("AddContact")
        
        if ((str.isnumeric(search_query)
             and len(search_query) == 22 )
                or alias_regex(search_query)):
            walletContact = Wallet.objects.filter(Q(cvu=search_query) | Q(alias=search_query))
            
            if len(walletContact) != 1:
                errorContact = "No pudimos encontrar un usuario con ese nombre."
                messages.add_message(request, messages.ERROR, errorContact)
                return redirect('AddContact')
            existingContact = Contact.objects.filter(wallet__in=walletContact).first()
            
            if existingContact is None:
                loggedCustomer = Customer.objects.filter(email=request.user.email).first()

                # check for own savings account
                if walletContact.filter(Q(cvu__startswith=NUMERO_DE_ENTIDAD_BANCARIA) & Q(customer=loggedCustomer)):
                    Contact.objects.create(
                        customer=Customer.objects.filter(email=request.user.email)[0],
                        wallet=walletContact[0],
                        is_own_bank_acc=True
                    )
                    return redirect('ContactList')

                if walletContact[0].customer.id != loggedCustomer.id:
                    Contact.objects.create(
                        customer=Customer.objects.filter(email=request.user.email)[0],
                        wallet=walletContact[0]
                    )
                    return redirect('ContactList')
                else:
                    errorContact = "No te podés agregar a vos mismo."
                    messages.add_message(request, messages.ERROR, errorContact)
                    return redirect('AddContact')
            else:
                errorContact = "Este contacto ya existe."
                messages.add_message(request, messages.ERROR, errorContact)
                return redirect('AddContact')          
        else:
            errorContact = "Input inválido."
            messages.add_message(request, messages.ERROR, errorContact)
            return redirect('AddContact')

    return render(request, 'users/add_contact.html')


def delete_contact(request, contact_id):
    Contact.objects.filter(id = contact_id).delete()

    return redirect('ContactList')

def AddFavorite(request, contact_id):
    Contact.objects.filter(id = contact_id, is_favorite = False).update(is_favorite= True)

    return redirect('ContactList')

def DeleteFavorite(request,contact_id):
    Contact.objects.filter(id = contact_id, is_favorite = True).update(is_favorite = False)
    
    return redirect('ContactList')

def CreateBankAccount(request):
    if not request.user.is_authenticated:
        return redirect(Login)
    clear_messages(request)
    customer = Customer.objects.get(email=request.user.email)
    modifiedCuit = customer.cuit + "0"
    accounts = range(randint(1, 3))
    cbus = set()
    for _ in accounts:
        cbu = cuenta_unica_generator(NUMERO_DE_SUCURSAL_BANCO, modifiedCuit, False)
        cbus.add(cbu)
        while cbu in cbus:
            cbu = cuenta_unica_generator(NUMERO_DE_SUCURSAL_BANCO, modifiedCuit, False)
        newWallet = Wallet()
        newWallet.cvu = cbu
        newWallet.alias = alias_generator()
        newWallet.customer_id = customer.id
        newWallet.bank_name = NOMBRE_BANCO_FICTICIO
        newWallet.balance = decimal.Decimal(uniform(10000, 49999))
        newWallet.save()
        logging.info(
            f"successfully created a bank account with cbu: {newWallet.cvu} for user {customer.email} with amount: ${newWallet.balance}")
    request.session['hasBankAccount'] = True
    messages.add_message(request, messages.INFO, "Asociaste exitosamente tus Cajas de Ahorro!")
    return redirect(Home)

def BankAccount(request):
    if not request.user.is_authenticated:
        return redirect(Login)
    clear_messages(request)
    customer = Customer.objects.get(email=request.user.email)
    bankAccs = Wallet.objects.filter(Q(customer=customer) & Q(cvu__startswith= "011"))
    if bankAccs is None:
        logging.INFO(f"No pudimos encontrar una cuenta bancaria para el usuario con email: {customer.email}")
    accounts = []
    for element in bankAccs:
        obj = SimpleNamespace(customer=customer.email, balance=element.balance, cuit=customer.cuit, cbu=element.cvu, alias=element.alias)
        accounts.append(obj)
    return render(request, 'BankAccount/BankAccountBase.html', {"bankAccs": accounts})

def ValidateEmail(request):
    clear_messages(request)
    if not request.user.is_authenticated:
        return redirect(Login)
    token = request.GET.get('token', 'default')
    customer = Customer.objects.get(email=request.user.email)
    validatedEmail = validateTokenAndReturnValue(token, customer)
    if len(validatedEmail) == 0:
        return redirect(Home)
    user = User.objects.get(email=request.user.email)
    user.username = validatedEmail
    user.email = validatedEmail
    customer.email = validatedEmail
    customer.save()
    user.save()
    createUserActivityAudit("Email", customer)
    return render(request, 'validations/validatedEmail.html')

def forgotCustomerPassword(email:str):
    token = generate_validation_token(50)
    send_mail(
        "Cambio de Contraseña para tu cuenta ECashFlow",
        "Alguien solicitó un cambio de contraseña para tu cuenta ECashFlow. "
        " Hacé click en el siguiente link para cambiar tu contraseña: \n"
        "https://ecashflow.online/forgot-password?email="+ email + "&" + "token=" + token,
        "ecashflow@gmail.com",
        [email],
        fail_silently=False,
    )
    customer = Customer.objects.get(email=email)
    newPasswordDataChange = CustomerDataChange()
    newPasswordDataChange.customer = customer
    newPasswordDataChange.field_changed = "PASSWORD"
    newPasswordDataChange.validation_token = token
    newPasswordDataChange.save()

def updateCustomerPassword(email:str):
    token = generate_validation_token(50)
    send_mail(
        "Validá tu nuevo Email en ECashFlow",
        "Alguien solicitó un cambio de contraseña para tu cuenta ECashFlow. "
        " Hacé click en el siguiente link para cambiar tu contraseña: \n"
        "https://ecashflow.online/change-password?token=" + token,
        "ecashflow@gmail.com",
        [email],
        fail_silently=False,
    )
    customer = Customer.objects.get(email=email)
    newPasswordDataChange = CustomerDataChange()
    newPasswordDataChange.customer = customer
    newPasswordDataChange.field_changed = "PASSWORD"
    newPasswordDataChange.validation_token = token
    newPasswordDataChange.save()

def updateCustomerEmail(oldEmail: str, newEmail: str):
    token = generate_validation_token(50)
    send_mail(
    "Validá tu nuevo Email en ECashFlow",
    "Alguien solicitó un cambio de email para tu cuenta ECashFlow. "
    " Hacé click en el siguiente link para finalizar el cambio: \n"
    "https://ecashflow.online/validateEmail?token=" + token,
    "ecashflow@gmail.com",
    [newEmail],
    fail_silently=False,
    )
    send_mail(
        "Alguien inició un cambio de Email en tu cuenta de ECashFlow",
        "Si fuiste vos, desestimá este Email. De lo contrario, ponete en contacto con nosotros"
        " para ayudarte a revertir este cambio.",
        "ecashflow@gmail.com",
        [oldEmail],
        fail_silently=False,
    )
    customer = Customer.objects.get(email=oldEmail)
    newEmailDataChange = CustomerDataChange()
    newEmailDataChange.customer = customer
    newEmailDataChange.field_changed = "EMAIL"
    newEmailDataChange.field_value = newEmail
    newEmailDataChange.validation_token = token
    newEmailDataChange.save()

def validatePhoneNumber(phone_number: str) -> str | None:
    length = len(phone_number)
    if length != 10:
        return "Número de teléfono debe tener 10 dígitos de longitud"
    for i in range(length):
        if not phone_number[i].isdigit():
            return "Número de teléfono solo debe tener dígitos"
    return None

def validateTokenAndReturnValue(token: str, customer: Customer) -> str:
    dataChangeRequest = CustomerDataChange.objects.filter(Q(validation_token = token) & Q(is_validated=False))
    if len(dataChangeRequest) != 1:
        return ""
    if dataChangeRequest[0].customer != customer:
        return ""
    dataChangeRequest[0].is_validated=True
    dataChangeRequest[0].save()
    return dataChangeRequest[0].field_value

def generate_validation_token(length: int):
    return binascii.hexlify(os.urandom(length // 2)).decode()

def alias_regex(alias: str) -> bool:
    # Pattern to match three words (alphanumeric or alphabetic) separated by periods, with total length between 6 and 20
    pattern = r'^(?=.{6,20}$)([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)$'
    match = re.search(pattern, alias)
    return True if match else False

def handle_uploaded_dni(file) -> (bool, str, str):
    image = Image.open(file)
    decoder = PDF417Decoder(image)

    if (decoder.decode() > 0):
        decoded = decoder.barcode_data_index_to_string(0)
        if decoded.count('@') != 8:
            return False, 'El DNI no pudo ser leído. Intente nuevamente.', ""
        dni_info = decoded.split('@')
        issue_date = dni_info[7].split('/')
        issue_datetime = datetime(int(issue_date[2]), int(issue_date[1]), int(issue_date[0]))
        if datetime.now() > issue_datetime.replace(year=issue_datetime.year + 15):
            return False, 'El DNI se encuentra vencido.', ""
        last_name = dni_info[1]
        name = dni_info[2]
        sex = dni_info[3]
        dni = dni_info[4]
        birth_date = dni_info[6].split('/')
        birth_datetime = datetime(int(birth_date[2]), int(birth_date[1]), int(birth_date[0]))
        if birth_datetime.replace(year=birth_datetime.year + 13) > datetime.now():
            return False, 'El usuario no se puede registrar ya que es menor a 13 años de edad.', ""

        cuit_number_back = dni_info[8][2]
        cuit_number_front = dni_info[8][0]+dni_info[8][1]

        cuit = cuit_number_front+dni+cuit_number_back

        if Customer.objects.filter(cuit=cuit).exists():
            return False, 'El DNI no pudo ser leído. Intente nuevamente.', ""

        token = generate_validation_token(50)

        register = CustomerRegister()
        register.name = name
        register.last_name = last_name
        register.birth_date = birth_datetime
        register.cuit = cuit
        register.validation_token = token

        register.save()

        return True, "", token
    return False, 'El DNI no pudo ser leído. Intente nuevamente.', ""