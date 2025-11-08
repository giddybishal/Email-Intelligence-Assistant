from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os, json, base64
import mailparser
import html
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def normalize_body(body):
    # Decode HTML entities and remove non-UTF-8 artifacts
    text = html.unescape(body.encode('latin1', 'ignore').decode('utf-8', 'ignore'))

    # Remove HTML tags like <a>, <div>, <p>, etc.
    text = re.sub(r'<[^>]+>', ' ', text)

    # Remove URLs (anything starting with http/https up to a space or newline)
    text = re.sub(r'http[s]?://\S+', '', text)

    # Remove excessive whitespace or line breaks
    text = re.sub(r'\s+', ' ', text).strip()

    return text

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

EXCLUDE = ['linkedin', 'internsathi', 'ngrok', 'himalayas', 'canva']

def authenticate_gmail():
    creds = None
    token_path = os.path.join(DATA_DIR, 'token.json')
    creds_path = os.path.join(DATA_DIR, 'credentials.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def fetch_latest_emails(service, n):
    # fetch IDs
    results = service.users().messages().list(userId='me', maxResults=50).execute()
    messages = results.get('messages', [])
    emails = []

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='raw').execute()

        # decode raw email data
        raw_email = base64.urlsafe_b64decode(msg_detail['raw'].encode('UTF-8'))
        parsed = mailparser.parse_from_bytes(raw_email)

        sender = parsed.from_[0][1] if parsed.from_ else None
        subject = parsed.subject
        date = parsed.date
        body = parsed.text_plain[0] if parsed.text_plain else parsed.body  # fallback if HTML-only

        # filter out unwanted senders
        if sender and any(ex in sender.lower() for ex in EXCLUDE):
            continue

        emails.append({
            "metadata": {
                "id": msg["id"],
                "threadId": msg["threadId"],
                "sender": sender,
                "date": date.strftime("%Y-%m-%d %H:%M:%S") if date else None
            },
            "body": f"Subject: {subject}\nFrom: {sender}\nDate: {date}\n\n{normalize_body(body.strip()) if body else ''}"
        })

        if len(emails) == n:
            break

    return emails

def save_emails_to_json(emails, filename='emails.json'):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(emails, f, ensure_ascii=False, indent=4)

def run_mail_fetcher():
    service = authenticate_gmail()
    emails = fetch_latest_emails(service, 10)
    save_emails_to_json(emails)
    print("Fetched emails saved to emails.json")

if __name__ == "__main__":
    run_mail_fetcher()    
