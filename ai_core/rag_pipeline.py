import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

VECTOR_STORE_PATH = "vector_store/"
DATA_PATH = "data/"

def load_and_split_documents():
    """
    Loads documents from the DATA_PATH and splits them into chunks.
    """
    print("Loading documents...")
    documents = []
    for filename in os.listdir(DATA_PATH):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(DATA_PATH, filename)
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
            print(f"  - Loaded {filename}")
    if not documents:
        print("No PDF documents found in the 'data' folder.")
        return None
        
    print(f"\nTotal pages loaded: {len(documents)}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,  
        chunk_overlap=200   
    )

    print("\nSplitting documents into chunks with new strategy...")
    chunked_documents = text_splitter.split_documents(documents)
    
    print(f"Total chunks created: {len(chunked_documents)}")
    
    return chunked_documents

def create_vector_store():
    """
    Loads documents, creates local embeddings using Hugging Face, 
    and stores them in a Chroma vector store.
    """
    chunked_documents = load_and_split_documents()
    if not chunked_documents:
        print("Document loading failed. Aborting vector store creation.")
        return

    print("\nInitializing Hugging Face embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("\nCreating and populating the vector store (this may take a few minutes)...")
    db = Chroma.from_documents(
        chunked_documents, 
        embeddings, 
        persist_directory=VECTOR_STORE_PATH
    )
    
    print("\nVector store created successfully!")
    print(f"Total documents in store: {db._collection.count()}")


def create_rag_chain():
    """
    Creates the complete RAG chain for answering questions.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")

    print("Loading existing vector store...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(
        persist_directory=VECTOR_STORE_PATH, 
        embedding_function=embeddings
    )

    retriever = db.as_retriever(search_kwargs={'k': 3}) 
    print("Retriever created.")

    template = """
    You are an expert motorcycle mechanic.
    Answer the following question based ONLY on the provided context.
    If the context does not contain the answer, state that you cannot answer the question.

    CONTEXT:
    {context}

    QUESTION:
    {question}

    ANSWER:
    """
    prompt = PromptTemplate.from_template(template)

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    print("RAG chain created successfully!")
    return rag_chain
