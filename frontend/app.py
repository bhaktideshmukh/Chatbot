import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Enterprise AI Chatbot", page_icon="🤖", layout="centered")

# Initialize session state variables
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LOGIN SCREEN ---
if st.session_state.user is None:
    st.title("🔒 Enterprise RBAC Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            # Send request to our FastAPI backend
            response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
            
            if response.status_code == 200:
                user_data = response.json()
                st.session_state.user = user_data
                st.success(f"Welcome {user_data['username']}! Logged in as: {user_data['role']}")
                st.rerun()
            else:
                st.error("Invalid username or password.")

# --- CHAT INTERFACE ---
else:
    role = st.session_state.user['role']
    st.title(f"🤖 Enterprise Chatbot ({role.upper()} Access)")
    
    # Sidebar Profile & Logout
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.user['username']}**")
        st.write(f"Role: **{role}**")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.messages = []
            st.rerun()
            
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question based on your department's data..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Call FastAPI /chat endpoint
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{API_URL}/chat", 
                    json={"query": prompt, "role": role, "chat_history": st.session_state.messages[:-1]}
                )
                
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer found.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Error communicating with backend: {response.text}")
