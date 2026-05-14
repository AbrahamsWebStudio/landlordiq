from urllib import request

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from datetime import date
from django.urls import reverse

from .models import Property, Unit
from tenants.models import Lease


@login_required
def property_list(request):
    # FIX: Only show properties owned by current user
    properties = Property.objects.filter(owner=request.user).prefetch_related('units')
    today = date.today()
    
    properties_data = []
    for property in properties:
        units = property.units.all()
        total_units_count = units.count()
        occupied_units_count = units.filter(is_occupied=True).count()
        
        revenue = Lease.objects.filter(
            status='active',
            unit__property=property
        ).aggregate(total=Sum('monthly_rent'))['total'] or 0
        
        occupancy_pct = round((occupied_units_count / total_units_count * 100) if total_units_count > 0 else 0)
        
        properties_data.append({
            'id': property.id,
            'name': property.name,
            'location': property.address,
            'total_units': total_units_count,
            'occupied_units': occupied_units_count,
            'monthly_revenue': int(revenue),
            'occupancy_rate': occupancy_pct,
            'status': property.status,  # FIX: Use actual status from model
        })
    
    # FIX: Only count current user's units
    total_units = Unit.objects.filter(property__owner=request.user).count()
    occupied_units = Unit.objects.filter(is_occupied=True, property__owner=request.user).count()
    occupancy_rate = round((occupied_units / total_units * 100) if total_units > 0 else 0)
    monthly_revenue = Lease.objects.filter(
        status='active', 
        unit__property__owner=request.user
    ).aggregate(total=Sum('monthly_rent'))['total'] or 0
    
    stats = [
        {'icon': 'building', 'icon_color': 'text-brand', 'value': properties.count(), 'label': 'Total Properties'},
        {'icon': 'home', 'icon_color': 'text-brand', 'value': total_units, 'label': 'Total Units'},
        {'icon': 'users', 'icon_color': 'text-ui-success', 'value': occupied_units, 'label': 'Occupied Units', 'trend': f'{occupancy_rate}% occupied', 'trend_color': 'text-ui-success'},
        {'icon': 'trending-up', 'icon_color': 'text-ui-success', 'value': f"KES {int(monthly_revenue):,}", 'label': 'Monthly Revenue'},
    ]
    
    breadcrumbs = [
        {"label": "Home", "url": reverse('home')},
        {"label": "Properties", "url": None},
    ]

    return render(request, 'properties/list.html', {
        'breadcrumbs': breadcrumbs,
        'properties': properties_data,
        'stats': stats,
        'today': today,
        'page_title': "Properties",
        'page_subtitle': today.strftime("%A, %d %B %Y"),
    })


@login_required
def property_detail(request, property_id):
    # FIX: Add owner filter for security
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)
    units = property_obj.units.all()
    today = date.today()
    
    breadcrumbs = [
        {"label": "Home", "url": reverse('home')},
        {"label": "Properties", "url": reverse('properties:property_list')},
        {"label": property_obj.name, "url": None},
    ]
    
    return render(request, 'properties/detail.html', {
        'breadcrumbs': breadcrumbs,
        'property': property_obj,
        'units': units,
        'occupied_count': units.filter(is_occupied=True).count(),
        'today': today,
        'page_title': property_obj.name,
        'page_subtitle': "Property Details",
    })


@login_required
def property_add(request):
    from django.http import HttpResponseRedirect
    from django.urls import reverse
    
    if request.method == 'POST':
        # FIX: Add status field
        prop = Property.objects.create(
            name=request.POST.get('name'),
            address=request.POST.get('address'),
            status=request.POST.get('status', 'active'),
            owner=request.user
        )
        return HttpResponseRedirect(reverse('properties:property_detail', args=[prop.id]))
    
    breadcrumbs = [
        {"label": "Home", "url": reverse('home')},
        {"label": "Properties", "url": reverse('properties:property_list')},
        {"label": "Add Property", "url": None},
    ]

    return render(request, 'properties/add.html', {
        'today': date.today(),
        'breadcrumbs': breadcrumbs,
        'cancel_url': reverse('properties:property_list'),
        'status_options': [  # ADD THIS for the dropdown
            {"value": "active", "label": "Active"},
            {"value": "inactive", "label": "Inactive"},
        ]
    })


@login_required
def property_edit(request, property_id):
    # FIX: Add owner filter for security
    prop = get_object_or_404(Property, id=property_id, owner=request.user)

    if request.method == 'POST':
        prop.name = request.POST.get('name')
        prop.address = request.POST.get('address')
        prop.status = request.POST.get('status')
        prop.save()
        return redirect('properties:property_detail', property_id=prop.id)

    breadcrumbs = [
        {"label": "Home", "url": reverse('home')},
        {"label": "Properties", "url": reverse('properties:property_list')},
        {"label": "Edit Property", "url": None},
    ]
    status_options = [
        {"value": "active", "label": "Active"},
        {"value": "inactive", "label": "Inactive"},
    ]

    return render(request, 'properties/edit.html', {
        'property': prop,
        'today': date.today(),
        'breadcrumbs': breadcrumbs,
        'status_options': status_options
    })


@login_required
def property_delete(request, property_id):
    from django.http import JsonResponse
    from django.contrib import messages
    
    prop = get_object_or_404(Property, id=property_id, owner=request.user)
    
    if request.method == 'POST':
        prop_name = prop.name
        
        # Check if property has units
        if prop.units.exists():
            error_msg = f'Cannot delete "{prop_name}" because it has {prop.units.count()} unit(s). Delete all units first.'
            
            # AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': error_msg}, status=400)
            
            messages.error(request, error_msg)
            return redirect('properties:property_detail', property_id=property_id)
        
        # Delete the property
        prop.delete()
        
        # AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, f'Property "{prop_name}" deleted successfully.')
        return redirect('properties:property_list')
    
    # GET request - redirect to property detail
    messages.warning(request, 'Please use the delete button on the property page.')
    return redirect('properties:property_detail', property_id=property_id)