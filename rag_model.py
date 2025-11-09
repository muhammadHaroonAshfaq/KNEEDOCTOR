"""Main Streamlit App — KneeDoc AI (Multi-Page with Login & Navigation)"""

import streamlit as st
from datetime import datetime
from data_loader import KneeArthritisDataLoader
from rag_model import KneeArthritisRAG

# ---------------------------------------------------------------------
# Streamlit Config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="KneeDoc AI",
    page_icon="🦵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------
# Global Styling (dark blue + white text)
# ---------------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #000000 0%, #001a33 100%) !important;
    color: white !important;
}
header, footer {visibility: hidden;}
h1, h2, h3, h4, h5, h6, p, div, label, span {
    color: white !important;
}
.stButton>button {
    background: linear-gradient(135deg, #0077ff, #33ccff);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.8rem 1.2rem;
    font-weight: 600;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #0099ff, #33ddff);
    transform: translateY(-2px);
}
input, textarea {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Initialize Session Variables
# ---------------------------------------------------------------------
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "rag" not in st.session_state:
    st.session_state.rag = None
if "rag_initialized" not in st.session_state:
    st.session_state.rag_initialized = False
if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now()

# ---------------------------------------------------------------------
# Helper: Load RAG
# ---------------------------------------------------------------------
@st.cache_resource
def init_rag(api_key):
    loader = KneeArthritisDataLoader(data_dir="data")
    loader.load_all()
    rag = KneeArthritisRAG(loader, api_key)
    return rag, loader

# ---------------------------------------------------------------------
# Login Page
# ---------------------------------------------------------------------
def login_page():
    st.markdown("<h1 style='text-align:center;'>🦵 Welcome to KneeDoc AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#aad4ff;'>Your AI physiotherapy assistant for knee arthritis</p>", unsafe_allow_html=True)
    
    st.image("https://cdn.pixabay.com/photo/2016/11/18/15/03/exercise-1838416_960_720.jpg", use_column_width=True)

    with st.form("login_form"):
        api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password", placeholder="sk-...")
        submitted = st.form_submit_button("Login")

        if submitted:
            if api_key and api_key.startswith("sk-"):
                with st.spinner("Initializing AI system..."):
                    st.session_state.api_key = api_key
                    st.session_state.rag, _ = init_rag(api_key)
                    st.session_state.rag_initialized = True
                st.success("✅ Login successful! Loading your dashboard...")
                st.rerun()
            else:
                st.error("⚠️ Please enter a valid OpenAI API key (starts with sk-).")

# ---------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------
def sidebar_nav():
    st.sidebar.title("🦵 KneeDoc AI")
    st.sidebar.success("✅ Logged in")

    st.sidebar.markdown("### Navigation")
    st.sidebar.page_link("pages/1_Home.py", label="🏠 Home")
    st.sidebar.page_link("pages/2_Features.py", label="⚙️ Features")
    st.sidebar.page_link("pages/3_Exercise_Plan.py", label="📋 Exercise Plan")
    st.sidebar.page_link("pages/4_Coach.py", label="🤖 AI Coach")

    st.sidebar.divider()
    st.sidebar.markdown("### Session Info")
    duration = (datetime.now() - st.session_state.session_start).seconds // 60
    st.sidebar.write(f"🕒 Duration: {duration} min")

    if st.sidebar.button("🔄 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# ---------------------------------------------------------------------
# App Logic
# ---------------------------------------------------------------------
if not st.session_state.api_key:
    login_page()
else:
    sidebar_nav()
    st.markdown("<h2 style='text-align:center;'>Welcome back to KneeDoc AI 🦵</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Use the sidebar to navigate between features.</p>", unsafe_allow_html=True)
