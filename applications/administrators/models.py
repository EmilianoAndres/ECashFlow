from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Administrator(models.Model):
    full_name = models.CharField("Nombre Completo", max_length=50)
    password = models.CharField("Contraseña", max_length=50)
    email = models.EmailField("Email", max_length=50)
    is_super_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)