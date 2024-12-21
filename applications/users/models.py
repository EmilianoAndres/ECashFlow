from django.contrib.sessions.models import Session
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Customer_Type(models.Model):
    name = models.CharField(null=False, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Update the updated_date field only if the instance already exists (i.e., it's not a new instance)
        self.updated_date = timezone.now()
        super(Customer_Type, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

class Funds_Source(models.Model):
    name = models.CharField(null=False, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Update the updated_date field whenever the model instance is saved
        self.updated_date = timezone.now()
        super(Funds_Source, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

class Marital_Status(models.Model):
    name = models.CharField(null=False, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Update the updated_date field whenever the model instance is saved
        self.updated_date = timezone.now()
        super(Marital_Status, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"
    
class Profession(models.Model):
    name = models.CharField(null=False, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Update the updated_date field whenever the model instance is saved
        self.updated_date = timezone.now()
        super(Profession, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"
    
class Tax_Situation(models.Model):
    name = models.CharField(null=False, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Update the updated_date field whenever the model instance is saved
        self.updated_date = timezone.now()
        super(Tax_Situation, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"

class Customer (models.Model):
    customer_type = models.ForeignKey(Customer_Type, on_delete=models.CASCADE, null=False)
    funds_source = models.ForeignKey(Funds_Source, on_delete=models.CASCADE, null=False)
    marital_status = models.ForeignKey(Marital_Status, on_delete=models.CASCADE, null=False)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, null=False)
    tax_situation = models.ForeignKey(Tax_Situation, on_delete=models.CASCADE, null=False)
    name = models.CharField("Nombre", max_length=30, default="name")
    last_name = models.CharField("Apellido", max_length=30, default="last_name")
    full_name = models.CharField("Nombre Completo", max_length=60, default="full_name")
    password = models.CharField("Contraseña",max_length=50)
    email = models.EmailField("Email", max_length=50)
    birth_date = models.DateTimeField(verbose_name="Fecha de nacimiento")
    phone_number = models.CharField("Número de Teléfono", max_length=10)
    cuit = models.CharField("CUIT", max_length=11)
    isPEP = models.BooleanField("Es Persona Politicamente Expuesta", default=False)
    isLB = models.BooleanField("Es Sujeto Obligado", default=False)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Update the updated_date field whenever the model instance is saved
        self.updated_date = timezone.now()
        super(Customer, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} - {self.email}"

    def remove_all_sessions(self):
        user_auth = User.objects.filter(email=self.email).first()
        if user_auth is None:
            return
        user_sessions = []
        all_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        for session in all_sessions:
            if str(user_auth.id) == session.get_decoded().get('_auth_user_id'):
                user_sessions.append(session.pk)
        return Session.objects.filter(pk__in=user_sessions).delete()

class CustomerDataChange(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)
    field_changed = models.CharField(max_length=50)
    field_value = models.CharField(max_length=100)
    is_validated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    validation_token = models.CharField(max_length=100, default="token")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

class CustomerRegister(models.Model):
    cuit = models.CharField(max_length=11)
    name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField()
    validation_token = models.CharField(max_length=100, default="token")
    is_validated = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


