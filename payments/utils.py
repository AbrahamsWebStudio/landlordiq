import requests
import base64
import os
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

class MpesaClient:
    def __init__(self):
        # Using the standard Safaricom Sandbox 'Lipa Na M-Pesa Online' credentials
        self.consumer_key = os.getenv("MPESA_CONSUMER_KEY")
        self.consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
        self.shortcode = os.getenv("MPESA_SHORTCODE")
        self.passkey = os.getenv("MPESA_PASSKEY")
        self.base_url = "https://sandbox.safaricom.co.ke"
        
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
