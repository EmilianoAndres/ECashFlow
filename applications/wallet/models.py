from django.db import models
from django.utils import timezone
from ..users.models import Customer
from ..vendors.models import Vendor


# Create your models here.
class Wallet(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)
    cvu = models.CharField(max_length=22)
    alias = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Update the updated_date field whenever the model instance is saved
        self.updated_date = timezone.now()
        super(Wallet, self).save(*args, **kwargs)

class EscrowWallet(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=False)
    cvu = models.CharField(max_length=22)
    alias = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

class Contact(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=False)
    is_favorite = models.BooleanField(default = False)
    is_own_bank_acc = models.BooleanField(default = False)
    

class Deposit(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=False)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    token = models.CharField(max_length=50)
    is_used = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Update the updated_date field whenever the model instance is saved
        self.updated_date = timezone.now()
        super(Deposit, self).save(*args, **kwargs)
