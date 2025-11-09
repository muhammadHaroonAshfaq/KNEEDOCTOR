# streamlit_app.py
"""KneeDoc AI — ChatGPT-style interface with collapsible sidebar, live streaming, typing animation, and timestamps."""

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
    layout="wide"
)


# --------------------------------------------------------
# MODERN CSS (ChatGPT-like)
# --------------------------------------------------------
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.stApp {background-color: #f0f2f6;}
.main {background-color: #f0f2f6;}
.top-nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 60px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 1.5rem;
    z-index: 1000;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.logo {font-size: 1.4rem; font-weight: 700; color: white;}
.toggle-btn {
    background: none; border: none; color: white;
    font-size: 1.5rem; cursor: pointer; margin-right: 1rem;
}
.chat-container {
    max-width: 900px;
    margin: 90px auto 120px auto;
    padding: 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.message-wrapper {display:flex; margin:1.5rem 0;}
.message-user{justify-content:flex-end;}
.message-assistant{justify-content:flex-start;}
.avatar{
    width:40px;height:40px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:1.2rem;flex-shrink:0;margin:0 1rem;
}
.avatar-user{background:linear-gradient(135deg,#667eea,#764ba2);}
.avatar-assistant{background:linear-gradient(135deg,#4CAF50,#45a049);}
.message-content{
    max-width:70%;padding:1rem 1.3rem;border-radius:16px;
    font-size:1rem;line-height:1.5;
}
.message-user .message-content{
    background:linear-gradient(135deg,#667eea,#764ba2);color:white;
}
.message-assistant .message-content{
    background:#f7f8fa;color:#222;border:1px solid #e0e0e0;
}
.timestamp{font-size:0.75rem;color:#888;text-align:right;margin-top:4px;}
.typing-indicator{display:flex;gap:4px;align-items:center;margin-left:60px;}
.typing-dot{
    width:8px;height:8px;border-radius:50%;background:#aaa;
    animation:blink 1.2s infinite;
}
.typing-dot:nth-child(2){animation-delay:0.2s;}
.typing-dot:nth-child(3){animation-delay:0.4s;}
@keyframes blink{0%,80%,100%{opacity:0;}40%{opacity:1;}}
.stButton>button{
    background:linear-gradient(135deg,#667eea,#764ba2);
    color:white;border:none;padding:0.8rem 2rem;
    border-radius:10px;font-weight:600;font-size:1rem;
    cursor:pointer;width:100%;transition:all 0.3s;
}
.stButton>button:hover{
    transform:translateY(-2px);
    box-shadow:0 10px 25px rgba(102,126,234,0.3);
}
.sidebar-custom {
    position: fixed;
    top: 60px;
    left: 0;
    width: 300px;
    height: 100%;
    background: white;
    border-right: 1px solid #ddd;
    padding: 1.5rem;
    overflow-y: auto;
    box-shadow: 2px 0 8px rgba(0,0,0,0.05);
    transition: transform 0.3s ease-in-out;
}
.sidebar-hidden {
    transform: translateX(-320px);
}
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
    "user_name": None,
    "sidebar_visible": True
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


# --------------------------------------------------------
# DATA LOADING
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
# TOP NAV BAR
# --------------------------------------------------------
col1, col2 = st.columns([0.1, 0.9])
with col1:
    if st.button("🍔", key="toggle_sidebar", help="Toggle sidebar"):
        st.session_state.sidebar_visible = not st.session_state.sidebar_visible

st.markdown('<div class="top-nav"><div class="logo">🦵 KneeDoc AI</div></div>', unsafe_allow_html=True)


# --------------------------------------------------------
# CUSTOM SIDEBAR
# --------------------------------------------------------
sidebar_class = "sidebar-custom" if st.session_state.sidebar_visible else "sidebar-custom sidebar-hidden"
st.markdown(f'<div class="{sidebar_class}">', unsafe_allow_html=True)

st.markdown("### ⚙️ Settings")

api_key = st.text_input("🔑 OpenAI API Key", type="password", placeholder="sk-...")
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
    st.info("👈 Enter your API key to start chatting")

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

st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------
# MAIN CHAT AREA
# --------------------------------------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if not api_key or not st.session_state.rag_initialized:
    st.markdown("""
    <div style="text-align:center; padding:6rem 2rem;">
        <h1 style="font-size:3rem; background:linear-gradient(135deg,#667eea,#764ba2);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        Welcome to KneeDoc AI</h1>
        <p style="color:#666;font-size:1.2rem;">Your Personal AI Exercise Coach for Knee Arthritis</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Get Started", use_container_width=True):
        st.info("👈 Enter your OpenAI API key in the sidebar to begin!")
else:
    # Initial message
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

    # Display chat messages
    for msg in st.session_state.messages:
        role_class = "message-user" if msg["role"] == "user" else "message-assistant"
        avatar = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f"""
        <div class="message-wrapper {role_class}">
            {'<div class="message-content">'+msg['content']+'</div><div class="avatar avatar-user">'+avatar+'</div>' if msg["role"]=="user" else '<div class="avatar avatar-assistant">'+avatar+'</div><div class="message-content">'+msg['content']+'</div>'}
        </div>
        <div class="timestamp">{msg['time']}</div>
        """, unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "time": datetime.now().strftime("%I:%M %p")
        })

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
