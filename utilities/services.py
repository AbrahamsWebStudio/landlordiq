from decimal import Decimal
from django.utils import timezone
from .models import ServiceUsage


class UtilityService:
    """Helper service for utility operations used by management commands and views."""

    @staticmethod
    def record_reading(subscription, current_reading, reading_date=None):
        """Record a service usage reading for a subscription.

        Args:
            subscription: UnitServiceSubscription instance
            current_reading: numeric (int/float/Decimal) current meter reading
            reading_date: optional date for the reading (defaults to today)

        Returns:
            The created ServiceUsage instance.
        """
        if reading_date is None:
            reading_date = timezone.now().date()

        # Use the billing month as the first day of the reading month
        billing_month = reading_date.replace(day=1)

        # Determine previous reading (last recorded current_reading)
        last = subscription.usage_records.order_by("-recorded_at", "-id").first()

        previous = last.current_reading if last else Decimal('0')

        # Normalize current reading to Decimal
        current = Decimal(str(current_reading))

        usage = ServiceUsage(
            subscription=subscription,
            previous_reading=previous,
            current_reading=current,
            billing_month=billing_month,
        )
        usage.save()
        return usage
