import decimal
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import migrations

from applications.users.models import Customer, Customer_Type, Marital_Status, Funds_Source, Profession, Tax_Situation
from applications.wallet.models import Wallet

from django.utils import timezone

def initial_seed(apps, schema_editor):

    customer_type = Customer_Type.objects.filter(name='Persona Fisica').first()
    marital_status = Marital_Status.objects.filter(name='Soltero').first()
    funds_source = Funds_Source.objects.filter(name='Salario/Ahorro').first()
    profession = Profession.objects.filter(name='Autónomo').first()
    tax_situation = Tax_Situation.objects.filter(name='Relación de Dependencia').first()

    # SEED TEST CUSTOMER AND WALLET
    newCustomer = Customer()
    newCustomer.email = 'test@test.com'
    newCustomer.name = 'Juan Ignacio'
    newCustomer.last_name = 'Perez'
    newCustomer.full_name = 'Juan Ignacio Perez'
    newCustomer.password = 'test'
    newCustomer.customer_type = customer_type
    newCustomer.phone_number = '1111222333'
    newCustomer.cuit = '00123456789'
    newCustomer.birth_date = datetime(1990, 1, 1)
    newCustomer.marital_status = marital_status
    newCustomer.funds_source = funds_source
    newCustomer.profession = profession
    newCustomer.tax_situation = tax_situation
    newCustomer.is_active = True
    newCustomer.save()
    UserModel = get_user_model()
    user = UserModel.objects.create_user('test@test.com', email='test@test.com', password='test')
    user.is_superuser = False
    user.is_staff = False
    user.last_login = timezone.now()

    newWallet = Wallet()
    newWallet.customer = newCustomer
    newWallet.cvu = '0004572600012345678907'
    newWallet.alias = 'hoja.pieda.leon'
    newWallet.balance = decimal.Decimal('1000000.00')
    newWallet.bank_name = "ECashFlow"
    newWallet.save()

    user.save()

    # SEED TEST CUSTOMER 2 AND WALLET
    newCustomer2 = Customer()
    newCustomer2.email = 'test2@test.com'
    newCustomer2.name = 'Ricardo'
    newCustomer2.last_name = 'Urquidiz'
    newCustomer2.full_name = 'Ricardo Urquidiz'
    newCustomer2.password = 'test'
    newCustomer2.customer_type = customer_type
    newCustomer2.phone_number = '1111222334'
    newCustomer2.cuit = '01123456789'
    newCustomer2.birth_date = datetime(1990, 1, 1)
    newCustomer2.marital_status = marital_status
    newCustomer2.funds_source = funds_source
    newCustomer2.profession = profession
    newCustomer2.tax_situation = tax_situation
    newCustomer2.is_active = True
    newCustomer2.save()
    UserModel = get_user_model()
    user2 = UserModel.objects.create_user('test2@test.com', email='test2@test.com', password='test')
    user2.is_superuser = False
    user2.is_staff = False
    user2.last_login = timezone.now()

    newWallet2 = Wallet()
    newWallet2.customer = newCustomer2
    newWallet2.cvu = '0004572600112345678900'
    newWallet2.alias = 'marc.sueno.flor'
    newWallet2.balance = decimal.Decimal('1000000.00')
    newWallet2.bank_name = "ECashFlow"
    newWallet2.save()

    user2.save()

    # SEED TEST CUSTOMER 3 AND WALLET
    newCustomer3 = Customer()
    newCustomer3.email = 'test3@test.com'
    newCustomer3.name = 'Maximiliano'
    newCustomer3.last_name = 'Martinez'
    newCustomer3.full_name = 'Maximiliano Martinez'
    newCustomer3.password = 'test'
    newCustomer3.customer_type = customer_type
    newCustomer3.phone_number = '1111222335'
    newCustomer3.cuit = '01213456789'
    newCustomer3.birth_date = datetime(1990, 1, 1)
    newCustomer3.marital_status = marital_status
    newCustomer3.funds_source = funds_source
    newCustomer3.profession = profession
    newCustomer3.tax_situation = tax_situation
    newCustomer3.is_active = True
    newCustomer3.save()
    UserModel = get_user_model()
    user3 = UserModel.objects.create_user('test3@test.com', email='test3@test.com', password='test')
    user3.is_superuser = False
    user3.is_staff = False
    user3.last_login = timezone.now()

    newWallet3 = Wallet()
    newWallet3.customer = newCustomer3
    newWallet3.cvu = '0004572670121345678902'
    newWallet3.alias = 'carro.barro.flor'
    newWallet3.balance = decimal.Decimal('1000000.00')
    newWallet3.bank_name = "ECashFlow"
    newWallet3.save()

    user3.save()

    # SEED TEST CUSTOMER 4 AND WALLET
    newCustomer4 = Customer()
    newCustomer4.email = 'test4@test.com'
    newCustomer4.name = 'Joaquín'
    newCustomer4.last_name = 'Colomar'
    newCustomer4.full_name = 'Joaquín Colomar'
    newCustomer4.password = 'test'
    newCustomer4.customer_type = customer_type
    newCustomer4.phone_number = '1111222336'
    newCustomer4.cuit = '01123546789'
    newCustomer4.birth_date = datetime(1990, 1, 1)
    newCustomer4.marital_status = marital_status
    newCustomer4.funds_source = funds_source
    newCustomer4.profession = profession
    newCustomer4.tax_situation = tax_situation
    newCustomer4.is_active = True
    newCustomer4.save()
    UserModel = get_user_model()
    user4 = UserModel.objects.create_user('test4@test.com', email='test4@test.com', password='test')
    user4.is_superuser = False
    user4.is_staff = False
    user4.last_login = timezone.now()

    newWallet4 = Wallet()
    newWallet4.customer = newCustomer4
    newWallet4.cvu = '0004572610112354678904'
    newWallet4.alias = 'perro.sueno.gato'
    newWallet4.balance = decimal.Decimal('1000000.00')
    newWallet4.bank_name = "ECashFlow"
    newWallet4.save()

    user4.save()

    # SEED TEST CUSTOMER 5 AND WALLET
    newCustomer5 = Customer()
    newCustomer5.email = 'test5@test.com'
    newCustomer5.name = 'Jorge Pedro'
    newCustomer5.last_name = 'Gómez'
    newCustomer5.full_name = 'Jorge Pedro Gómez'
    newCustomer5.password = 'test'
    newCustomer5.customer_type = customer_type
    newCustomer5.phone_number = '1111222337'
    newCustomer5.cuit = '01123457786'
    newCustomer5.birth_date = datetime(1990, 1, 1)
    newCustomer5.marital_status = marital_status
    newCustomer5.funds_source = funds_source
    newCustomer5.profession = profession
    newCustomer5.tax_situation = tax_situation
    newCustomer5.is_active = True
    newCustomer5.save()
    UserModel = get_user_model()
    user5 = UserModel.objects.create_user('test5@test.com', email='test5@test.com', password='test')
    user5.is_superuser = False
    user5.is_staff = False
    user5.last_login = timezone.now()

    newWallet5 = Wallet()
    newWallet5.customer = newCustomer5
    newWallet5.cvu = '0004572610112345778605'
    newWallet5.alias = 'bote.carro.flor'
    newWallet5.balance = decimal.Decimal('1000000.00')
    newWallet5.bank_name = "ECashFlow"
    newWallet5.save()

    user5.save()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_seed_data'),
        ('wallet', '0001_initial'),
        ('auth', '0005_alter_user_last_login_null')
    ]

    operations = [
        migrations.RunPython(initial_seed),
    ]