import streamlit as st
from datetime import datetime
from data_loader import KneeArthritisDataLoader
from rag_model import KneeArthritisRAG

st.set_page_config(page_title="KneeDoc AI", page_icon="🦵", layout="wide")

# --- CSS ---
st.markdown("""
<style>
body {
  background: radial-gradient(circle at top left, #1a1f35 0%, #0d1117 70%);
  color: #e6e8eb;
  transition: opacity 0.6s ease-in;
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
  animation: fadeIn 0.7s ease-in-out;
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
@keyframes fadeIn {
  from {opacity: 0; transform: translateY(10px);}
  to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)


# --- Session State Setup ---
defaults = {
    "api_key": None,
    "rag": None,
    "rag_initialized": False,
    "session_start": datetime.now(),
    "page": "Home"
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


# --- LOGIN PAGE ---
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
            st.session_state.page = "Home"
            st.rerun()
        else:
            st.error("Please enter a valid OpenAI API key (starts with 'sk-').")

    st.markdown("</div></div>", unsafe_allow_html=True)


# --- SIDEBAR NAVIGATION ---
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


# --- PAGE CONTENTS ---
def page_home():
    st.markdown("""
    <h1 style='text-align:center;'>Welcome to KneeDoc AI 🦵</h1>
    <p style='text-align:center;color:#aaa;'>Your personal AI-powered companion for knee arthritis care.</p>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.image("https://cdn-icons-png.flaticon.com/512/2920/2920243.png", width=180)
    st.write("""
    - Personalized exercise plans  
    - Step-by-step recovery coaching  
    - Progress monitoring and health tips  
    """)


def page_features():
    st.title("⚙️ Features")
    st.write("Explore what makes KneeDoc AI unique:")
    cols = st.columns(2)
    features = [
        ("🤖", "AI Coach", "Interactive chat-based knee rehabilitation support."),
        ("💪", "Custom Exercises", "Tailored routines based on your pain and flexibility."),
        ("📈", "Progress Tracker", "Track recovery metrics in real-time."),
        ("🔒", "Data Privacy", "Your health data stays on your device.")
    ]
    for i, (emoji, title, desc) in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div style='background:rgba(255,255,255,0.05);
                        border-radius:12px;
                        padding:1rem;
                        border:1px solid rgba(255,255,255,0.1);
                        margin-bottom:0.8rem;'>
                <h3>{emoji} {title}</h3>
                <p style='color:#aaa;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)


def page_exercise():
    st.title("💪 Your Exercise Plan")
    if not st.session_state.rag_initialized:
        st.warning("Please log in again to load your AI model.")
        return
    st.info("Your personalized knee exercise plan will appear here after chatting with the AI Coach.")
    st.json({"Example": "This is where the plan from RAG would load dynamically."})


def page_coach():
    st.title("🤖 AI Coach")
    if not st.session_state.rag_initialized:
        st.warning("Please log in again to use the AI Coach.")
        return

    rag = st.session_state.rag
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "👋 Hi! I'm your KneeDoc AI Coach. Tell me about your knee issue to begin."}]

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.markdown(f"🤖 **KneeDoc:** {msg['content']}")
        else:
            st.markdown(f"👤 **You:** {msg['content']}")

    user_input = st.chat_input("Type your message here...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            profile = rag.extract_patient_info(user_input)
            context = rag.retrieve_context(user_input, profile)
            response = rag.generate_response(user_input, profile, context, st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


def page_faq():
    st.title("❓ Frequently Asked Questions")
    faq = {
        "Is this a medical app?": "No, it’s an educational AI assistant. Always consult your doctor before any exercise.",
        "Do I need equipment?": "Mostly bodyweight-based exercises, but a mat or chair can help.",
        "Is my data safe?": "Yes — no personal data leaves your local machine."
    }
    for q, a in faq.items():
        with st.expander(q):
            st.write(a)


# --- MAIN LOGIC ---
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
