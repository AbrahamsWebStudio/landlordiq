from django.contrib import admin
from .models import Tenant, Lease


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'national_id')
    search_fields = ('full_name', 'phone_number')


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'unit', 'start_date',
                    'deposit_amount', 'is_active')
    list_filter = ('status',)
