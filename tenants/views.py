from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from datetime import date
from calendar import monthrange

from .models import Tenant, Lease
from properties.models import Unit
from payments.models import Invoice


@login_required
def tenant_list(request):
    today = date.today()
    tenants = Tenant.objects.all()
    
    tenants_data = []
    active_leases_count = 0
    overdue_payments_count = 0
    expiring_leases_count = 0
    
    for tenant in tenants:
        active_lease = Lease.objects.filter(tenant=tenant, status='active').first()
        
        unit_display = "No unit assigned"
        rent_amount = "0"
        lease_status = "Inactive"
        payment_status = "N/A"
        initials = "??"
        
        if tenant.full_name:
            name_parts = tenant.full_name.split()
            if name_parts:
                initials = ''.join([p[0].upper() for p in name_parts[:2]])
        
        if active_lease:
            active_leases_count += 1
            
            if active_lease.unit:
                unit_display = f"Unit {active_lease.unit.unit_number}"
                if active_lease.unit.property:
                    unit_display += f", {active_lease.unit.property.name}"
            
            rent_amount = f"{int(active_lease.monthly_rent):,}" if active_lease.monthly_rent else "0"
            lease_status = "Active"
            
            if active_lease.end_date:
                days_until_expiry = (active_lease.end_date - today).days
                if 0 <= days_until_expiry <= 30:
                    lease_status = "Expiring"
                    expiring_leases_count += 1
            
            current_invoice = Invoice.objects.filter(lease=active_lease).order_by('-billing_month').first()
            
            if current_invoice:
                balance = float(current_invoice.total_amount) - float(current_invoice.amount_paid)
                if balance <= 0:
                    payment_status = "Paid"
                else:
                    due_day = active_lease.rent_due_day
                    last_day = monthrange(today.year, today.month)[1]
                    due_date = date(today.year, today.month, min(due_day, last_day))
                    if (today - due_date).days > 0:
                        payment_status = "Overdue"
                        overdue_payments_count += 1
                    else:
                        payment_status = "Pending"
        
        lease_class = ""
        if lease_status == "Active":
            lease_class = "bg-green-100 text-green-700"
        elif lease_status == "Expiring":
            lease_class = "bg-orange-100 text-orange-700"
        else:
            lease_class = "bg-gray-100 text-gray-600"
        
        payment_class = ""
        if payment_status == "Paid":
            payment_class = "bg-green-100 text-green-700"
        elif payment_status == "Overdue":
            payment_class = "bg-red-100 text-red-700"
        elif payment_status == "Pending":
            payment_class = "bg-yellow-100 text-yellow-700"
        else:
            payment_class = "bg-gray-100 text-gray-600"
        
        tenants_data.append({
            'id': tenant.id,
            'name': tenant.full_name or "Unknown",
            'initials': initials,
            'phone': tenant.phone_number or "N/A",
            'unit': unit_display,
            'rent': rent_amount,
            'lease_status': lease_status,
            'lease_class': lease_class,
            'payment_status': payment_status,
            'payment_class': payment_class,
        })
    
    total_units = Unit.objects.count()
    occupied_units = Unit.objects.filter(is_occupied=True).count()
    occupancy_rate = round((occupied_units / total_units * 100) if total_units > 0 else 0)
    
    stats = [
        {'icon': 'users', 'icon_color': 'text-brand', 'value': tenants.count(), 'label': 'Total Tenants', 'trend': '+3 this month', 'trend_color': 'text-ui-success'},
        {'icon': 'file-text', 'icon_color': 'text-brand', 'value': active_leases_count, 'label': 'Active Leases', 'trend': f'{occupancy_rate}% occupancy', 'trend_color': 'text-ui-success'},
        {'icon': 'alert-circle', 'icon_color': 'text-ui-danger', 'value': overdue_payments_count, 'label': 'Overdue Payments', 'trend': 'Require attention', 'trend_color': 'text-ui-danger'},
        {'icon': 'clock', 'icon_color': 'text-ui-warning', 'value': expiring_leases_count, 'label': 'Leases Expiring', 'trend': 'Next 30 days', 'trend_color': 'text-ui-warning'},
    ]
    
    table_columns = ['TENANT', 'CONTACT', 'UNIT', 'RENT', 'LEASE', 'PAYMENT']
    
    return render(request, 'tenants/list.html', {
        'stats': stats,
        'table_columns': table_columns,
        'table_rows': tenants_data,
        'today': today,
        'page_title': "Tenants",
        'page_subtitle': today.strftime("%A, %d %B %Y"),
    })


@login_required
def tenant_detail(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    return render(request, 'tenants/detail.html', {'tenant': tenant, 'today': date.today()})


@login_required
def tenant_add(request):
    from django.http import HttpResponseRedirect
    from django.urls import reverse
    
    if request.method == 'POST':
        tenant = Tenant.objects.create(
            full_name=request.POST.get('full_name'),
            phone_number=request.POST.get('phone_number'),
            email=request.POST.get('email'),
            national_id=request.POST.get('national_id'),
        )
        return HttpResponseRedirect(reverse('tenants:tenant_detail', args=[tenant.id]))
    
    return render(request, 'tenants/add.html', {'today': date.today()})


@login_required
def tenant_edit(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    if request.method == 'POST':
        tenant.full_name = request.POST.get('full_name')
        tenant.phone_number = request.POST.get('phone_number')
        tenant.email = request.POST.get('email')
        tenant.save()
        return redirect('tenants:tenant_detail', tenant_id=tenant.id)
    
    return render(request, 'tenants/edit.html', {'tenant': tenant, 'today': date.today()})


@login_required
def tenant_delete(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    if request.method == 'POST':
        tenant.delete()
        return redirect('tenants:tenant_list')
    return render(request, 'tenants/confirm_delete.html', {'tenant': tenant, 'today': date.today()})


@login_required
def tenant_lease(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    active_lease = tenant.leases.filter(status='active').first()
    return render(request, 'tenants/lease.html', {'tenant': tenant, 'lease': active_lease, 'today': date.today()})
