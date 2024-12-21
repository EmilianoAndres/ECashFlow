

from django.urls import path
from .views import *

urlpatterns = [
    path('uploadBarcode/', UploadBarcode, name="UploadBarcode"),
    path('createPayment/', CreatePayment, name="CreatePayment")
]