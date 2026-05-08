from decimal import Decimal
from datetime import date
from tenants.models import Lease
from utilities.models import ServiceUsage
from .models import Invoice


def generate_invoice_for_lease(lease, billing_month):
    """
    Generate one invoice for one lease for one month.
    billing_month: a date object — use the first day of the month.
    e.g. generate_invoice_for_lease(lease, date(2026, 5, 1))
    """

    # Guard: do not create duplicate invoices
    if Invoice.objects.filter(lease=lease, billing_month=billing_month).exists():
        return None, 'Invoice already exists for this month'

    # Step 1: Rent — pull from the Lease, not the Unit
    rent = lease.monthly_rent

    # Step 2: Charges — sum all ServiceUsage records for this unit this month
    usage_records = ServiceUsage.objects.filter(
        subscription__unit=lease.unit,
        billing_month=billing_month
    )
    charges_total = sum(u.billed_amount for u in usage_records)

    # Step 3: Create the Invoice
    invoice = Invoice.objects.create(
        lease=lease,
        billing_month=billing_month,
        rent_amount=rent,
        charges_amount=Decimal(str(charges_total)),
        total_amount=rent + Decimal(str(charges_total)),
        status=Invoice.STATUS_UNPAID
    )

    return invoice, 'Created'


def generate_all_invoices(billing_month):
    """
    Run this on the 1st of every month.
    Generates invoices for every active lease.
    Returns a summary dict with counts.
    """
    active_leases = Lease.objects.filter(status='active')
    created = 0
    skipped = 0

    for lease in active_leases:
        invoice, message = generate_invoice_for_lease(lease, billing_month)
        if invoice:
            created += 1
        else:
            skipped += 1

    return {
        'month': billing_month,
        'active_leases': active_leases.count(),
        'invoices_created': created,
        'invoices_skipped': skipped,
    }
