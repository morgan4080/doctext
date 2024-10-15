import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

API_URL = os.getenv('API_URL')
MONGODB_URI = os.getenv('MONGODB_URI')

client = MongoClient(MONGODB_URI)
db = client['proctor'] 
order_session_collection = db['order_session']

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

def create_order_session(order_id, session_token):
    try:
        # Use the order_id as the _id for the document
        filter_query = {'_id': order_id}
        update_data = {'$set': {'session_token': session_token}}

        # Upsert: Insert if not exists, update if it exists
        result = order_session_collection.update_one(
            filter_query, update_data, upsert=True
        )

        if result.upserted_id:
            print(f"Created new session for Order ID: {result.upserted_id}")
            return {'success': True, 'message': 'Order session created successfully'}
        else:
            print(f"Updated session token for Order ID: {order_id}")
            return {'success': True, 'message': 'Order session updated successfully'}

    except Exception as e:
        print(f"Error creating/updating order session: {e}")
        return {'success': False, 'message': str(e)}

# Function to look up the session token by order_id
def get_session_token_by_order_id(order_id):
    try:
        session = order_session_collection.find_one({'order_id': order_id})
        if session:
            return session.get('session_token')
        else:
            return None
    except Exception as e:
        print(f"Error retrieving session token: {e}")
        return None