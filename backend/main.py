from utils.mail_fetcher import run_mail_fetcher
from utils.mail_embedding import run_mail_embedding
from utils.llm_caller import chat

def main():
    run_mail_fetcher()
    run_mail_embedding()
    chat("Are there any new important news about my intership?")

if __name__ == '__main__':
    main()
