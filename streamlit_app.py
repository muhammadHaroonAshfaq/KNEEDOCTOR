import streamlit as st
from datetime import datetime
import time
from data_loader import KneeArthritisDataLoader
from rag_model import KneeArthritisRAG

st.set_page_config(page_title="Knee Rehab Assistant", page_icon="🏋️", layout="wide")

# === GLOBAL STYLES ===
st.markdown("""
<style>
.stApp {
  background: linear-gradient(160deg, #000000 0%, #001a33 100%) !important;
  color: #ffffff !important;
}
[data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
  background: transparent !important;
  color: #ffffff !important;
}
h1, h2, h3, h4, h5, h6, label, p, span, div { color: #ffffff !important; }
section[data-testid="stSidebar"] {
  background: rgba(0, 0, 20, 0.85) !important;
  color: white !important;
  border-right: 1px solid rgba(0,153,255,0.2);
}
.card {
  background: rgba(0,51,102,0.4);
  border-radius: 12px;
  padding: 1.2rem;
  margin-bottom: 1rem;
  border: 1px solid rgba(0,153,255,0.3);
  box-shadow: 0 0 8px rgba(0,153,255,0.2);
}

/* Floating Restart Chat Button */
.restart-btn {
  position: fixed;
  top: 20px;
  right: 25px;
  background-color: white;
  color: black;
  border: none;
  border-radius: 50px;
  padding: 10px 18px;
  font-weight: 600;
  box-shadow: 0 2px 10px rgba(255,255,255,0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1000;
}
.restart-btn:hover {
  background-color: black;
  color: white;
  box-shadow: 0 0 15px rgba(255,255,255,0.7);
  transform: scale(1.05);
}

/* Chat bubbles */
.chat-bubble {padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem; max-width: 80%; word-wrap: break-word;}
.user-bubble {background: linear-gradient(135deg, #0055aa, #0099ff); align-self: flex-end; color: white; margin-left: auto;}
.ai-bubble {background: linear-gradient(135deg, #1a2233, #223a5f); color: #e5e7eb; align-self: flex-start;}
.typing {font-style: italic; color: #8ab4f8; padding: 0.5rem;}
</style>
""", unsafe_allow_html=True)

# === SESSION STATE ===
for k, v in {
    "api_key": None,
    "rag": None,
    "rag_initialized": False,
    "session_start": datetime.now(),
    "page": "Home",
    "messages": [],
}.items():
    st.session_state.setdefault(k, v)

# === LOGIN PAGE ===
def login_page():
    st.markdown('<div class="login-container" style="text-align:center;">', unsafe_allow_html=True)
    st.image("https://cdn.pixabay.com/photo/2017/03/14/15/55/exercise-2140760_1280.png", width=260)
    st.markdown("<h2>🏋️ Knee Rehab Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<p>Your AI-powered knee rehabilitation coach</p>", unsafe_allow_html=True)

    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    if st.button("Continue"):
        if api_key.startswith("sk-"):
            st.session_state.api_key = api_key
            with st.spinner("Initializing your AI coach..."):
                loader = KneeArthritisDataLoader(data_dir="data")
                loader.load_all()
                st.session_state.rag = KneeArthritisRAG(loader, api_key)
                st.session_state.rag_initialized = True
            st.success("✅ Login successful! Redirecting...")
            time.sleep(1)
            st.session_state.page = "AI Coach"
            st.rerun()
        else:
            st.error("Please enter a valid API key starting with 'sk-'")

# === SIDEBAR ===
def sidebar_menu():
    with st.sidebar:
        st.title("🏋️ Knee Rehab Assistant")
        st.success("Logged in successfully")
        menu = st.radio("📍 Navigation", ["Home", "Features", "AI Coach", "FAQ"],
                        index=["Home", "Features", "AI Coach", "FAQ"].index(st.session_state.page))
        st.session_state.page = menu
        st.caption("Session started: " + st.session_state.session_start.strftime("%I:%M %p"))

# === PAGES ===
def page_home():
    st.title("Welcome to Knee Rehab Assistant 🦵")
    st.markdown("<div class='card'>• Personalized AI guidance for knee health</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>• Step-by-step pain and recovery analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>• Safe and guided exercises</div>", unsafe_allow_html=True)

def page_features():
    st.title("⚙️ Features")
    features = [
        ("🤖", "AI Rehab Coach", "Conversational assistant that guides you through knee recovery."),
        ("💪", "Custom Exercises", "Tailored workouts for your pain level and flexibility."),
        ("📊", "Progress Tracker", "Monitor improvements in mobility."),
        ("🔒", "Data Privacy", "Your data stays local and secure.")
    ]
    for emoji, title, desc in features:
        st.markdown(f"<div class='card'><h3>{emoji} {title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)

def page_coach():
    st.title("🤖 AI Rehab Coach")

    if not st.session_state.rag_initialized:
        st.warning("Please log in again to use the AI Coach.")
        return

    rag = st.session_state.rag

    # Floating Restart Button
    st.markdown('<button class="restart-btn" onclick="window.location.reload()">🔄 Restart Chat</button>', unsafe_allow_html=True)

    # Initialize messages
    if not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": "👋 Hi! What’s your name?"}]

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            bubble_class = "ai-bubble" if msg["role"] == "assistant" else "user-bubble"
            st.markdown(f"<div class='chat-bubble {bubble_class}'>{msg['content']}</div>", unsafe_allow_html=True)

    # Auto scroll
    st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)

    user_input = st.chat_input("Type your message...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

    # After user reply
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_message = st.session_state.messages[-1]["content"]

        with st.spinner("Knee Rehab Assistant is thinking..."):
            typing_placeholder = st.empty()
            typing_placeholder.markdown("<div class='typing'>Assistant is typing...</div>", unsafe_allow_html=True)
            time.sleep(1.2)
            typing_placeholder.empty()

            ai_response, step = rag.conversational_intake(user_message)

            if step == "done":
                profile = st.session_state.get("patient_profile", {})
                context = rag.retrieve_context(user_message, profile)
                ai_response = rag.generate_response(user_message, profile, context, st.session_state.messages)

        # Typing animation
        bubble_placeholder = st.empty()
        ai_text = ""
        for char in ai_response:
            ai_text += char
            bubble_placeholder.markdown(f"<div class='chat-bubble ai-bubble'>{ai_text}</div>", unsafe_allow_html=True)
            time.sleep(0.02)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.rerun()

def page_faq():
    st.title("❓ FAQ")
    faq = {
        "Is this a medical app?": "No — this is an AI-assisted educational tool. Always consult your physician.",
        "Do I need gym equipment?": "No, most exercises are bodyweight-based.",
        "Is my data stored?": "No, your data stays local and private."
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
    elif st.session_state.page == "AI Coach":
        page_coach()
    elif st.session_state.page == "FAQ":
        page_faq()
