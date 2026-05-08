from django.contrib import admin
from .models import ServiceCharge, UnitServiceSubscription, ServiceUsage


@admin.register(ServiceCharge)
class ServiceChargeAdmin(admin.ModelAdmin):
    list_display = ('name', 'charge_type', 'unit_price', 'is_active')
    list_filter = ('charge_type', 'is_active')


@admin.register(UnitServiceSubscription)
class UnitServiceSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('unit', 'service', 'is_active')
    list_filter = ('service', 'is_active')


@admin.register(ServiceUsage)
class ServiceUsageAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'billing_month', 'previous_reading',
                    'current_reading', 'billed_amount', 'recorded_at')
    readonly_fields = ('billed_amount',)
