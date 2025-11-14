import os
from datetime import datetime, timedelta
from .mail_fetcher import run_mail_fetcher
from .mail_embedding import run_mail_embedding
from .llm_caller import chat

DATA_DIR = "data"
LAST_FETCH_FILE = os.path.join(DATA_DIR, "last_fetch.txt")
FETCH_INTERVAL = timedelta(minutes=60)

def main(message):
    # --- Only fetch emails if interval passed ---
    fetch_needed = True
    if os.path.exists(LAST_FETCH_FILE):
        with open(LAST_FETCH_FILE, "r") as f:
            last_fetch = datetime.fromisoformat(f.read().strip())
        if datetime.now() - last_fetch < FETCH_INTERVAL:
            fetch_needed = False

    if fetch_needed:
        run_mail_fetcher()

        # --- Write the latest time to last_fetch.txt ---
        with open(LAST_FETCH_FILE, "w") as f:
            f.write(datetime.now().isoformat())
        
        run_mail_embedding()

    return chat(message)

if __name__ == '__main__':
    main()
