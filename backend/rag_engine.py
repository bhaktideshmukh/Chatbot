import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
vectorstore = Chroma(persist_directory="chroma_db2", embedding_function=embeddings)
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.3)

def get_answer(query: str, role: str, chat_history: list) -> str:
    # 1. RBAC Logic
    allowed_roles = ["general"]
    if role == "c-level":
        allowed_roles = ["finance", "hr", "marketing", "engineering", "general"]
    elif role != "general":
        allowed_roles.append(role) 

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 4, "filter": {"role": {"$in": allowed_roles}}}
    )
    
    # Format history for LangChain
    formatted_history = []
    for msg in chat_history:
        langchain_role = "human" if msg["role"] == "user" else "ai"
        formatted_history.append((langchain_role, msg["content"]))
    
    # 2. History-Aware Retriever Prompt
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    
    # 3. Answer Generation Prompt
    system_prompt = (
        "You are a helpful AI assistant for the company. "
        "Use the following retrieved context to answer the user's question.\n\n"
        "Context:\n{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    # 4. Invoke with Memory
    response = rag_chain.invoke({"input": query, "chat_history": formatted_history})
    
    answer = response["answer"]
    sources = [doc.metadata.get("source") for doc in response["context"]]
    if sources:
        answer += "\n\n*Sources: " + ", ".join(set(sources)) + "*"
        
    return answer
