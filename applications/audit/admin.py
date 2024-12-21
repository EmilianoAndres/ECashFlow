from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Audit)
admin.site.register(Audit_Tx)
admin.site.register(Audit_UserActivity)