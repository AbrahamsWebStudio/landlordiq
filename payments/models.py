from django.db import models
from tenants.models import Lease


# ── THE MASTER BILL ──────────────────────────────────────────────────────────
class Invoice(models.Model):

    STATUS_UNPAID = 'unpaid'
    STATUS_PARTIAL = 'partial'
    STATUS_PAID = 'paid'
    STATUS_CHOICES = [
        (STATUS_UNPAID, 'Unpaid'),
        (STATUS_PARTIAL, 'Partial'),
        (STATUS_PAID, 'Paid'),
    ]

    lease = models.ForeignKey(
        Lease, on_delete=models.PROTECT, related_name='invoices'
    )
    # First day of the month this invoice covers — e.g. 2026-05-01
    billing_month = models.DateField()
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    charges_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_UNPAID
    )
    created_at = models.DateTimeField(auto_now_add=True)
    mpesa_checkout_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        # One invoice per lease per month — no duplicates
        unique_together = ['lease', 'billing_month']
        ordering = ['-billing_month']

    def update_status(self):
        """Call this after every payment to recalculate status."""
        if self.amount_paid >= self.total_amount:
            self.status = self.STATUS_PAID
        elif self.amount_paid > 0:
            self.status = self.STATUS_PARTIAL
        else:
            self.status = self.STATUS_UNPAID
        self.save()

    def __str__(self):
        return f"{self.lease.tenant.full_name} - {self.billing_month} - {self.get_status_display()}"


class InvoiceItem(models.Model):
    SOURCE_RENT = 'rent'
    SOURCE_UTILITY = 'utility'
    SOURCE_MAINTENANCE = 'maintenance'
    SOURCE_OTHER = 'other'

    SOURCE_CHOICES = [
        (SOURCE_RENT, 'Rent'),
        (SOURCE_UTILITY, 'Utility'),
        (SOURCE_MAINTENANCE, 'Maintenance'),
        (SOURCE_OTHER, 'Other'),
    ]

    invoice = models.ForeignKey(
        'Invoice',
        on_delete=models.CASCADE,
        related_name='items'
    )

    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default=SOURCE_OTHER
    )

    # THIS is what connects maintenance later
    maintenance_request_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"

# ── PAYMENT ──────────────────────────────────────────────────────────────────
class Payment(models.Model):

    invoice = models.ForeignKey(
        Invoice, on_delete=models.PROTECT, related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    mpesa_code = models.CharField(max_length=50, unique=True)
    is_confirmed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-payment_date']

    def save(self, *args, **kwargs):
        """Auto-update invoice amount_paid and status after every payment."""
        super().save(*args, **kwargs)
        # Recalculate total paid on the invoice
        total = self.invoice.payments.filter(
            is_confirmed=True
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        self.invoice.amount_paid = total
        self.invoice.update_status()

    def __str__(self):
        return f"KES {self.amount} — {self.mpesa_code}"
