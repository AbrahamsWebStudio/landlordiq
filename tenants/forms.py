from django import forms
from .models import Tenant, Lease
from properties.models import Unit


class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['full_name', 'phone_number', 'national_id', 'email']

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')

        # basic Kenyan validation
        if not phone.startswith('07') and not phone.startswith('01'):
            raise forms.ValidationError("Enter a valid Kenyan phone number")

        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be 10 digits")

        return phone


class LeaseForm(forms.ModelForm):
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.filter(is_occupied=False),
        required=False
    )

    class Meta:
        model = Lease
        fields = ['unit', 'start_date', 'monthly_rent']

    def clean_monthly_rent(self):
        rent = self.cleaned_data.get('monthly_rent')

        if rent and rent <= 0:
            raise forms.ValidationError("Rent must be greater than 0")

        return rent
