from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ---- Initialize the RAG pipeline ----
pages = PyPDFLoader("products.pdf").load()
chunks = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30).split_documents(pages)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    max_new_tokens=512,
    temperature=0.3,
)
chat = ChatHuggingFace(llm=llm)

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

prompt = ChatPromptTemplate.from_template(
    "You are a friendly shop assistant for Crystal Clear Beauty. "
    "Answer the question using only the context below. "
    "If the answer is not in the context, say you don't know.\n\n"
    "Context:\n{context}\n\nQuestion: {question}"
)

qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | chat | StrOutputParser()
)

# ---- API ----
app = FastAPI()

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(body: Question):
    return {"answer": qa_chain.invoke(body.question)}

@app.get("/health")
def health():
    return {"status": "ok"}