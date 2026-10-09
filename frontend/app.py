import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Enterprise AI Chatbot", page_icon="🤖", layout="wide")

# Custom CSS for a beautiful Enterprise look
st.markdown("""
    <style>
        .main-header {
            font-family: 'Inter', sans-serif;
            color: #60a5fa;
            font-weight: 800;
            text-align: center;
            margin-bottom: 30px;
        }
        .stTextInput>div>div>input {
            border-radius: 8px;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LOGIN SCREEN ---
if st.session_state.user is None:
    st.markdown("<h1 class='main-header'>🔒 FinSolve Technologies</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; margin-top: -20px; margin-bottom: 30px; font-size: 16px; font-weight: 500;'>Role-Based Access Control Portal</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### Welcome Back")
            st.markdown("Please sign in to access your departmental documents.")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign In")
                
                if submitted:
                    with st.spinner("Authenticating..."):
                        response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
                        
                        if response.status_code == 200:
                            user_data = response.json()
                            st.session_state.user = user_data
                            st.success(f"Welcome {user_data['username']}! Logged in as: {user_data['role'].upper()}")
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")

# --- CHAT INTERFACE ---
else:
    role = st.session_state.user['role']
    token = st.session_state.user['access_token']
    
    with st.sidebar:
        st.markdown(f"## 👤 {st.session_state.user['username'].capitalize()}")
        st.info(f"**Role:** {role.upper()}")
        st.success("✅ Secure Connection (JWT)")
        
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.messages = []
            st.rerun()

    st.markdown(f"<h2 class='main-header'>🤖 AI Assistant ({role.upper()})</h2>", unsafe_allow_html=True)

    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a question about your departmental data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching secure documents..."):
                try:
                    chat_req = {
                        "query": prompt,
                        "role": role,
                        "chat_history": [] 
                    }
                    response = requests.post(f"{API_URL}/chat", json=chat_req)
                    
                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
