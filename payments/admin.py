from django.contrib import admin
from .models import Invoice, Payment


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('lease', 'billing_month', 'total_amount', 'status')
    list_filter = ('status', 'billing_month')
    search_fields = ('lease__tenant__full_name', 'lease__unit__unit_number')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'mpesa_code', 'payment_date', 'is_confirmed')
    search_fields = ('mpesa_code', 'invoice__lease__tenant__full_name')