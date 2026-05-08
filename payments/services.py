from .invoice_engine import generate_invoice_for_lease


class BillingService:
    @staticmethod
    def generate_invoice(lease, billing_date):
        """Wrapper around the invoice engine to generate one invoice."""
        month_start = billing_date.replace(day=1)
        invoice, msg = generate_invoice_for_lease(lease, month_start)
        return invoice
