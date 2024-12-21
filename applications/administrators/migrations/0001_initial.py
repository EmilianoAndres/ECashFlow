# Generated by Django 5.1.1 on 2024-11-05 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Administrator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=50, verbose_name='Nombre Completo')),
                ('password', models.CharField(max_length=50, verbose_name='Contraseña')),
                ('email', models.EmailField(max_length=50, verbose_name='Email')),
                ('is_super_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]