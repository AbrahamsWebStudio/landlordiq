# utilities/models.py
from django.db import models
from properties.models import Unit


# ── THE MENU ─────────────────────────────────────────────────────────────────
class ServiceCharge(models.Model):

    TYPE_FIXED = 'fixed'
    TYPE_METERED = 'metered'
    TYPE_CHOICES = [
        (TYPE_FIXED, 'Fixed'),
        (TYPE_METERED, 'Metered'),
    ]

    name = models.CharField(max_length=100)
    # e.g. Water, Trash, Generator Levy, Security Fee
    charge_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    # For Fixed: this is the flat monthly amount
    # For Metered: this is the price per unit consumed
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_charge_type_display()})"


# ── THE LINK ─────────────────────────────────────────────────────────────────
class UnitServiceSubscription(models.Model):

    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name='subscriptions'
    )
    service = models.ForeignKey(
        ServiceCharge, on_delete=models.PROTECT, related_name='subscriptions'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['unit', 'service']

    def __str__(self):
        return f"{self.unit} — {self.service.name}"


# ── THE RECORD ───────────────────────────────────────────────────────────────
class ServiceUsage(models.Model):

    subscription = models.ForeignKey(
        UnitServiceSubscription, on_delete=models.PROTECT,
        related_name='usage_records'
    )
    billing_month = models.DateField()
    # For Metered: enter previous and current — billed_amount is calculated
    # For Fixed: previous_reading and current_reading are left null
    previous_reading = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    current_reading = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    billed_amount = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.subscription.service.charge_type == 'metered':
            # Calculate from meter readings
            consumed = self.current_reading - self.previous_reading
            self.billed_amount = consumed * self.subscription.service.unit_price
        else:
            # Fixed charge — just use the unit price directly
            self.billed_amount = self.subscription.service.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subscription} - {self.billing_month}"