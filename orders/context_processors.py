import os
from dotenv import load_dotenv

load_dotenv()

def paypal_settings(request):
    client_id = os.getenv('PAYPAL_CLIENT_ID')    
    return {
        'PAYPAL_CLIENT_ID': client_id
    }