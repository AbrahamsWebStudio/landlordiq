from django.db import models
from django.conf import settings


class Property(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=255)
    address = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Unit(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE,
                                 related_name='units')
    unit_number = models.CharField(max_length=50)
    # Renamed from rent_amount — this is now a default suggestion only
    # The actual rent charged is stored on the Lease model
    default_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.property.name} - {self.unit_number}"

    def get_utility_status(self):
        """Returns a list of latest usage records for this unit."""
        from utilities.models import UnitServiceSubscription
        status = []
        subscriptions = self.subscriptions.all()  # Uses the related_name
        for sub in subscriptions:
            # usage_records are ordered most-recent-first by recorded_at
            latest = sub.usage_records.order_by('-recorded_at').first()
            status.append({
                'name': sub.service.name,
                'last_reading': latest.current_reading if latest else "No data",
                'last_bill': latest.billed_amount if latest else 0,
                'date': latest.recorded_at if latest else None
            })
        return status
