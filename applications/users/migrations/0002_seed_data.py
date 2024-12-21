# -*- coding: utf-8 -*-
from time import timezone

from django.contrib.auth.models import User
from django.db import migrations

from applications.users.models import Customer_Type, Profession, Marital_Status, Tax_Situation, Funds_Source, Customer


def initial_seed(apps, schema_editor):

    # SEED CUSTOMER TYPES
    customer_type_1 = Customer_Type()
    customer_type_1.name = 'Persona Fisica'
    customer_type_1.save()

    # SEED PROFESSIONS
    profession_1 = Profession()
    profession_1.name = 'Autónomo'
    profession_1.save()
    profession_2 = Profession()
    profession_2.name = 'Empleado'
    profession_2.save()
    profession_3 = Profession()
    profession_3.name = 'Jubilado/Pensionado'
    profession_3.save()
    profession_4 = Profession()
    profession_4.name = 'Estudiante'
    profession_4.save()
    profession_5 = Profession()
    profession_5.name = 'Desempleado'
    profession_5.save()

    # SEED MARITAL STATUSES
    marital_status_1 = Marital_Status()
    marital_status_1.name = "Soltero"
    marital_status_1.save()
    marital_status_2 = Marital_Status()
    marital_status_2.name = "Concubino"
    marital_status_2.save()
    marital_status_3 = Marital_Status()
    marital_status_3.name = "Casado"
    marital_status_3.save()
    marital_status_4 = Marital_Status()
    marital_status_4.name = "Separado"
    marital_status_4.save()
    marital_status_5 = Marital_Status()
    marital_status_5.name = "Divorciado"
    marital_status_5.save()
    marital_status_6 = Marital_Status()
    marital_status_6.name = "Viudo"
    marital_status_6.save()

    # SEED TAX SITUATIONS
    tax_situation_1 = Tax_Situation()
    tax_situation_1.name = "Monotributo"
    tax_situation_1.save()
    tax_situation_2 = Tax_Situation()
    tax_situation_2.name = "Relación de Dependencia"
    tax_situation_2.save()
    tax_situation_3 = Tax_Situation()
    tax_situation_3.name = "Responsable Inscripto"
    tax_situation_3.save()
    tax_situation_4 = Tax_Situation()
    tax_situation_4.name = "Desempleado"
    tax_situation_4.save()

    # SEED FUNDS SOURCES
    funds_source_1 = Funds_Source()
    funds_source_1.name = "Salario/Ahorro"
    funds_source_1.save()
    funds_source_2 = Funds_Source()
    funds_source_2.name = "Indemnización/Compensación"
    funds_source_2.save()
    funds_source_3 = Funds_Source()
    funds_source_3.name = "Herencia/Legado/Donación"
    funds_source_3.save()
    funds_source_4 = Funds_Source()
    funds_source_4.name = "Venta de Muebles/Inmuebles"
    funds_source_4.save()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial')
    ]

    operations = [
        migrations.RunPython(initial_seed),
    ]