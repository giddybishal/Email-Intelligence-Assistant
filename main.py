from mail_fetcher import authenticate_gmail, fetch_latest_emails, save_emails_to_json

def main():
    service = authenticate_gmail()
    emails = fetch_latest_emails(service, 5) 
    save_emails_to_json(emails)

if __name__ == '__main__':
    main()
