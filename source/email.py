import os
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

SCOPES = [
        "https://www.googleapis.com/auth/gmail.send"
    ]

CLIENT_CONFIG = {'installed': {
    'client_id': os.getenv('GOOGLE_CLIENT_ID'),
    'project_id': os.getenv('GOOGLE_PROJECT_ID'),
    'auth_uri': os.getenv('GOOGLE_AUTH_URI'),
    'token_uri': os.getenv('GOOGLE_TOKEN_URI'),
    'auth_provider_x509_cert_url': os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
    'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
    'redirect_uris': ["http://localhost"]}}

flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
creds = flow.run_local_server(port=0)
service = build('gmail', 'v1', credentials=creds)


def order_confirmation(email):
    message = MIMEText('This is the body of the email')
    message['to'] = email
    message['subject'] = 'Order Complete Confirmation'
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(F'sent message to {message} Message Id: {message["id"]}')
    except HTTPError as error:
        print(F'An error occurred: {error}')
        message = None