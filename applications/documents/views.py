import io
from io import StringIO
from sqlite3 import IntegrityError
from types import SimpleNamespace

from django.core.mail import send_mail, EmailMessage
from django.db.transaction import atomic
from django.shortcuts import render, redirect
from pyexpat.errors import messages

from .forms import DocumentForm
from pyzbar.pyzbar import decode
from PIL import Image
from django.contrib import messages

from ..audit.models import Audit_Tx, Audit
from ..users.models import Customer
from ..vendors.models import VendorPayment, Vendor

from datetime import datetime

from django.db.models import Q

from ..wallet.models import Wallet, EscrowWallet

from applications.home.views import Home

from decimal import Decimal

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Create your views here.

def clear_messages(request):
    storage = messages.get_messages(request)
    storage.used = True

vendorListCodes = Vendor.objects.all().values_list('code', flat=True)

def UploadBarcode(request):
    clear_messages(request)
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        print("here")
        if form.is_valid():
            print("her2")
            barcodeInfo = handle_uploaded_file(request.FILES["file"])
            if barcodeInfo[0]:
                vendor = Vendor.objects.filter(code=barcodeInfo[1][0]).first()
                customer = Customer.objects.filter(email=request.user.email).first()
                if vendor is None:
                    messages.add_message(request, messages.ERROR, "No pudimos encontrar un prestador de utilidades asociado")
                    return render(request, "documents/uploadBarcode.html")
                dueDate = datetime.strptime(barcodeInfo[1][2], '%d%m%y')
                if datetime.now() >= dueDate:
                    messages.add_message(request, messages.ERROR, "La boleta está vencida")
                    return render(request, "documents/uploadBarcode.html")
                paymentNumber = barcodeInfo[1][1]
                amount = barcodeInfo[1][3]
                decimals = amount[-2] + amount[-1]
                amount = amount[:-2]
                finalAmount = amount + '.' + decimals
                existingPayment = VendorPayment.objects.filter(Q(vendor=vendor) & Q(payment_number=paymentNumber)).first()
                if existingPayment is not None:
                    if not existingPayment.is_active:
                        obj = SimpleNamespace(vendor=vendor.name, paymentNumber=paymentNumber,
                                              duedate=dueDate.strftime("%d/%m/%y"), amount=finalAmount)
                        return render(request, 'documents/createpayment.html', {'paymentInfo': obj})
                    else:
                        messages.add_message(request, messages.ERROR, "Ya hemos enviado este pago a aprobación.")
                        return redirect(Home)
                SavePayment(vendor, customer, paymentNumber, dueDate, finalAmount)
                obj = SimpleNamespace(vendor=vendor.name, paymentNumber=barcodeInfo[1][1], duedate=dueDate.strftime("%d/%m/%y"), amount=finalAmount)
                return render(request, 'documents/createpayment.html', {'paymentInfo': obj})
            messages.add_message(request, messages.ERROR, "No pudimos encontrar un prestador de utilidades asociado")
            return render(request, "documents/uploadBarcode.html")
    form = DocumentForm()
    return render(request, "documents/uploadBarcode.html", {"form": form})

def CreatePayment(request):
    clear_messages(request)
    if request.method == "POST":
        vendorName = request.POST.get('vendor')
        paymentNumber = request.POST.get('paymentNumber')
        customer = Customer.objects.filter(email=request.user.email).first()
        existingPayment = VendorPayment.objects.filter(Q(vendor__name=vendorName) & Q(payment_number=paymentNumber)).first()
        if existingPayment is None:
            messages.add_message(request, messages.ERROR, "Hubo un error procesando la solicitud. Prueba nuevamente más tarde")
            return redirect(Home)
        if not existingPayment.is_active:
            success = ExecutePayment(request, customer, existingPayment)
            if not success:
                return redirect(Home)
        wallet = Wallet.objects.filter(customer=customer).first()
        buffer = buildDocumentVendorPayment(wallet, existingPayment)
        sendEmailVendorPayment(request.user.email, buffer)
        messages.add_message(request, messages.INFO, "Hemos enviado tu pago para ser aprobado")
        return redirect(Home)
    return redirect(Home)

def SavePayment(vendor, customer, payment_number, due_date, amount) -> bool:
    newVendorPayment = VendorPayment()
    newVendorPayment.vendor = vendor
    newVendorPayment.customer = customer
    newVendorPayment.payment_number = payment_number
    newVendorPayment.due_date = due_date
    try:
        decimalAmount = Decimal(amount)
    except ValueError:
        return False
    newVendorPayment.amount = decimalAmount
    try:
        newVendorPayment.save()
    except IntegrityError:
        return False
    return True

@atomic
def ExecutePayment(request, customer: Customer, payment: VendorPayment) -> bool:
    wallet = Wallet.objects.filter(customer=customer).first()
    vendorWallet = EscrowWallet.objects.filter(vendor=payment.vendor).first()
    if wallet.balance < payment.amount:
        messages.add_message(request, messages.ERROR, "Not enough funds. Payment can not be processed")
        return False
    wallet.balance -= payment.amount
    vendorWallet.balance += payment.amount
    wallet.save()
    vendorWallet.save()
    newAudit = Audit(customer=customer)
    newAuditTx = Audit_Tx(audit=newAudit)
    newAuditTx.origin_customer = customer
    newAuditTx.origin_acc = wallet
    newAuditTx.destination_vendor = payment.vendor
    newAuditTx.amount = payment.amount
    payment.is_active = True
    newAudit.save()
    newAuditTx.save()
    payment.save()
    return True


def handle_uploaded_file(file) -> (bool, list[str]):
    try:
        result = decode(Image.open(file))
    except:
        return False, []
    if result is not None:
        barcode = result[0].data
        barcodeString = barcode.decode("utf-8")
        print(barcodeString)
        for key in vendorListCodes:
            if barcodeString.startswith(key):
                paymentNumber = barcodeString[7:15]
                start = barcodeString.find('000000')
                duedate = barcodeString[start - 6:start]
                print(f'vencimiento: {duedate}')
                start += 6
                rest = barcodeString[start:]
                amount = rest[:rest.index("00")]
                amount += '0'
                print(f'monto: {amount}')
                return True, [key, paymentNumber, duedate, amount]
    return False, ['']

def buildDocumentVendorPayment(wallet: Wallet, existingPayment: VendorPayment):
    buffer = io.BytesIO()
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # margins
    margin_left = 50
    margin_right = 50
    margin_top = 50
    margin_bottom = 50

    text_y = height - margin_top

    text_object = p.beginText(margin_left, text_y)
    text_object.setFont("Helvetica", 12)

    content = f"""Hola desde ECashFlow!

    Has realizado un pago exitoso desde tu billetera ECashFlow:
    {wallet.cvu}
    Para {existingPayment.vendor.name}, un proveedor de {existingPayment.vendor.vendor_type.name}
    por ${existingPayment.amount} pesos.
    
    Gracias por utilizar ECashFlow!"""

    for line in content.splitlines():
        # Handle line wrapping
        for word in line.split(' '):
            if text_object.getX() + p.stringWidth(word + ' ', "Helvetica", 12) > (width - margin_right):
                text_object.textLine()  # Go to the next line
            text_object.textOut(word + ' ')  # Add the word to the text object

        text_object.textLine()  # Add a line break at the end of the line

    p.drawText(text_object)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def sendEmailVendorPayment(email: str, buffer):
    email = EmailMessage("Has realizado un pago exitoso desde tu billetera ECashFlow!",
                            "Ver archivo adjunto para más detalles.",
                            'ecashflow@gmail.com',
                            [email])
    email.attach('invoice.pdf', buffer.read(), 'application/pdf')
    email.send()