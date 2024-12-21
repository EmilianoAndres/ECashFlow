# Generated by Django 5.1.1 on 2024-11-05 03:43

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('vendors', '0001_initial'),
        ('wallet', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Audit_Deposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=18, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('audit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.audit')),
            ],
        ),
        migrations.CreateModel(
            name='Audit_Tx',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=18, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('audit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.audit')),
                ('destination_acc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination_account', to='wallet.wallet')),
                ('destination_customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='destination_customer', to='users.customer')),
                ('destination_vendor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='destination_vendor', to='vendors.vendor')),
                ('origin_acc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin_account', to='wallet.wallet')),
            ],
        ),
        migrations.CreateModel(
            name='Audit_UserActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('emailChanged', models.BooleanField(default=False)),
                ('passwordChanged', models.BooleanField(default=False)),
                ('phoneNumberChanged', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('audit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.audit')),
            ],
        ),
    ]
