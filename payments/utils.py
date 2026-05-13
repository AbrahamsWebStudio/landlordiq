import requests
import base64
from datetime import datetime
from decouple import config


class MpesaClient:
    def __init__(self):
        # Read credentials and settings from environment via python-decouple
        self.consumer_key = config('MPESA_CONSUMER_KEY', default='')
        self.consumer_secret = config('MPESA_CONSUMER_SECRET', default='')
        self.shortcode = config('MPESA_SHORTCODE', default='')
        self.passkey = config('MPESA_PASSKEY', default='')
        # Allow overriding the base URL (sandbox vs production)
        self.base_url = config('MPESA_BASE_URL', default='https://sandbox.safaricom.co.ke')
        
    def get_token(self):
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        # Manually construct the Basic Auth header
        auth_string = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {"Authorization": f"Basic {encoded_auth}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get('access_token')
        except Exception as e:
            print(f"Token Error: {e}")
            if hasattr(response, 'text'):
                print(f"Safaricom said: {response.text}")
            return None

    def generate_password(self, timestamp):
        data_to_encode = self.shortcode + self.passkey + timestamp
        return base64.b64encode(data_to_encode.encode()).decode('utf-8')

    def stk_push(self, phone, amount, callback_url, reference):
        token = self.get_token()
        if not token:
            return {"errorMessage": "Could not generate access token"}

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = self.generate_password(timestamp)
        
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(float(amount)),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": callback_url,
            "AccountReference": reference,
            "TransactionDesc": f"Payment for {reference}"
        }
        
        response = requests.post(
            f"{self.base_url}/mpesa/stkpush/v1/processrequest",
            json=payload, 
            headers=headers
        )
        return response.json()
