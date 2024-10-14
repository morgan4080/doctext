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

def get_order(order_id):
    try:
        url = f'{API_URL}/getOrders/{order_id}'
        print(f"Get Order URL {url}")
        response = requests.get(url)

        if response.status_code == 200:
            order_data = response.json()
        else:
            print(f"Failed to fetch order. Status code: {url} {response.status_code}")
            order_data = {"error": f"Failed to fetch order. Status code: {response.status_code}"}

    except requests.exceptions.RequestException as e:
        order_data = {"error": f"Request failed: {str(e)}"}

    return order_data

def calculate_order_amount(order_id):
    order_data=get_order(order_id)
    return order_data.get('totalPrice', 0)