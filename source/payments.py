import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('API_URL')

def calculate_discount(order_id):
    print(f"Calculate discount {order_id} {API_URL}")
    discount = {
        "code": "N/A",
        "amount": 0.00
    }

    return discount

def get_order(order_id, session_token):
    try:
        print(f"Session Token {session_token}")
        url = f'{API_URL}/getOrders/{order_id}'

        if session_token:
            headers = {
                'Cookie': 'next-auth.session-token='+session_token
            }
        else:
            headers = {
                'Cookie': 'next-auth.session-token='+os.getenv('SESSION_TOKEN')
            }

        response = requests.request("GET", url, headers=headers)


        if response.status_code == 200:
            order_data = response.json()
        else:
            print(f"Failed to fetch order. Status code: {url} {response.status_code}")
            order_data = {"error": f"Failed to fetch order. Status code: {response.status_code}"}

    except requests.exceptions.RequestException as e:
        order_data = {"error": f"Request failed: {str(e)}"}

    return order_data

def calculate_order_amount(order_id, session_token):
    order_data=get_order(order_id, session_token)
    return order_data.get('totalPrice', 0)