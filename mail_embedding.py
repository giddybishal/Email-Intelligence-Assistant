import json
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def load_emails(file_path="emails.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        emails = json.load(f)
    return emails

def prepare_documents(emails):
    docs = []
    for email in emails:
        metadata = email.get("metadata", {})
        text = email.get("body", "")
        
        # Optionally truncate or clean the body if it's very long
        # text = text[:2000]   # limit to 2000 chars if needed
        
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "id": metadata.get("id"),
                    "sender": metadata.get("sender"),
                    "date": metadata.get("date"),
                },
            )
        )
    return docs

def get_embeddings_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def build_faiss_index(docs, save_path="faiss_index"):
    embeddings = get_embeddings_model()
    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(save_path)
    print(f"FAISS index saved to '{save_path}'")

def query_faiss(query, save_path="faiss_index"):
    embeddings = get_embeddings_model()
    vector_store = FAISS.load_local(save_path, embeddings, allow_dangerous_deserialization=True)
    
    results = vector_store.similarity_search(query, k=3)
    for i, r in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(r.metadata)
        print(r.page_content)  # print only first 500 chars

def run_mail_embedding():
    # Step 1: load and embed
    emails = load_emails()
    docs = prepare_documents(emails)
    build_faiss_index(docs)
    
    # Step 2: test query
    # query_faiss("job and work")

if __name__ == "__main__":
    run_mail_embedding()
