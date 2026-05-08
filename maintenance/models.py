# maintenance/models.py
from django.db import models
from tenants.models import Tenant
from properties.models import Unit

class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    BILLABLE_TO = [
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
        ('split', 'Split'),
    ]

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='maintenance_requests')
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=255)
    description = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    billable_to = models.CharField(max_length=20, choices=BILLABLE_TO, default='landlord')

    created_at = models.DateTimeField(auto_now_add=True)
    

class MaintenanceWorkOrder(models.Model):
    request = models.OneToOneField(MaintenanceRequest, on_delete=models.CASCADE)

    assigned_to = models.CharField(max_length=255, blank=True, null=True)  # handyman/vendor
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    material_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_completed = models.BooleanField(default=False)

    def total_cost(self):
        return self.labor_cost + self.material_cost