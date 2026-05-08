from django.core.management.base import BaseCommand
from utilities.models import ServiceCharge

class Command(BaseCommand):
    help = 'Seeds initial service charges for LandlordIQ'

    def handle(self, *args, **kwargs):
        services = [
            {'name': 'Water', 'charge_type': 'metered', 'unit_price': 150.00},
            {'name': 'Trash', 'charge_type': 'fixed', 'unit_price': 500.00},
            {'name': 'Security', 'charge_type': 'fixed', 'unit_price': 1000.00},
        ]

        for service_data in services:
            obj, created = ServiceCharge.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'charge_type': service_data['charge_type'],
                    'unit_price': service_data['unit_price']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Exists: {obj.name}"))