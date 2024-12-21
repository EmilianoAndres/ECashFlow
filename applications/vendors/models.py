from django.db import models
from django.utils import timezone

from applications.users.models import Customer


# Create your models here.

class VendorType(models.Model):
    name = models.CharField(null=False, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class Vendor(models.Model):
    vendor_type = models.ForeignKey(VendorType, on_delete=models.CASCADE, null=False)
    code = models.CharField("CODE", max_length=7)
    name = models.CharField("Vendor Fantasy Name", max_length=50)
    cuit = models.CharField("CUIT", max_length=11)
    holder_name = models.CharField("Holder's Name", max_length=50)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Update the updated_date field whenever the model instance is saved
        self.updated_date = timezone.now()
        super(Vendor, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - Code: {self.code}"

class VendorPayment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=False)
    payment_number = models.CharField("Payment Number", max_length=8)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    due_date = models.DateField(null=True)
    has_impacted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['vendor', 'payment_number'], name='unique vendorcodepayment')
        ]
