import os
import django

# 1. Setup Django & Env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from payments.utils import MpesaClient
from payments.models import Invoice

def run_test():
    client = MpesaClient()
    
    # Target your phone number (Format: 2547XXXXXXXX) - set via env for safety
    from decouple import config
    phone = config('TEST_PHONE', default='2547XXXXXXXX')
    
    # 2. Get the latest invoice from your seeded data
    try:
        invoice = Invoice.objects.latest('created_at')
        amount = int(invoice.total_amount)
        reference = f"INV{invoice.id}"
        print(f"--- Testing STK Push for Invoice {reference} ---")
        print(f"Amount: KES {amount}")
    except Exception:
        print("No invoice found, using default test values.")
        amount = 1
        reference = "TEST001"

    # 3. Trigger the Push using your public callback URL (from env)
    from decouple import config
    callback_url = config('MPESA_CALLBACK_URL', default='http://localhost:8000' + '/payments/callback/')
    
    response = client.stk_push(
        phone=phone,
        amount=amount,
        callback_url=callback_url,
        reference=reference
    )
    
    print("\nSafaricom Response:")
    print(response)

if __name__ == "__main__":
    run_test()