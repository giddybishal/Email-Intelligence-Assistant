import json
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

with open("emails.json", "r", encoding="utf-8") as f:
    emails = json.load(f)

email_docs = [
    Document(
        page_content=e["content"],
        metadata=e["metadata"]
    )
    for e in emails
]

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.from_documents(email_docs, embeddings)
db.save_local("email_index")