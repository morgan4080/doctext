import os
import datetime
import stripe
import json
from flask import Flask, render_template, request, redirect, flash, send_from_directory, url_for, jsonify
from dotenv import load_dotenv
from config.config import Config
from source.file_handlers import save_file
from source.extractors import extract_text_from_docx, extract_content_from_pptx
from source.payments import calculate_discount, get_order, calculate_order_amount, get_user, update_payment_status, create_transaction, create_order_session, get_session_token_by_order_id, dollars_to_cents, cents_to_dollars

load_dotenv()

app = Flask(__name__, template_folder='../templates')
app.config.from_object(Config)

stripe.api_key = os.getenv('SECRET_KEY_STRP')
WEBHOOK_SCRT = os.getenv('STRP_WEBHOOK_SCRT')

@app.route('/robots.txt')
def robots():
    return send_from_directory('../static', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('../static', 'sitemap.xml')

@app.route('/checkout/complete/<order_id>')
def checkout_complete(order_id):
    session_token = request.cookies.get('next-auth.session-token')
    order_data = get_order(order_id, session_token)
    return render_template('complete.html', order=order_data, discount=calculate_discount(order_id))

@app.route('/checkout/<order_id>')
def checkout_form(order_id):
    session_token = request.cookies.get('next-auth.session-token')
    order_data = get_order(order_id, session_token)
    print(get_session_token_by_order_id(order_id))
    return render_template('checkout_form.html', order=order_data, discount=calculate_discount(order_id), publishable=os.getenv('PUBLISHABLE_KEY_STRP'), session_token=session_token)

@app.route('/docext/')
def upload_form():
    return render_template('upload.html')

@app.route('/docext/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        flash('No files selected')
        return redirect(request.url)
    
    files = request.files.getlist('files[]')
    
    for file in files:
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        save_file(file)
    
    return redirect(url_for('list_uploaded_files'))

@app.route('/docext/uploads')
def list_uploaded_files():
    try:
        extracted_data = []
        files = os.listdir(app.config['UPLOAD_FOLDER'])

        if not files:
            return redirect(url_for('upload_form'))

        for file in files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            if os.path.isfile(file_path):
                if file.endswith('.docx'):
                    data = extract_text_from_docx(file_path)
                elif file.endswith('.pptx'):
                    data = extract_content_from_pptx(file_path)
                else:
                    data = "Unsupported file type"

                upload_info = {
                    'file_name': file,
                    'upload_date': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                    'data': data
                }

                extracted_data.append(upload_info)

        return render_template('uploads.html', files=extracted_data)
    except Exception as e:
        return str(e)

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        session_token = request.cookies.get('next-auth.session-token')
        data = json.loads(request.data)
        amount = calculate_order_amount(data["id"], session_token)
        amount_in_cents = dollars_to_cents(amount)
        create_order_session(data["id"], session_token)
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
            },
            metadata={'orderId': data["id"]},
        )
        return jsonify({
            'clientSecret': intent['client_secret']
            # [DEV]: For demo purposes only, you should avoid exposing the PaymentIntent ID in the client-side code.
            # 'dpmCheckerLink': 'https://dashboard.stripe.com/settings/payment_methods/review?transaction_id={}'.format(intent['id']),
        })
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/checkout/hook', methods=['POST'])
def stripe_webhook():
    # Get the webhook data from the request
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Verify the webhook signature using Stripe library
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SCRT
        )
    except ValueError as e:
        # Invalid payload
        print(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f"Signature verification failed: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle the event based on its type
    event_type = event['type']
    data = event['data']['object']

    if event_type == 'payment_intent.succeeded':
        print(f"Payment for {data['amount']} succeeded.")
        # Process the payment (e.g., update order status in your database)
        order_id = data['metadata'].get('orderId')
        session_token = get_session_token_by_order_id(order_id)

        print(f"Metadata Order ID: {order_id}, Session Token: {session_token}")

        session_data = get_user(session_token)

        if 'error' in session_data and session_data['error'] is not None:
            print(f"ERROR getting user session data: {session_data.error}")
        else:
            user = session_data.get('user', {})

            username = user.get('name')
            user_id = user.get('_id')

            print({'transactionid': data['id'], 'amount': cents_to_dollars(data['amount']), 'username': username, 'userid': user_id, 'currency': data['currency'], 'orderid': order_id})

            update_payment_status(order_id, session_token)

            create_transaction(data['id'], cents_to_dollars(data['amount']), username, user_id, data['currency'], order_id, session_token)
    
    elif event_type == 'payment_intent.payment_failed':
        print(f"Payment for {data['amount']} failed.")
        # Handle the failure (e.g., notify the user)
    else:
        print(f"Unhandled event type: {event_type}")

    # Respond to Stripe with a 200 status to acknowledge receipt
    return jsonify({'status': 'success'}), 200

if __name__ == "__main__":
    app.run(debug=True)
