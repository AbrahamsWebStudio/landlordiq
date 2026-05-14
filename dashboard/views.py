from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import date, timedelta
from calendar import monthrange

from tenants.models import Tenant, Lease
from properties.models import Unit
from payments.models import Invoice, Payment


@login_required
def dashboard(request):
    today = date.today()
    
    # Get active leases
    active_leases = Lease.objects.select_related('tenant', 'unit__property').filter(status='active')
    
    # Count unique tenants with active leases
    active_tenants_count = active_leases.values('tenant').distinct().count()
    
    # Current month invoices
    month_start = date(today.year, today.month, 1)
    invoices = Invoice.objects.select_related('lease', 'lease__tenant', 'lease__unit__property')\
        .filter(billing_month=month_start)
    
    invoice_map = {inv.lease_id: inv for inv in invoices}
    
    # Calculate stats
    total_collected = 0
    total_outstanding = 0
    overdue_tenants = []
    outstanding_count = 0
    
    for lease in active_leases:
        invoice = invoice_map.get(lease.id)
        if not invoice:
            continue
        
        balance = invoice.total_amount - invoice.amount_paid
        total_collected += float(invoice.amount_paid)
        total_outstanding += float(balance)
        
        if balance > 0:
            outstanding_count += 1
            
            # Calculate days overdue
            due_day = lease.rent_due_day
            last_day = monthrange(today.year, today.month)[1]
            due_date = date(today.year, today.month, min(due_day, last_day))
            days_overdue = (today - due_date).days
            
            if days_overdue > 0:
                overdue_tenants.append({
                    'name': lease.tenant.full_name,
                    'unit': lease.unit.unit_number,
                    'amount': f"{int(lease.monthly_rent):,}",
                    'days_overdue': days_overdue,
                })
    
    # Get recent payments
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_payments = Payment.objects.select_related(
        'invoice__lease__tenant',
        'invoice__lease__unit__property',
    ).filter(
        is_confirmed=True,
        payment_date__gte=thirty_days_ago
    ).order_by('-payment_date')[:10]
    
    payments_feed = []
    for p in recent_payments:
        lease = p.invoice.lease
        paid_on = p.payment_date
        
        diff = (today - paid_on.date()).days
        if diff == 0:
            time_label = f"Today, {paid_on.strftime('%I:%M %p')}"
        elif diff == 1:
            time_label = f"Yesterday, {paid_on.strftime('%I:%M %p')}"
        elif diff < 7:
            time_label = f"{diff} days ago"
        else:
            time_label = paid_on.strftime('%-d %b, %I:%M %p')
        
        receipt = getattr(p, 'mpesa_code', None) or getattr(p, 'mpesa_receipt_number', None) or 'MPESA'
        
        payments_feed.append({
            "name": lease.tenant.full_name,
            "unit": f"Unit {lease.unit.unit_number}",
            "amount": f"{int(p.amount):,}",
            "time": time_label,
            "ref": receipt,
        })
    
    # Chart data
    chart_bars = []
    for i in range(5, -1, -1):
        if today.month - i <= 0:
            year = today.year - 1
            month = 12 + (today.month - i)
        else:
            year = today.year
            month = today.month - i
        
        m_start = date(year, month, 1)
        month_total = Invoice.objects.filter(billing_month=m_start).aggregate(total=Sum('amount_paid'))['total'] or 0
        is_current = (month == today.month and year == today.year)
        
        max_revenue = 1500000
        height_percent = max(int((month_total / max_revenue) * 90), 30) if month_total > 0 else 30
        
        if month_total >= 1000000:
            value_display = f"KES {month_total/1000000:.1f}M"
        elif month_total >= 1000:
            value_display = f"KES {month_total/1000:.0f}K"
        else:
            value_display = f"KES {int(month_total)}"
        
        chart_bars.append({
            "label": m_start.strftime('%b'),
            "value": value_display,
            "height": f"{height_percent}%",
            "color": "bg-ui-success" if is_current else "bg-brand",
        })
    
    # Calculate expiring leases
    thirty_days_later = today + timedelta(days=30)
    expiring_leases = Lease.objects.filter(
        status='active',
        end_date__lte=thirty_days_later,
        end_date__gte=today
    ).count()
    
    stats = {
        "collected": f"KES {int(total_collected):,}",
        "outstanding": f"KES {int(total_outstanding):,}",
        "total_tenants": active_tenants_count,
        "maintenance_pending": len(overdue_tenants),
    }
    
    return render(request, "dashboard/index.html", {
        "stats": stats,
        "overdue_tenants": overdue_tenants,
        "payments_feed": payments_feed,
        "chart_bars": chart_bars,
        "today": today,
        "outstanding_count": outstanding_count,
        "expiring_leases": expiring_leases,
        "page_title": "Dashboard",
        "page_subtitle": today.strftime("%A, %d %B %Y"),
    })
