import streamlit as st
from datetime import datetime
from data_loader import KneeArthritisDataLoader
from rag_model import KneeArthritisRAG

st.set_page_config(page_title="KneeDoc AI", page_icon="🦵", layout="wide")

# --- CSS for dark gradient + animations ---
st.markdown("""
<style>
body {
  background: radial-gradient(circle at top left, #1a1f35 0%, #0d1117 70%);
  color: #e6e8eb;
}
h1, h2, h3, h4, h5, h6 { color: #fff; }
.stApp { background-color: transparent; }

.login-container {
  display: flex; justify-content: center; align-items: center;
  height: 100vh; flex-direction: column;
}
.login-card {
  background: rgba(255,255,255,0.05);
  padding: 3rem 3.5rem; border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  text-align: center; max-width: 420px; width: 90%;
}
.login-card h2 {
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  font-size: 2rem; font-weight: 700;
}
.gradient-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white; border: none; padding: 0.8rem 2rem;
  border-radius: 8px; font-weight: 600; font-size: 1rem;
  cursor: pointer; transition: all 0.3s ease; width: 100%;
}
.gradient-btn:hover {
  box-shadow: 0 0 20px rgba(118, 75, 162, 0.6);
  transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)


# --- Initialize session state ---
for key in ["api_key", "rag", "rag_initialized", "session_start"]:
    if key not in st.session_state:
        st.session_state[key] = None if "initialized" not in key else False
st.session_state.session_start = st.session_state.session_start or datetime.now()


# --- Login Page ---
def login_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>🦵 KneeDoc AI</h2>", unsafe_allow_html=True)
    st.markdown("<p>Enter your OpenAI API key to continue</p>", unsafe_allow_html=True)

    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    if st.button("Continue", key="login_btn", help="Enter your API key to continue", use_container_width=True):
        if api_key.startswith("sk-"):
            st.session_state.api_key = api_key
            with st.spinner("Initializing your session..."):
                loader = KneeArthritisDataLoader(data_dir="data")
                loader.load_all()
                st.session_state.rag = KneeArthritisRAG(loader, api_key)
                st.session_state.rag_initialized = True
            st.success("✅ Login successful! Redirecting...")
            st.experimental_rerun()
        else:
            st.error("Please enter a valid OpenAI API key (starts with 'sk-').")

    st.markdown("</div></div>", unsafe_allow_html=True)


# --- Route to pages after login ---
if not st.session_state.api_key:
    login_page()
else:
    st.sidebar.title("🦵 KneeDoc AI")
    st.sidebar.success("Logged in successfully")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Navigation**")
    st.sidebar.page_link("streamlit_app.py", label="Login", icon="🔑")
    st.sidebar.page_link("pages/1_Home.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/2_Features.py", label="Features", icon="⚙️")
    st.sidebar.page_link("pages/3_Exercise_Plan.py", label="Exercise Plan", icon="💪")
    st.sidebar.page_link("pages/4_Coach.py", label="AI Coach", icon="🤖")
    st.sidebar.page_link("pages/5_FAQ.py", label="FAQ", icon="❓")
    st.sidebar.markdown("---")
    st.sidebar.caption("Session started at: " + st.session_state.session_start.strftime("%I:%M %p"))
    st.markdown(
        "<h1 style='text-align:center;margin-top:3rem;'>Welcome to KneeDoc AI 🦵</h1>"
        "<p style='text-align:center;color:#aaa;'>Choose a section from the sidebar to begin.</p>",
        unsafe_allow_html=True
    )
