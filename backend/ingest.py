import os
import csv
import shutil
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Load environment variables
load_dotenv(override=True)

DATA_DIR = "backend/data"
CHROMA_PATH = "chroma_db"

def main():
    raw_documents = []
    pre_chunked_docs = []
    
    # 1. Iterate over every item in the data directory
    for item in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, item)
        
        # 2. Check if it is a folder (this folder name will be our 'role')
        if os.path.isdir(folder_path):
            role = item.lower()
            
            # 3. Iterate through the files inside this role folder
            for filename in os.listdir(folder_path):
                filepath = os.path.join(folder_path, filename)
                
                # --- NEW ROW-BY-ROW CSV LOGIC ---
                if filename.endswith(".csv"):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row_idx, row in enumerate(reader):
                            # Create a readable sentence for the LLM
                            row_details = ", ".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in row.items())
                            row_text = f"Data Record from {filename}: {row_details}"
                            
                            doc = Document(
                                page_content=row_text,
                                metadata={
                                    "role": role, 
                                    "source": filename,
                                    "row_id": row_idx
                                }
                            )
                            # These are already perfect chunks, so bypass the text splitter!
                            pre_chunked_docs.append(doc)
                            
                # --- STANDARD TEXT FILE LOGIC ---
                elif filename.endswith((".md", ".txt")):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                        
                    doc = Document(
                        page_content=text,
                        metadata={
                            "role": role, 
                            "source": filename
                        }
                    )
                    raw_documents.append(doc)
            
    print(f"Loaded {len(raw_documents)} raw text documents and {len(pre_chunked_docs)} CSV rows.")
    
    # 4. Split the standard text documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150
    )
    chunks = text_splitter.split_documents(raw_documents)
    print(f"Split raw documents into {len(chunks)} chunks.")
    
    # Combine everything!
    all_chunks = chunks + pre_chunked_docs
    all_chunks = [c for c in all_chunks if c.page_content.strip()]
    
    print(f"Total chunks to ingest: {len(all_chunks)}")

    # 5. Clean up old DB to avoid duplicates
    if os.path.exists(CHROMA_PATH):
        print("Clearing old vector database...")
        shutil.rmtree(CHROMA_PATH)
        
    import time
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", task_type="retrieval_document")
    vectorstore = Chroma(embedding_function=embeddings, persist_directory=CHROMA_PATH)
    
    # Process in batches to avoid rate limits but keep it fast
    batch_size = 10
    successful = 0
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        print(f"Ingesting batch {i//batch_size + 1} (Rows {i} to {i+len(batch)})...")
        try:
            vectorstore.add_documents(batch)
            successful += len(batch)
            time.sleep(1) # Sleep to respect rate limits
        except Exception as e:
            print(f"Failed to ingest batch: {e}")
            time.sleep(3) # Wait a bit longer if rate limited
        
    print(f"Ingestion complete. {successful}/{len(all_chunks)} chunks added to Vector database!")

if __name__ == "__main__":
    main()
