from django.urls import path
from . import views


app_name = 'payments'

urlpatterns = [
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
    path('initiate/<int:invoice_id>/', views.initiate_payment, name='initiate_payment'),
    path('ledger/', views.tenant_ledger, name='tenant_ledger'),
    path('receipt/<int:invoice_id>/', views.download_receipt, name='download_receipt'),
    path('invoice/<int:invoice_id>/download/', views.download_invoice, name='download_invoice'),
]
