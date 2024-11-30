from django import forms
from django.forms import PasswordInput, TextInput

from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["customer_type", "funds_source", "marital_status",
                  "profession", "tax_situation", "password", "email",
                  "isPEP", "isLB"]
        labels = {
            "tax_situation": "Situación Impositiva",
            "profession": "Profesión",
            "marital_status": "Estado Marital",
            "customer_type": "Tipo de Persona",
            "funds_source": "Origen de los Fondos",
            "password": "Contraseña",
            "email": "Email",
        }
        widgets = {
            "password": PasswordInput(
                attrs={'placeholder': '********', 'autocomplete': 'off', 'data-toggle': 'password'}),
        }