import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Load environment variables (Make sure OPENAI_API_KEY is in your .env)
load_dotenv()

DATA_DIR = "backend/data"
CHROMA_PATH = "chroma_db2"

def main():
    documents = []
    
    # 1. Iterate over every item in the data directory
    for item in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, item)
        
        # 2. Check if it is a folder (this folder name will be our 'role')
        if os.path.isdir(folder_path):
            role = item.lower() # e.g., 'finance', 'hr', 'general'
            
            # 3. Iterate through the files inside this role folder
            for filename in os.listdir(folder_path):
                if filename.endswith((".md", ".txt", ".csv")):
                    filepath = os.path.join(folder_path, filename)
                    
                    # Read the file content
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                        
                    # 4. Create the LangChain Document with RBAC Metadata!
                    doc = Document(
                        page_content=text,
                        metadata={
                            "role": role, 
                            "source": filename
                        }
                    )
                    documents.append(doc)
            
    print(f"Loaded {len(documents)} documents with role metadata.")
    
    # 5. Split the documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, # slightly larger chunks for markdown
        chunk_overlap=150
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    
    import time

    # Filter empty chunks just in case
    chunks = [c for c in chunks if c.page_content.strip()]
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", task_type="retrieval_document")
    
    vectorstore = Chroma(embedding_function=embeddings, persist_directory=CHROMA_PATH)
    
    # Process individually to avoid rate limits, IndexError, and safety blocks
    successful = 0
    for i, chunk in enumerate(chunks):
        print(f"Ingesting chunk {i+1} of {len(chunks)}...")
        try:
            vectorstore.add_documents([chunk])
            successful += 1
            time.sleep(1) # Sleep to respect rate limits
        except Exception as e:
            print(f"Failed to ingest chunk {i+1}: {e}")
            time.sleep(2) # Wait a bit longer if rate limited
        
    print(f"Ingestion complete. {successful}/{len(chunks)} chunks added to Vector database!")

if __name__ == "__main__":
    main()
