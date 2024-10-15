import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('API_URL')

def calculate_discount(order_id):
    discount = {
        "code": "N/A",
        "amount": 0.00
    }

    return discount

def get_order(order_id, session_token):
    try:
        url = f'{API_URL}/getOrders/{order_id}'

        if session_token:
            headers = {
                'Cookie': 'next-auth.session-token='+session_token
            }
        else:
            headers = {
                'Cookie': 'next-auth.session-token='
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

def get_user(session_token):
    try:
        url = f'{API_URL}/auth/session'

        if session_token:
            headers = {
                'Cookie': 'next-auth.session-token='+session_token
            }
        else:
            headers = {
                'Cookie': 'next-auth.session-token='
            }

        response = requests.request("GET", url, headers=headers)


        if response.status_code == 200:
            session_data = response.json()
        else:
            print(f"Failed to fetch auth session. Status code: {url} {response.status_code}")
            session_data = {"error": f"Failed to fetch auth session. Status code: {response.status_code}"}

    except requests.exceptions.RequestException as e:
        session_data = {"error": f"Request failed: {str(e)}"}

    return session_data

def update_payment_status(order_id, session_token):
    data = {'paymentStatus': 'confirmed'}
    
    try:
        url = f'{API_URL}/paymentstatus/{order_id}'

        if session_token:
            headers = {
                'Cookie': 'next-auth.session-token='+session_token
            }
        else:
            headers = {
                'Cookie': 'next-auth.session-token='
            }

        response = requests.request(
            "PUT",
            url,
            json=data,
            headers=headers
        )

        # Check if the request was successful
        if response.status_code == 200:
            print(f"Order {order_id} status updated to 'confirmed'.")
        else:
            print(f"Failed to update order {order_id}. Response: {response.text}")

    except requests.RequestException as e:
        print(f"Error while updating order {order_id}: {e}")

def create_transaction(transaction_id, amount, username, user_id, currency, order_id, session_token):
    
    data = {'transactionid': transaction_id, 'amount': amount, 'username': username, 'userid': user_id, 'currency': currency, 'orderid': order_id}
    
    try:
        url = f'{API_URL}/transaction'

        if session_token:
            headers = {
                'Cookie': 'next-auth.session-token='+session_token
            }
        else:
            headers = {
                'Cookie': 'next-auth.session-token='
            }

        response = requests.request(
            "POST",
            url,
            json=data,
            headers=headers
        )

        if response.status_code == 200:
            print(f"Transaction {transaction_id} created.")
        else:
            print(f"Failed to create transaction {transaction_id}. Response: {response.text}")

    except requests.RequestException as e:
        print(f"Error while creating transaction {transaction_id}: {e}")

def calculate_order_amount(order_id, session_token):
    order_data=get_order(order_id, session_token)
    return order_data.get('totalPrice', 1)