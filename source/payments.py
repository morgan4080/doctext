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

def dollars_to_cents(dollars):
    """Convert dollars to cents."""
    if dollars < 0:
        raise ValueError("Amount cannot be negative.")
    return int(round(dollars * 100))

def cents_to_dollars(cents):
    """Convert cents to dollars."""
    if cents < 0:
        raise ValueError("Amount cannot be negative.")
    return round(cents / 100, 2)

def initial_draft_pricing(apply, p):
        """Apply 10% extra if initial draft is requested."""
        return p * 0.1 if apply else 0.0

def calculate_order_price(data):
    price = 0.0
    spacing = 1
    pages_pricing = 0.0
    slides_pricing = 0.0
    charts_pricing = 0.0
    digital_copy_pricing = 0.0
    one_page_summary_pricing = 0.0
    plagiarism_report_pricing = 0.0
    apply_initial_draft = False

    # Calculate pages pricing: pages * priceBeforeExtraOptions
    if isinstance(data.get("pages"), (int, float)):
        pages_pricing = data.get("priceBeforeExtraOptions", 0) * data["pages"]

    # Calculate slides pricing: 6.5 * slides
    if isinstance(data.get("slides"), (int, float)):
        slides_pricing = 6.5 * data["slides"]

    # Calculate charts pricing: 5.0 * charts
    if isinstance(data.get("charts"), (int, float)):
        charts_pricing = 5.0 * data["charts"]

    # Adjust spacing: 'single' = 2 * price, 'double' = 1 * price
    if isinstance(data.get("spacing"), str):
        spacing = 2 if data["spacing"] == "single" else 1

    # Digital copies: +9.99 if true
    if isinstance(data.get("digital_copies"), bool) and data["digital_copies"]:
        digital_copy_pricing = 9.99

    # Apply initial draft: set flag if true
    if isinstance(data.get("initial_draft"), bool) and data["initial_draft"]:
        apply_initial_draft = True

    # One page summary: +17.99 if true
    if isinstance(data.get("one_page_summary"), bool) and data["one_page_summary"]:
        one_page_summary_pricing = 17.99

    # Plagiarism report: +7.99 if true
    if isinstance(data.get("plagiarism_report"), bool) and data["plagiarism_report"]:
        plagiarism_report_pricing = 7.99

    # Calculate total price
    price = (
        pages_pricing * spacing
        + slides_pricing
        + charts_pricing
        + plagiarism_report_pricing
        + one_page_summary_pricing
        + digital_copy_pricing
        + initial_draft_pricing(apply_initial_draft, pages_pricing)
    )

    # Return price as a string rounded to 2 decimal places
    print(f"SHOW THE PRICE {price}")
    return price

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