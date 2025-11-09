# streamlit_app.py
"""KneeDoc AI — ChatGPT-style interface with live streaming replies, typing animation, and timestamps"""

import streamlit as st
from datetime import datetime
import time
from data_loader import KneeArthritisDataLoader
from rag_model import KneeArthritisRAG

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="KneeDoc AI",
    page_icon="🦵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------------
# MODERN STYLING
# --------------------------------------------------------
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.stApp, .main {background-color: #0d1117;}
.chat-container {max-width:900px;margin:80px auto 120px auto;padding:0 2rem;}
.top-nav {position:fixed;top:0;left:0;right:0;height:60px;background:linear-gradient(135deg,#1a1f35,#0d1117);
display:flex;align-items:center;padding:0 2rem;z-index:1000;border-bottom:1px solid rgba(255,255,255,0.1);}
.logo {font-size:1.5rem;font-weight:700;background:linear-gradient(135deg,#667eea,#764ba2);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.message-wrapper{display:flex;margin:1.5rem 0;}
.message-user{justify-content:flex-end;}
.message-assistant{justify-content:flex-start;}
.avatar{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;
font-size:1.2rem;flex-shrink:0;margin:0 1rem;}
.avatar-user{background:linear-gradient(135deg,#667eea,#764ba2);}
.avatar-assistant{background:linear-gradient(135deg,#4CAF50,#45a049);}
.message-content{max-width:70%;padding:1rem 1.3rem;border-radius:16px;font-size:1rem;line-height:1.5;}
.message-user .message-content{background:linear-gradient(135deg,#667eea,#764ba2);color:white;
border-bottom-right-radius:4px;}
.message-assistant .message-content{background:rgba(255,255,255,0.05);color:#e6e8eb;
border:1px solid rgba(255,255,255,0.1);border-bottom-left-radius:4px;}
.timestamp{font-size:0.75rem;color:#888;text-align:right;margin-top:4px;}
.typing-indicator{display:flex;gap:4px;align-items:center;margin-left:60px;}
.typing-dot{width:8px;height:8px;border-radius:50%;background:#888;animation:blink 1.2s infinite;}
.typing-dot:nth-child(2){animation-delay:0.2s;}
.typing-dot:nth-child(3){animation-delay:0.4s;}
@keyframes blink{0%,80%,100%{opacity:0;}40%{opacity:1;}}
.stButton>button{background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;
padding:0.8rem 2rem;border-radius:10px;font-weight:600;font-size:1rem;cursor:pointer;width:100%;
transition:all 0.3s;}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 10px 25px rgba(102,126,234,0.4);}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# SESSION STATE
# --------------------------------------------------------
defaults = {
    "messages": [],
    "patient_profile": None,
    "current_plan": None,
    "exercise_progress": {},
    "session_start": datetime.now(),
    "rag_initialized": False,
    "user_name": None
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# --------------------------------------------------------
# LOADERS
# --------------------------------------------------------
@st.cache_resource
def load_data():
    loader = KneeArthritisDataLoader(data_dir="data")
    loader.load_all()
    return loader

@st.cache_resource
def initialize_rag(loader, api_key):
    return KneeArthritisRAG(loader, api_key)

# --------------------------------------------------------
# NAVBAR
# --------------------------------------------------------
st.markdown('<div class="top-nav"><div class="logo">🦵 KneeDoc AI</div></div>', unsafe_allow_html=True)

# --------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    if api_key:
        st.success("✅ API Key configured")
        if not st.session_state.rag_initialized:
            with st.spinner("Loading exercise database..."):
                try:
                    loader = load_data()
                    st.session_state.rag = initialize_rag(loader, api_key)
                    st.session_state.rag_initialized = True
                    st.success(f"✅ {len(loader.exercises)} exercises loaded")
                except Exception as e:
                    st.error(f"❌ Error loading data: {e}")
    else:
        st.info("👈 Enter your API key to get started.")

    st.divider()

    if st.session_state.patient_profile:
        prof = st.session_state.patient_profile
        st.markdown(f"""
        **👤 {st.session_state.user_name or 'User'}**
        - Age: {prof.get('age', 'N/A')}  
        - Severity: {prof.get('severity', 'N/A')}/4  
        - Pain: {prof.get('pain_level', 'N/A')}/10
        """)

    if st.button("🔄 New Session"):
        for k in list(st.session_state.keys()):
            if k not in ["rag", "rag_initialized"]:
                del st.session_state[k]
        st.rerun()

# --------------------------------------------------------
# MAIN CHAT AREA
# --------------------------------------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if not api_key or not st.session_state.rag_initialized:
    st.markdown("""
    <div style="text-align:center; padding:6rem 2rem;">
        <h1 style="font-size:3rem;background:linear-gradient(135deg,#667eea,#764ba2);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        Welcome to KneeDoc AI</h1>
        <p style="color:#9aa0b6;font-size:1.2rem;">Your Personal AI Exercise Coach for Knee Arthritis</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Get Started", use_container_width=True):
        st.info("👈 Enter your OpenAI API key in the sidebar to begin!")
else:
    # --------------------------------------------------------
    # INITIAL MESSAGE
    # --------------------------------------------------------
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "👋 **Hi! I'm your KneeDoc AI Coach.**\n\n"
                "Please share:\n"
                "- Your name\n"
                "- Your age\n"
                "- A brief description of your knee condition\n\n"
                "*Example:* 'I'm Sarah, 65, mild arthritis, pain when climbing stairs.'"
            ),
            "time": datetime.now().strftime("%I:%M %p")
        })

    # --------------------------------------------------------
    # RENDER CHAT HISTORY
    # --------------------------------------------------------
    for msg in st.session_state.messages:
        role_class = "message-user" if msg["role"] == "user" else "message-assistant"
        avatar = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f"""
        <div class="message-wrapper {role_class}">
            {'<div class="message-content">'+msg['content']+'</div><div class="avatar avatar-user">'+avatar+'</div>' if msg["role"]=="user" else '<div class="avatar avatar-assistant">'+avatar+'</div><div class="message-content">'+msg['content']+'</div>'}
        </div>
        <div class="timestamp">{msg['time']}</div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # USER INPUT + STREAMING REPLY
    # --------------------------------------------------------
    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "time": datetime.now().strftime("%I:%M %p")
        })

        # Typing indicator
        typing_placeholder = st.empty()
        with typing_placeholder.container():
            st.markdown("""
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            """, unsafe_allow_html=True)
        time.sleep(1.5)

        try:
            rag = st.session_state.rag
            if not st.session_state.patient_profile:
                profile = rag.extract_patient_info(user_input)
                st.session_state.patient_profile = profile
                st.session_state.user_name = next(
                    (w.strip(",.") for w in user_input.split() if w[0].isupper()), "User"
                )
                ctx = rag.retrieve_context(user_input, profile)
                plan = rag.create_exercise_plan(profile, ctx)
                st.session_state.current_plan = plan
                full_reply = rag.generate_response(user_input, profile, ctx, st.session_state.messages)
            else:
                ctx = rag.retrieve_context(user_input, st.session_state.patient_profile)
                full_reply = rag.generate_response(user_input, st.session_state.patient_profile, ctx, st.session_state.messages)

            # Live streaming effect
            typing_placeholder.empty()
            reply_box = st.empty()
            displayed = ""
            for token in full_reply.split():
                displayed += token + " "
                reply_box.markdown(f"""
                <div class="message-wrapper message-assistant">
                    <div class="avatar avatar-assistant">🤖</div>
                    <div class="message-content">{displayed.strip()}</div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.03)
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_reply,
                "time": datetime.now().strftime("%I:%M %p")
            })
        except Exception as e:
            typing_placeholder.empty()
            st.error(f"⚠️ {e}")
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
