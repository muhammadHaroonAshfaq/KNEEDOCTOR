import streamlit as st
from datetime import datetime
import time
from data_loader import KneeArthritisDataLoader
from rag_model import KneeArthritisRAG

st.set_page_config(page_title="KneeDoc AI", page_icon="🦵", layout="wide")

# === GLOBAL DARK THEME ===
st.markdown("""
<style>
body {
  background: linear-gradient(160deg, #000000 0%, #001a33 100%);
  color: #ffffff;
}
h1, h2, h3, h4, h5, h6, label, p, span, div {
  color: #ffffff !important;
}
.stApp { background-color: transparent; }

.sidebar .sidebar-content {
  background-color: #000000;
  color: white;
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  flex-direction: column;
}
.login-card {
  background: rgba(0, 51, 102, 0.4);
  padding: 3rem 3.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 25px rgba(0, 153, 255, 0.4);
  text-align: center;
  max-width: 420px;
  width: 90%;
  animation: fadeIn 0.7s ease-in-out;
}
.login-card h2 {
  background: linear-gradient(135deg, #0099ff, #33ccff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 2rem;
  font-weight: 700;
}
.gradient-btn {
  background: linear-gradient(135deg, #0077ff, #33ccff);
  color: white;
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}
.gradient-btn:hover {
  box-shadow: 0 0 20px rgba(0, 153, 255, 0.8);
  transform: translateY(-2px);
}
.chat-bubble {
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 0.5rem;
  max-width: 80%;
  word-wrap: break-word;
}
.user-bubble {
  background: linear-gradient(135deg, #0055aa, #0099ff);
  align-self: flex-end;
  color: white;
  margin-left: auto;
}
.ai-bubble {
  background: linear-gradient(135deg, #111827, #1f2b3b);
  color: #e5e7eb;
  align-self: flex-start;
}
.typing {
  font-style: italic;
  color: #8ab4f8;
  padding: 0.5rem;
}
@keyframes fadeIn {
  from {opacity: 0; transform: translateY(10px);}
  to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)


# === SESSION STATE ===
defaults = {
    "api_key": None,
    "rag": None,
    "rag_initialized": False,
    "session_start": datetime.now(),
    "page": "Home",
    "messages": []
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


# === LOGIN PAGE ===
def login_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>🦵 KneeDoc AI</h2>", unsafe_allow_html=True)
    st.markdown("<p>Enter your OpenAI API key to continue</p>", unsafe_allow_html=True)

    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    if st.button("Continue", key="login_btn", use_container_width=True):
        if api_key.startswith("sk-"):
            st.session_state.api_key = api_key
            with st.spinner("Initializing your AI coach..."):
                loader = KneeArthritisDataLoader(data_dir="data")
                loader.load_all()
                st.session_state.rag = KneeArthritisRAG(loader, api_key)
                st.session_state.rag_initialized = True
            st.success("✅ Login successful! Redirecting...")
            time.sleep(0.8)
            st.session_state.page = "Home"
            st.rerun()
        else:
            st.error("Please enter a valid OpenAI API key (starts with 'sk-').")

    st.markdown("</div></div>", unsafe_allow_html=True)


# === SIDEBAR MENU ===
def sidebar_menu():
    with st.sidebar:
        st.title("🦵 KneeDoc AI")
        st.success("Logged in successfully")
        st.markdown("---")

        menu = st.radio("📍 Navigation", [
            "Home",
            "Features",
            "Exercise Plan",
            "AI Coach",
            "FAQ"
        ], index=["Home", "Features", "Exercise Plan", "AI Coach", "FAQ"].index(st.session_state.page))

        st.session_state.page = menu
        st.markdown("---")
        st.caption("Session started: " + st.session_state.session_start.strftime("%I:%M %p"))


# === PAGE FUNCTIONS ===
def page_home():
    st.markdown("<h1 style='text-align:center;'>Welcome to KneeDoc AI 🦵</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#ccc;'>AI-powered knee arthritis guidance and recovery support.</p>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2920/2920243.png", width=200)
    st.write("""
    - Personalized AI recommendations  
    - Guided exercises  
    - Real-time tracking and education
    """)


def page_features():
    st.title("⚙️ Features")
    features = [
        ("🤖", "AI Coach", "Interactive chat-based knee rehabilitation support."),
        ("💪", "Custom Exercises", "Tailored routines based on pain and flexibility."),
        ("📈", "Progress Tracker", "Monitor recovery progress in real-time."),
        ("🔒", "Data Privacy", "Your data stays local and secure.")
    ]
    cols = st.columns(2)
    for i, (emoji, title, desc) in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div style='background:rgba(0,51,102,0.3);border-radius:12px;
                        padding:1rem;border:1px solid rgba(255,255,255,0.1);
                        margin-bottom:0.8rem;'>
                <h3>{emoji} {title}</h3>
                <p style='color:#aaa;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)


def page_exercise():
    st.title("💪 Exercise Plan")
    if not st.session_state.rag_initialized:
        st.warning("Please log in again to access your exercise plan.")
        return
    st.info("Personalized exercise routines will appear here after AI analysis.")
    st.json({"Example": "Sample plan generated from RAG context."})


# === UPGRADED AI COACH PAGE ===
def page_coach():
    st.title("🤖 AI Coach")
    if not st.session_state.rag_initialized:
        st.warning("Please log in again to use the AI Coach.")
        return

    rag = st.session_state.rag
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": "👋 Hi! I'm your KneeDoc AI Coach. How is your knee feeling today?"})

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "assistant":
                st.markdown(f"<div class='chat-bubble ai-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Type your message...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("KneeDoc AI is thinking..."):
            # Simulated typing effect
            typing_placeholder = st.empty()
            typing_placeholder.markdown("<div class='typing'>KneeDoc is typing...</div>", unsafe_allow_html=True)
            time.sleep(1.2)
            typing_placeholder.empty()

            profile = rag.extract_patient_info(user_input)
            context = rag.retrieve_context(user_input, profile)
            response = rag.generate_response(user_input, profile, context, st.session_state.messages)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


def page_faq():
    st.title("❓ FAQ")
    faq = {
        "Is this a medical app?": "No — this is an AI-assisted educational guide. Always consult your doctor.",
        "Do I need gym equipment?": "No, most routines are bodyweight only.",
        "Is my data stored?": "Your data stays local on your device."
    }
    for q, a in faq.items():
        with st.expander(q):
            st.write(a)


# === ROUTING ===
if not st.session_state.api_key:
    login_page()
else:
    sidebar_menu()
    if st.session_state.page == "Home":
        page_home()
    elif st.session_state.page == "Features":
        page_features()
    elif st.session_state.page == "Exercise Plan":
        page_exercise()
    elif st.session_state.page == "AI Coach":
        page_coach()
    elif st.session_state.page == "FAQ":
        page_faq()
