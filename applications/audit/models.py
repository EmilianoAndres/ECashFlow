from uuid import uuid4

from django.utils import timezone

from django.db import models
from django.db.models import DecimalField, BooleanField

from applications.users.models import Customer
from applications.vendors.models import Vendor
from applications.wallet.models import Wallet


# Create your models here.

class Audit(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Update the updated_date field only if the instance already exists (i.e., it's not a new instance)
        self.updated_date = timezone.now()
        super(Audit, self).save(*args, **kwargs)

class Audit_Deposit(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, null=False)
    unique_id = models.UUIDField(default=uuid4, editable=False, unique=True)
    amount = DecimalField(max_digits=18, decimal_places=2, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class Audit_Tx(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, null=False)
    unique_id = models.UUIDField(default=uuid4, editable=False, unique=True)
    origin_acc = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=False, related_name="origin_account")
    destination_acc = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=True, related_name="destination_account")
    destination_customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name="destination_customer")
    destination_vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="destination_vendor")
    amount = DecimalField(max_digits=18, decimal_places=2, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Update the updated_date field whenever the model instance is saved
        self.updated_date = timezone.now()
        super(Audit_Tx, self).save(*args, **kwargs)

class Audit_UserActivity(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, null=False)
    unique_id = models.UUIDField(default=uuid4, editable=False, unique=True)
    emailChanged = BooleanField(null=False, default=False)
    passwordChanged = BooleanField(null=False, default=False)
    phoneNumberChanged = BooleanField(null=False, default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Update the updated_date field whenever the model instance is saved
        self.updated_date = timezone.now()
        super(Audit_UserActivity, self).save(*args, **kwargs)
