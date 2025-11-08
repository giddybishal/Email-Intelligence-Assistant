from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.callbacks import StdOutCallbackHandler
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

index_path = os.path.join(DATA_DIR, "faiss_index")

vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k":3})

llm = ChatOllama(model="gpt-oss:120b-cloud")

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory, callbacks=[StdOutCallbackHandler()])

def chat(message):
    result = conversation_chain.invoke({"question": message})
    return result["answer"]

if __name__ == "__main__":
    print(chat('Are there any recent mails about my Internship?'))
