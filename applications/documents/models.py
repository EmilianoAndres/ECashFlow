from django.db import models

# Create your models here.

class Barcode(models.Model):
    file = models.FileField(upload_to='documents/%Y/%m/%d')