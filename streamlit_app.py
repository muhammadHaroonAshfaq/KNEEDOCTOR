# streamlit_app.py
"""KneeDoc AI — ChatGPT-style interface with collapsible sidebar, live streaming, typing animation, and timestamps."""

import streamlit as st
from datetime import datetime
import time
# Assuming 'data_loader' and 'rag_model' are available and correct
from data_loader import KneeArthritisDataLoader
from rag_model import KneeArthritisRAG


# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="KneeDoc AI",
    page_icon="🦵",
    # Changed to 'centered' for better control over the main chat width
    layout="centered" 
)


# --------------------------------------------------------
# MODERN CHATGPT-LIKE CSS (Optimized for Alignment)
# --------------------------------------------------------
st.markdown("""
<style>
/* Base Streamlit Overrides */
#MainMenu, header, footer {visibility: hidden;}
.stApp {background-color: #ffffff;} 
.main {background-color: #f0f2f6;} 
.css-1rs6k0q {padding-top: 60px;} /* Push content down to clear fixed nav bar */
.stChatInput {
    position: fixed;
    bottom: 0;
    width: 100%;
    /* Ensure chat input is visible and centered */
    max-width: 800px; 
    left: 50%;
    transform: translateX(-50%);
    background: #f0f2f6; /* Match main body background */
    padding: 10px 0;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.05);
}


/* Fixed Top Navigation Bar */
.top-nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 60px;
    background: linear-gradient(135deg, #5c6bc0, #7986cb); 
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 1.5rem;
    z-index: 1000;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.logo {font-size: 1.6rem; font-weight: 700; color: white;}
.toggle-btn {display: none;} 

/* Main Chat Container - Adjusted for reliable clearance and width */
.chat-container {
    max-width: 800px; 
    /* Increased margin-bottom to clear the fixed stChatInput */
    margin: 30px auto 100px auto; 
    padding: 1.5rem 1rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

/* Message Structure - CRITICAL FIX: Ensures alignment and timestamp placement */
.message-full-wrapper {
    margin: 1.5rem 0; /* Clear spacing between messages */
}
.message-wrapper {
    display: flex; 
    align-items: flex-end; 
    gap: 10px; 
}
.message-user {
    justify-content: flex-end;
}
.message-assistant {
    justify-content: flex-start;
}
.avatar {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
    color: white;
}
.avatar-user {
    background: linear-gradient(135deg, #5c6bc0, #7986cb);
}
.avatar-assistant {
    background: linear-gradient(135deg, #4CAF50, #81c784);
}
.message-content {
    max-width: 75%; 
    padding: 1rem 1.3rem; 
    border-radius: 20px; 
    font-size: 1rem; line-height: 1.5;
    word-break: break-word; /* Prevents overflow issues */
}
.message-user .message-content {
    background: linear-gradient(135deg, #5c6bc0, #7986cb);
    color: white;
    border-top-right-radius: 4px;
}
.message-assistant .message-content {
    background: #eef1f6; 
    color: #333;
    border-top-left-radius: 4px;
}

/* Timestamp - FIXED: Aligned directly below the message content */
.timestamp {
    font-size: 0.7rem;
    color: #999;
    /* Move to a separate flex-item for better control */
    text-align: right;
    margin-top: 5px;
}
.user-timestamp {
    text-align: right;
}
.assistant-timestamp {
    text-align: left;
    margin-left: 46px; /* Push it under the message content, aligning with the bubble's start */
}


/* Typing Indicator - Corrected horizontal alignment */
.typing-indicator {
    display: flex; gap: 6px; align-items: center; 
    margin-left: 46px; /* Align under the assistant's avatar */
    margin-top: 10px;
}
.typing-dot {
    width: 8px; height: 8px; border-radius: 50%; background: #aaa;
    animation: blink 1.2s infinite;
}
.typing-dot:nth-child(2) {animation-delay: 0.2s;}
.typing-dot:nth-child(3) {animation-delay: 0.4s;}
@keyframes blink {0%, 80%, 100% {opacity: 0;} 40% {opacity: 1;}}

/* Sidebar/Button Styling - Improved look */
.stButton>button {
    background: linear-gradient(135deg, #5c6bc0, #7986cb); 
    color: white; border: none; padding: 0.7rem 1.5rem;
    border-radius: 8px; font-weight: 600; font-size: 0.95rem;
    cursor: pointer; width: 100%; transition: all 0.3s;
}
.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(92, 107, 192, 0.3);
}
/* Adjust Streamlit's native sidebar styling for better integration */
.stSidebar {
    padding-top: 60px; 
    box-shadow: 2px 0 8px rgba(0,0,0,0.05);
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
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


# --------------------------------------------------------
# DATA LOADING & CACHING (Integration Unchanged)
# --------------------------------------------------------
@st.cache_resource
def load_data():
    """Loads exercise data."""
    loader = KneeArthritisDataLoader(data_dir="data")
    loader.load_all()
    return loader


@st.cache_resource
def initialize_rag(_loader, api_key):
    """Initializes the RAG model."""
    return KneeArthritisRAG(_loader, api_key)


# --------------------------------------------------------
# TOP NAV BAR
# --------------------------------------------------------
st.markdown("""
<div class="top-nav">
    <div class="logo">🦵 KneeDoc AI</div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    # The API Key input remains the same
    api_key = st.text_input("🔑 OpenAI API Key", type="password", placeholder="sk-...")
    
    if api_key:
        st.success("✅ API Key configured")
        if not st.session_state.rag_initialized:
            with st.spinner("Loading exercise database..."):
                try:
                    # Integration with data_loader and rag_model remains the same
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
        **👤 Patient Profile**
        - **Name:** {st.session_state.user_name or 'User'}
        - **Age:** {prof.get('age', 'N/A')}
        - **Severity:** {prof.get('severity', 'N/A')}/4
        - **Pain:** {prof.get('pain_level', 'N/A')}/10
        """)

    if st.button("🔄 New Session", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k not in ["rag", "rag_initialized", "api_key"]:
                del st.session_state[k]
        st.rerun()


# --------------------------------------------------------
# MAIN CHAT AREA
# --------------------------------------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if not api_key or not st.session_state.rag_initialized:
    # Initial landing page without API key
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem;">
        <h1 style="font-size:3rem; 
        background:linear-gradient(135deg, #5c6bc0, #7986cb);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        Welcome to KneeDoc AI</h1>
        <p style="color:#666;font-size:1.1rem; margin-top:10px;">Your Personal AI Exercise Coach for Knee Arthritis</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("👈 Please enter your OpenAI API key in the sidebar to begin!")
else:
    # Initialize first assistant message if starting new
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "👋 **Hi! I'm your KneeDoc AI Coach.**\n\n"
                "Please share some details to create your personalized plan:\n"
                "- Your name and age\n"
                "- Your general knee condition (e.g., mild arthritis, recovering from surgery)\n"
                "- Your pain level (1-10)\n\n"
                "*Example:* 'I'm Sarah, 65, mild arthritis, pain when climbing stairs (5/10).'"
            ),
            "time": datetime.now().strftime("%I:%M %p")
        })

    # Display all messages
    for msg in st.session_state.messages:
        role_class = "message-user" if msg["role"] == "user" else "message-assistant"
        avatar = "👤" if msg["role"] == "user" else "🤖"
        
        # CRITICAL FIX: The HTML is structured for two separate lines/alignments
        if msg["role"] == "user":
            message_html = f"""
            <div class="message-full-wrapper">
                <div class="message-wrapper {role_class}">
                    <div class="message-content">{msg['content']}</div>
                    <div class="avatar avatar-{msg["role"]}">{avatar}</div>
                </div>
                <div class="timestamp user-timestamp">{msg['time']}</div>
            </div>
            """
        else:
             message_html = f"""
            <div class="message-full-wrapper">
                <div class="message-wrapper {role_class}">
                    <div class="avatar avatar-{msg["role"]}">{avatar}</div>
                    <div class="message-content">{msg['content']}</div>
                </div>
                <div class="timestamp assistant-timestamp">{msg['time']}</div>
            </div>
            """

        st.markdown(message_html, unsafe_allow_html=True)

    # Chat Input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "time": datetime.now().strftime("%I:%M %p")
        })
        st.rerun() 

    # If the last message was from the user, generate a response
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        
        # Display typing indicator while processing
        typing_placeholder = st.empty()
        with typing_placeholder.container():
            st.markdown("""
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            """, unsafe_allow_html=True)
        time.sleep(1.0) 

        # Response Generation Logic (Integration Unchanged)
        try:
            rag = st.session_state.rag
            
            # This logic remains untouched to maintain integration with rag_model
            if not st.session_state.patient_profile:
                profile = rag.extract_patient_info(user_input)
                st.session_state.patient_profile = profile
                st.session_state.user_name = next(
                    (w.strip(",.") for w in user_input.split() if w[0].isupper()), "User"
                )
                ctx = rag.retrieve_context(user_input, profile)
                # plan = rag.create_exercise_plan(profile, ctx) # Commented out as before
                # st.session_state.current_plan = plan 
                full_reply = rag.generate_response(user_input, profile, ctx, st.session_state.messages)
            else:
                ctx = rag.retrieve_context(user_input, st.session_state.patient_profile)
                full_reply = rag.generate_response(user_input, st.session_state.patient_profile, ctx, st.session_state.messages)

            typing_placeholder.empty()
            
            # Live Streaming Display
            reply_container = st.empty()
            displayed_content = ""
            current_time_str = datetime.now().strftime("%I:%M %p")
            
            # The streaming loop
            for token in full_reply.split():
                displayed_content += token + " "
                
                # FIXED: HTML for streaming response display, uses the same alignment fix
                streaming_html = f"""
                <div class="message-full-wrapper">
                    <div class="message-wrapper message-assistant">
                        <div class="avatar avatar-assistant">🤖</div>
                        <div class="message-content">{displayed_content.strip()}</div>
                    </div>
                    <div class="timestamp assistant-timestamp">{current_time_str}</div>
                </div>
                """
                reply_container.markdown(streaming_html, unsafe_allow_html=True)
                time.sleep(0.03)

            # Save the final message to state
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_reply,
                "time": current_time_str
            })
            st.rerun() 

        except Exception as e:
            typing_placeholder.empty()
            st.error(f"⚠️ An error occurred during response generation. Check your API key and model logic: {e}")
            
st.markdown("</div>", unsafe_allow_html=True)
