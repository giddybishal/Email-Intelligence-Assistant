from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os, json, re
from bs4 import BeautifulSoup
from base64 import urlsafe_b64decode

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

EXCLUDE = ['linkedin', 'internsathi', 'ngrok', 'himalayas', 'canva']

def clean_email_body(body, extract_urls=False, extract_emails=False):
    # 1. Strip HTML
    soup = BeautifulSoup(body, "html.parser")
    text = soup.get_text(separator="\n")

    # 2. Remove quoted replies / forward headers
    text = re.sub(r'(^>.*?$)', '', text, flags=re.MULTILINE)
    text = re.sub(r'On .* wrote:', '', text, flags=re.DOTALL)
    text = re.sub(r'Forwarded message:', '', text, flags=re.IGNORECASE)

    # 3. Normalize whitespace
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    text = text.strip()

    # 4. Optional extraction
    urls = re.findall(r'https?://\S+', text) if extract_urls else []
    emails = re.findall(r'\S+@\S+', text) if extract_emails else []

    return text, urls, emails

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def get_email_body(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            # recursive check for nested parts
            body = get_email_body(part)
            if body:
                return body
    if payload.get('mimeType') == 'text/plain' and payload.get('body', {}).get('data'):
        return urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    return None

def fetch_latest_emails(service, n):
    # fetch IDs
    results = service.users().messages().list(userId='me', maxResults=50).execute()
    messages = results.get('messages', [])
    emails = []

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_detail['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), None)
        sender = next((h['value'] for h in headers if h['name'] == 'From'), None)
        if True in [exclude in sender.lower() for exclude in EXCLUDE]:
            continue
        date = next((h['value'] for h in headers if h['name'] == 'Date'), None)

        raw_body = get_email_body(msg_detail['payload']) or ''
        cleaned_body, urls, emails_in_body = clean_email_body(raw_body, extract_urls=True, extract_emails=True)

        emails.append({
            'id': msg['id'],
            'threadId': msg['threadId'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': cleaned_body,
            'urls': urls,
            'emails_in_body': emails_in_body
        })

        if len(emails) == n:
            break

    return emails

def save_emails_to_json(emails, filename='emails.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(emails, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    service = authenticate_gmail()
    emails = fetch_latest_emails(service, 2)
    save_emails_to_json(emails)
    print("Fetched emails saved to emails.json")
