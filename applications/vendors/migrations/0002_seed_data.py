from django.db import models, migrations

from applications.vendors.models import VendorType, Vendor
from applications.wallet.models import EscrowWallet


def initial_seed(apps, schema_editor):

    # SEED Vendor Types
    vendor_type_1 = VendorType()
    vendor_type_1.name = 'Utilities'
    vendor_type_1.save()

    # SEED Vendor
    vendor_1 = Vendor()
    vendor_1.vendor_type = vendor_type_1
    vendor_1.code = '2400006'
    vendor_1.name = 'EPEC'
    vendor_1.cuit = '30999027489'
    vendor_1.holder_name = 'EMPRESA PROVINCIAL DE ENERGIA DE CORDOBA'
    vendor_1.save()

    # SEED Vendor EscrowWallet
    wallet_1 = EscrowWallet()
    wallet_1.vendor = vendor_1
    wallet_1.cvu = '0005234603099902748902'
    wallet_1.alias = 'pato.nieve.hoja'
    wallet_1.save()

class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0001_initial')
    ]

    operations = [
        migrations.RunPython(initial_seed),
    ]