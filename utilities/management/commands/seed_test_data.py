from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from properties.models import Property, Unit
from tenants.models import Tenant, Lease
from utilities.models import ServiceCharge, UnitServiceSubscription
from utilities.services import UtilityService
from django.utils import timezone
from datetime import timedelta
from decouple import config

class Command(BaseCommand):
    help = 'Seeds a complete test environment'

    def handle(self, *args, **kwargs):
        # 1. Owner (use env-configured defaults when available)
        owner = User.objects.filter(is_superuser=True).first()
        if not owner:
            admin_user = config('SEED_ADMIN_USER', default='admin')
            admin_email = config('SEED_ADMIN_EMAIL', default='admin@example.com')
            admin_password = config('SEED_ADMIN_PASSWORD', default='admin123')
            owner = User.objects.create_superuser(admin_user, admin_email, admin_password)

        # 2. Property
        prop_name = config('SEED_PROPERTY_NAME', default='GDC Plaza')
        prop_address = config('SEED_PROPERTY_ADDRESS', default='Kakamega Central')
        prop, _ = Property.objects.get_or_create(
            name=prop_name,
            defaults={'address': prop_address, 'owner': owner}
        )

        # 3. Unit
        unit_number = config('SEED_UNIT_NUMBER', default='Suite 101')
        unit_rent = float(config('SEED_UNIT_RENT', default=25000.00))
        unit, _ = Unit.objects.get_or_create(
            property=prop,
            unit_number=unit_number,
            defaults={'default_rent': unit_rent}
        )

        # 4. Tenant
        tenant_name = config('SEED_TENANT_NAME', default='John Doe')
        tenant_email = config('SEED_TENANT_EMAIL', default='john@example.com')
        tenant_phone = config('SEED_TENANT_PHONE', default='0712345678')
        tenant_national_id = config('SEED_TENANT_NATIONAL_ID', default='12345678')

        tenant, _ = Tenant.objects.get_or_create(
            full_name=tenant_name,
            defaults={
                'email': tenant_email,
                'phone_number': tenant_phone,
                'national_id': tenant_national_id
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