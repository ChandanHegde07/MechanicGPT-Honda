import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

DATA_PATH = "data/"

def load_and_split_documents():
    """
    Loads all PDF documents from the DATA_PATH, splits them into manageable chunks,
    and returns a list of these chunks.
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
        return []

    print(f"\nTotal pages loaded: {len(documents)}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  
        chunk_overlap=100 
    )
    
    print("\nSplitting documents into chunks...")
    chunked_documents = text_splitter.split_documents(documents)
    
    print(f"Total chunks created: {len(chunked_documents)}")
    
    return chunked_documents

if __name__ == '__main__':
    chunks = load_and_split_documents()
    
    if chunks:
        print("\n--- Sample Chunk ---")
        print(chunks[0].page_content[:500])
        print("\n--- Metadata of Sample Chunk ---")
        print(chunks[0].metadata)