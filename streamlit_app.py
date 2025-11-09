import streamlit as st
from datetime import datetime
import time
from data_loader import KneeArthritisDataLoader
from rag_model import KneeArthritisRAG

st.set_page_config(page_title="KneeDoc AI", page_icon="🦵", layout="wide")

# === DARK THEME + GRADIENT CHAT ===
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
h1,h2,h3,h4,h5,h6,p,span,div,label {
  color: #ffffff !important;
  font-family: "Inter", sans-serif;
}
section[data-testid="stSidebar"] {
  background: rgba(0,0,20,0.85)!important;
  border-right: 1px solid rgba(0,153,255,0.2);
}
.card {
  background: rgba(0,51,102,0.4);
  border-radius: 12px;
  padding: 1.2rem; margin-bottom: 1rem;
  border: 1px solid rgba(0,153,255,0.3);
  box-shadow: 0 0 8px rgba(0,153,255,0.2);
}
.chat-bubble {
  padding: 1rem 1.2rem;
  border-radius: 14px;
  margin-bottom: 0.8rem;
  max-width: 80%;
  line-height: 1.5;
  word-wrap: break-word;
  animation: fadeIn 0.6s ease;
}
.user-bubble {
  background: linear-gradient(135deg, #0044aa, #0099ff);
  color: white;
  margin-left: auto;
  border: 1px solid rgba(255,255,255,0.2);
  box-shadow: 0 0 10px rgba(0,153,255,0.3);
}
.ai-bubble {
  background: linear-gradient(135deg, #121e35, #1e3258);
  color: #e5e7eb;
  margin-right: auto;
  border: 1px solid rgba(0,153,255,0.2);
  box-shadow: 0 0 10px rgba(0,153,255,0.15);
  animation: breathe 3s ease-in-out infinite;
}
.typing {
  color: #8ab4f8;
  font-style: italic;
  padding: 0.6rem 1rem;
  border-left: 3px solid #33ccff;
  animation: fadeIn 0.5s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes breathe {
  0%, 100% { box-shadow: 0 0 10px rgba(0,153,255,0.2); }
  50% { box-shadow: 0 0 25px rgba(0,153,255,0.5); }
}
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
    "patient_profile": {},
    "exercise_plan": None
}.items():
    st.session_state.setdefault(k, v)


# === LOGIN PAGE ===
def login_page():
    st.markdown("<div style='text-align:center; margin-top:10%;'>", unsafe_allow_html=True)
    st.image("https://cdn.pixabay.com/photo/2017/03/14/15/55/exercise-2140760_1280.png", width=280)
    st.markdown("<h2 style='background: linear-gradient(135deg,#33ccff,#0077ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>🦵 KneeDoc AI</h2>", unsafe_allow_html=True)
    st.caption("Your Personal AI Exercise Coach for Knee Arthritis")

    api_key = st.text_input("Enter OpenAI API Key", type="password", placeholder="sk-...")
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
            st.error("Please enter a valid OpenAI API key (starts with 'sk-').")
    st.markdown("</div>", unsafe_allow_html=True)


# === SIDEBAR MENU ===
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


# === AI COACH PAGE ===
def page_coach():
    st.title("🤖 AI Coach")

    if not st.session_state.rag_initialized:
        st.warning("Please log in again to use the AI Coach.")
        return

    rag = st.session_state.rag

    # Initial message
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Hi! I'm your KneeDoc AI Coach. Let's begin — what should I call you?"
        })
        st.session_state.intake_step = "ask_name"

    # Display chat bubbles
    chat_box = st.container()
    with chat_box:
        for msg in st.session_state.messages:
            bubble = "ai-bubble" if msg["role"] == "assistant" else "user-bubble"
            st.markdown(f"<div class='chat-bubble {bubble}'>{msg['content']}</div>", unsafe_allow_html=True)

    # User input
    user_input = st.chat_input("Type your message...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("KneeDoc is thinking..."):
            typing = st.empty()
            typing.markdown("<div class='typing'>💬 KneeDoc is typing...</div>", unsafe_allow_html=True)
            time.sleep(1.2)
            typing.empty()

            # Intake conversation
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
                        st.session_state.exercise_plan = rag.create_exercise_plan(profile, {})
                        reply = f"Thanks! Based on your pain level ({pain}/10), here’s your personalized exercise plan 🏋️"
                    except:
                        reply = "Please rate your pain between 1 and 10."

                else:
                    reply = "All details collected! You can now ask for exercises anytime 💪"

            else:
                profile = st.session_state.patient_profile
                context = rag.retrieve_context(user_input, profile)
                reply = rag.generate_response(user_input, profile, context, st.session_state.messages)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    # Show exercise plan when ready
    if st.session_state.intake_done and st.session_state.exercise_plan:
        st.markdown("### 🏋️ Your Personalized Exercise Plan")
        for ex in st.session_state.exercise_plan["exercises"]:
            with st.expander(f"{ex['name']} (Difficulty {ex['difficulty']}/4)"):
                st.markdown(f"**Category:** {ex['category']}")
                st.markdown(f"**Reps/Sets:** {ex['reps']} reps × {ex['sets']} sets")
                st.markdown("**Instructions:**")
                for i in ex["instructions"]:
                    st.markdown(f"- {i}")
                st.markdown(f"**Primary Benefit:** {ex['category']} improvement")


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


# === ROUTER ===
if not st.session_state.api_key:
    login_page()
else:
    sidebar_menu()
    if st.session_state.page == "Home":
        page_home()
    elif st.session_state.page == "AI Coach":
        page_coach()
    elif st.session_state.page == "FAQ":
        page_faq()
