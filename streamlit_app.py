import streamlit as st
from datetime import datetime
import time
from data_loader import KneeArthritisDataLoader
from rag_model import KneeArthritisRAG

st.set_page_config(page_title="KneeDoc AI", page_icon="🦵", layout="wide")

# === DARK THEME CSS ===
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
h1,h2,h3,h4,h5,h6,label,p,span,div { color: #ffffff !important; }
section[data-testid="stSidebar"] {
  background: rgba(0,0,20,0.85)!important; border-right:1px solid rgba(0,153,255,0.2);
}
.card {
  background: rgba(0,51,102,0.4);
  border-radius: 12px;
  padding: 1.2rem; margin-bottom: 1rem;
  border: 1px solid rgba(0,153,255,0.3);
  box-shadow: 0 0 8px rgba(0,153,255,0.2);
}
.chat-bubble {
  padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem;
  max-width: 80%; word-wrap: break-word;
}
.user-bubble {
  background: linear-gradient(135deg,#0055aa,#0099ff);
  color:white; margin-left:auto;
}
.ai-bubble {
  background: linear-gradient(135deg,#1a2233,#223a5f);
  color:#e5e7eb; margin-right:auto;
}
.typing { font-style: italic; color: #8ab4f8; padding: 0.5rem; }
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
    "intake_step": None,
    "intake_done": False,
    "patient_profile": {}
}.items():
    st.session_state.setdefault(k, v)


# === LOGIN PAGE ===
def login_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.image("https://cdn.pixabay.com/photo/2017/03/14/15/55/exercise-2140760_1280.png", width=260)
    st.markdown("<h2>🦵 KneeDoc AI</h2>", unsafe_allow_html=True)
    st.markdown("<p>Your Personal AI Exercise Coach for Knee Arthritis</p>", unsafe_allow_html=True)

    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    if st.button("Continue", use_container_width=True):
        if api_key.startswith("sk-"):
            with st.spinner("Initializing your AI coach..."):
                loader = KneeArthritisDataLoader()
                st.session_state.rag = KneeArthritisRAG(loader, api_key)
                st.session_state.rag_initialized = True
                st.session_state.api_key = api_key
            st.success("✅ Login successful! Redirecting...")
            time.sleep(0.8)
            st.session_state.page = "Home"
            st.rerun()
        else:
            st.error("Please enter a valid OpenAI API key.")
    st.markdown("</div></div>", unsafe_allow_html=True)


# === SIDEBAR ===
def sidebar_menu():
    with st.sidebar:
        st.title("🦵 KneeDoc AI")
        st.success("Logged in successfully")
        st.markdown("---")
        menu = st.radio("📍 Navigation", [
            "Home", "Features", "Exercise Plan", "AI Coach", "FAQ"
        ], index=["Home", "Features", "Exercise Plan", "AI Coach", "FAQ"].index(st.session_state.page))
        st.session_state.page = menu
        st.markdown("---")
        st.caption("Session started: " + st.session_state.session_start.strftime("%I:%M %p"))


# === HOME PAGE ===
def page_home():
    st.markdown("<h1 style='text-align:center;'>Welcome to KneeDoc AI 🦵</h1>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2920/2920243.png", width=200)
    st.markdown("<div class='card'>• Personalized AI recommendations</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>• Guided exercises for recovery</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>• Real-time tracking and insights</div>", unsafe_allow_html=True)


# === FEATURES PAGE ===
def page_features():
    st.title("⚙️ Features")
    features = [
        ("🤖", "AI Coach", "Interactive chat-based knee rehabilitation support."),
        ("💪", "Custom Exercises", "Tailored routines based on pain and flexibility."),
        ("📈", "Progress Tracker", "Monitor recovery progress in real-time."),
        ("🔒", "Data Privacy", "Your data stays local and secure.")
    ]
    for emoji, title, desc in features:
        st.markdown(f"<div class='card'><h3>{emoji} {title}</h3><p style='color:#ccc;'>{desc}</p></div>", unsafe_allow_html=True)


# === EXERCISE PAGE ===
def page_exercise():
    st.title("💪 Exercise Plan")
    if not st.session_state.rag_initialized:
        st.warning("Please log in again to access your exercise plan.")
        return
    st.info("Personalized exercise routines will appear here after AI analysis.")
    st.json({"Example": "Sample plan generated from RAG context."})


# === AI COACH PAGE (CONVERSATIONAL FLOW) ===
def page_coach():
    st.title("🤖 AI Coach")
    if not st.session_state.rag_initialized:
        st.warning("Please log in again to use the AI Coach.")
        return

    rag = st.session_state.rag
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Hi! I'm your KneeDoc AI Coach. Let's start with your name — what should I call you?"
        })
        st.session_state.intake_step = "ask_name"

    # Render chat
    for msg in st.session_state.messages:
        bubble = "ai-bubble" if msg["role"] == "assistant" else "user-bubble"
        st.markdown(f"<div class='chat-bubble {bubble}'>{msg['content']}</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("KneeDoc AI is typing..."):
            time.sleep(1)

            # === Conversational Intake Flow ===
            if not st.session_state.intake_done:
                step = st.session_state.intake_step
                profile = st.session_state.patient_profile

                if step == "ask_name":
                    profile["name"] = user_input.strip().split(" ")[0]
                    reply = f"Nice to meet you, {profile['name']}! 😊 How old are you?"
                    st.session_state.intake_step = "ask_age"

                elif step == "ask_age":
                    try:
                        age = int("".join([c for c in user_input if c.isdigit()]))
                        profile["age"] = age
                        reply = "Got it! What kind of knee problem are you facing — pain, stiffness, or limited movement?"
                        st.session_state.intake_step = "ask_problem"
                    except:
                        reply = "Please enter a valid age (e.g., 35)."

                elif step == "ask_problem":
                    profile["problem"] = user_input.strip()
                    reply = "On a scale of 1–10, how severe is your knee pain right now?"
                    st.session_state.intake_step = "ask_pain"

                elif step == "ask_pain":
                    try:
                        pain = int("".join([c for c in user_input if c.isdigit()]))
                        profile["pain_level"] = pain
                        st.session_state.intake_done = True
                        reply = f"Thanks! Based on your pain level ({pain}/10), I’ll create your personalized exercise plan 🏋️"
                    except:
                        reply = "Please rate your pain between 1 and 10."

                else:
                    reply = "All details collected! You can now ask for exercises anytime 💪"

            # === After Intake ===
            else:
                profile = st.session_state.patient_profile
                context = rag.retrieve_context(user_input, profile)
                reply = rag.generate_response(user_input, profile, context, st.session_state.messages)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()


# === FAQ PAGE ===
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
