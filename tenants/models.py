# tenants/models.py
from django.db import models
from django.conf import settings
from properties.models import Unit


class Tenant(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='tenant_profile',
        null=True, blank=True
    )
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    national_id = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    
    @property
    def id_number(self):
        """Compatibility alias for templates/forms that expect `id_number`."""
        return self.national_id

    @property
    def is_active(self):
        """Returns True if the tenant has any active leases."""
        return self.leases.filter(status='active').exists()


class Lease(models.Model):

    STATUS_ACTIVE = 'active'
    STATUS_UNDER_NOTICE = 'under_notice'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_UNDER_NOTICE, 'Under Notice'),
        (STATUS_CLOSED, 'Closed'),
    ]

    tenant = models.ForeignKey(
        Tenant, on_delete=models.PROTECT, related_name='leases'
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name='leases'
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # New fields — the billing core
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    rent_due_day = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )

    # is_active is now derived from status — kept as a Python property
    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    @property
    def total_paid(self):
        """Sum of amount_paid across all invoices for this lease."""
        from django.db.models import Sum
        total = self.invoices.aggregate(total=Sum('amount_paid'))['total'] or 0
        return total

    @property
    def balance(self):
        """Outstanding balance across all invoices for this lease."""
        from django.db.models import Sum
        totals = self.invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        paid = self.invoices.aggregate(total=Sum('amount_paid'))['total'] or 0
        return totals - paid

    def __str__(self):
        return f"{self.tenant.full_name} - {self.unit.unit_number}"
