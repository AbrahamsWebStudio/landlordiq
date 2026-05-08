import os
import django
from dotenv import load_dotenv

# 1. Setup Django & Env
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from payments.utils import MpesaClient
from payments.models import Invoice

def run_test():
    client = MpesaClient()
    
    # Target your phone number (Format: 2547XXXXXXXX)
    phone = "254795285363" 
    
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

    # 3. Trigger the Push using your Ngrok URL from earlier
    callback_url = "https://6f85-41-90-144-8.ngrok-free.app/payments/callback/"
    
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