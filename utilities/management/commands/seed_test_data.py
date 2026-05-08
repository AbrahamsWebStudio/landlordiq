from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from properties.models import Property, Unit
from tenants.models import Tenant, Lease
from utilities.models import ServiceCharge, UnitServiceSubscription
from utilities.services import UtilityService
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seeds a complete test environment'

    def handle(self, *args, **kwargs):
        # 1. Owner
        owner = User.objects.filter(is_superuser=True).first()
        if not owner:
            owner = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

        # 2. Property
        prop, _ = Property.objects.get_or_create(
            name="GDC Plaza", 
            defaults={'address': "Kakamega Central", 'owner': owner}
        )

        # 3. Unit
        unit, _ = Unit.objects.get_or_create(
            property=prop, 
            unit_number="Suite 101",
            defaults={'default_rent': 25000.00} 
        )

        # 4. Tenant
        tenant, _ = Tenant.objects.get_or_create(
            full_name="John Doe", 
            defaults={
                'email': "john@example.com", 
                'phone_number': "0712345678",
                'national_id': "12345678"
            }
        )

        # 5. Lease
        Lease.objects.get_or_create(
            unit=unit,
            tenant=tenant,
            status='active',
            defaults={
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timedelta(days=365),
                'monthly_rent': 25000.00,
                'deposit_amount': 25000.00
            }
        )

       # 6. Utilities Seeding
        water_charge, _ = ServiceCharge.objects.get_or_create(
            name="Water", 
            charge_type="metered", 
            defaults={'unit_price': 150.00}
        )
        
        sub, _ = UnitServiceSubscription.objects.get_or_create(
            unit=unit, 
            service=water_charge
        )

        # Record a reading (10 units * 150 = 1500)
        from utilities.services import UtilityService
        UtilityService.record_reading(sub, 10.00)
        self.stdout.write(self.style.SUCCESS("Recorded 10 units of Water for John Doe."))

        # 7. Invoice Generation
        # Generate invoice using the invoice engine
        from payments.invoice_engine import generate_invoice_for_lease
        lease = Lease.objects.get(unit=unit, tenant=tenant, status='active')
        billing_month = timezone.now().date().replace(day=1)
        invoice, msg = generate_invoice_for_lease(lease, billing_month)

        if invoice:
            self.stdout.write(self.style.SUCCESS(
                f"Generated Invoice: {invoice.total_amount} KES (Rent: {invoice.rent_amount}, Charges: {invoice.charges_amount})"
            ))
        
        self.stdout.write(self.style.SUCCESS("Successfully seeded GDC Plaza."))