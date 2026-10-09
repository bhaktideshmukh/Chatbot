# FinSolve Technologies - RBAC AI Chatbot 🤖

An enterprise-grade Retrieval-Augmented Generation (RAG) chatbot built with **FastAPI**, **Streamlit**, and **LangChain** for FinSolve Technologies. 

This chatbot uses **Google's Gemini AI** to answer questions based on internal company documents. What makes this chatbot special is its **Role-Based Access Control (RBAC)**—it dynamically filters the vector database to ensure that employees can *only* query documents that they have the authorization to see based on their department.

## 🌟 Key Features
- **Role-Based Access Control (RBAC):** Users are assigned roles (e.g., Finance, HR, Engineering). The RAG engine filters ChromaDB on the backend to guarantee employees cannot leak or access unauthorized cross-departmental data.
- **Conversational Memory:** Built with LangChain's History-Aware Retriever, allowing users to ask natural follow-up questions without losing context.
- **Multi-Format Document Ingestion:** Recursively processes and embeds Markdown (`.md`), Text (`.txt`), and Data (`.csv`) files.
- **Google Gemini Integration:** Powered by `gemini-3.5-flash` for high-speed, cost-effective inference and `gemini-embedding-2` for dense vector search.

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **Backend:** FastAPI, Pydantic
* **AI Orchestration:** LangChain (Classic)
* **Vector Database:** ChromaDB
* **LLM & Embeddings:** Google Generative AI (Gemini)

---

## 🚀 Getting Started

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/bhaktideshmukh/Chatbot.git
cd Chatbot
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root directory and add your Google Gemini API Key:
```env
GOOGLE_API_KEY=your_api_key_here
```

### 3. Data Ingestion
Put your departmental data into the `backend/data/` folders. Then, run the ingestion script to chunk, embed, and store the documents in ChromaDB:
```bash
python backend/ingest.py
```
*(Note: If you get a file lock error while running this, make sure your FastAPI server is temporarily stopped!)*

### 4. Start the Backend (FastAPI)
Run the backend API server from the root directory:
```bash
python -m uvicorn backend.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### 5. Start the Frontend (Streamlit)
Open a new terminal and run the Streamlit UI:
```bash
python -m streamlit run frontend/app.py
```

---

## 🔐 Demo Accounts
To test the Role-Based Access Control, use the following dummy credentials (passwords are all `password123` unless specified):

| Username | Role | Access Level |
| :--- | :--- | :--- |
| `boss` | C-Level | **Full Access** to all departmental data |
| `peter` | Finance | Finance & General documents |
| `sarah` | HR | HR & General documents |
| `john` | Marketing | Marketing & General documents |
| `alice` | Engineering | Engineering & General documents |
| `intern` | General | Only General company policies |

*Try logging in as `peter` and asking about HR salaries. The bot will automatically block the query and state that it doesn't have the context to answer it!*
