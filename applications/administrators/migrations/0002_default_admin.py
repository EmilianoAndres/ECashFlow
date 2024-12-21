from datetime import datetime

from decouple import config
from django.contrib.auth.models import User
from django.db import migrations

from applications.administrators.models import Administrator


def initial_seed(apps, schema_editor):

    # SEED ADMIN USER
    newUser = User.objects.create_user(config("DEFAULT_ADMIN_USER", cast=str, default=None),
                                       config("DEFAULT_ADMIN_USER", cast=str, default=None),
                                       config("DEFAULT_ADMIN_PASSWORD", cast=str, default=None)
                                       )
    newUser.last_login = datetime.now()
    newUser.save()
    newAdmin = Administrator()
    newAdmin.full_name = config("DEFAULT_ADMIN_USER", cast=str, default=None)
    newAdmin.email = config("DEFAULT_ADMIN_USER", cast=str, default=None)
    newAdmin.password = config("DEFAULT_ADMIN_PASSWORD", cast=str, default=None)
    newAdmin.save()


class Migration(migrations.Migration):

    dependencies = [
        ('administrators', '0001_initial'),
        ('users', '0003_test_user'),
        ('auth', '0005_alter_user_last_login_null')
    ]

    operations = [
        migrations.RunPython(initial_seed),
    ]