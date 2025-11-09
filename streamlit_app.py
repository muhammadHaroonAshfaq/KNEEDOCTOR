# streamlit_app.py
"""Enhanced Streamlit app for Knee Arthritis Exercise Guide"""

import streamlit as st
from datetime import datetime
import os
from data_loader import KneeArthritisDataLoader
from rag_model import KneeArthritisRAG

# Page configuration
st.set_page_config(
    page_title="Knee Arthritis Exercise Guide",
    page_icon="🦵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Chat messages */
    .chat-message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 5px solid #764ba2;
    }
    
    .chat-message-assistant {
        background: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 5px solid #4CAF50;
    }
    
    /* Profile card */
    .profile-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .profile-card h3 {
        color: #667eea;
        margin-top: 0;
    }
    
    .profile-item {
        padding: 0.5rem 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .profile-item:last-child {
        border-bottom: none;
    }
    
    /* Exercise plan */
    .exercise-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .exercise-card:hover {
        transform: translateX(5px);
    }
    
    .exercise-completed {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    }
    
    /* Progress bar */
    .progress-container {
        background: #e0e0e0;
        border-radius: 10px;
        height: 25px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
        height: 100%;
        border-radius: 10px;
        text-align: center;
        line-height: 25px;
        color: white;
        font-weight: bold;
        transition: width 0.3s ease;
    }
    
    /* Welcome box */
    .welcome-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .welcome-box h2 {
        color: white;
        margin-top: 0;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Info boxes */
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #e8f5e9;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'patient_profile' not in st.session_state:
    st.session_state.patient_profile = None
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None
if 'exercise_progress' not in st.session_state:
    st.session_state.exercise_progress = {}
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()
if 'rag_initialized' not in st.session_state:
    st.session_state.rag_initialized = False
if 'conversation_stage' not in st.session_state:
    st.session_state.conversation_stage = 'welcome'  # welcome, collecting_info, active
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# Load data and initialize RAG (cached)
@st.cache_resource
def load_data():
    """Load dataset"""
    loader = KneeArthritisDataLoader(data_dir="data")
    loader.load_all()
    return loader

@st.cache_resource
def initialize_rag(_loader, api_key):
    """Initialize RAG model"""
    return KneeArthritisRAG(_loader, api_key)

# Header
st.markdown("""
<div class="main-header">
    <h1>🦵 Knee Arthritis Exercise Guide</h1>
    <p>Your Personal AI Exercise Coach - Helping You Move Better, Feel Better</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # API Key input
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key to get started"
    )
    
    if api_key:
        st.markdown('<div class="success-box">✅ API Key configured</div>', unsafe_allow_html=True)
        
        # Initialize RAG only once
        if not st.session_state.rag_initialized:
            with st.spinner("🔄 Loading exercise database..."):
                try:
                    loader = load_data()
                    st.session_state.rag = initialize_rag(loader, api_key)
                    st.session_state.rag_initialized = True
                    st.success(f"✅ Loaded {len(loader.exercises)} exercises")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.markdown('<div class="info-box">ℹ️ Please enter your OpenAI API key to begin</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Patient Profile
    st.markdown("### 📊 Your Profile")
    if st.session_state.patient_profile:
        profile = st.session_state.patient_profile
        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-item"><strong>Name:</strong> {st.session_state.user_name or 'Not provided'}</div>
            <div class="profile-item"><strong>Age:</strong> {profile.get('age', 'N/A')}</div>
            <div class="profile-item"><strong>Severity:</strong> {profile.get('severity', 'N/A')}/4</div>
            <div class="profile-item"><strong>Pain Level:</strong> {profile.get('pain_level', 'N/A')}/10</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">👋 Start chatting to create your profile!</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Exercise Plan
    st.markdown("### 📋 Exercise Plan")
    if st.session_state.current_plan and st.session_state.current_plan.get('exercises'):
        exercises = st.session_state.current_plan['exercises']
        completed = sum(1 for ex in exercises if ex.get('completed', False))
        total = len(exercises)
        
        # Progress bar
        progress_percent = (completed / total * 100) if total > 0 else 0
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress_percent}%">
                {completed}/{total}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Exercise list
        for i, ex in enumerate(exercises, 1):
            completed_class = "exercise-completed" if ex.get('completed', False) else ""
            status = "✅" if ex.get('completed', False) else "⭕"
            st.markdown(f"""
            <div class="exercise-card {completed_class}">
                {status} <strong>{i}. {ex['name']}</strong><br>
                <small>Difficulty: {ex['difficulty']}/4 | {ex['reps']} reps</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">💡 Complete your profile to get your personalized plan</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Session info
    st.markdown("### ⏱️ Session Info")
    duration = (datetime.now() - st.session_state.session_start).seconds // 60
    st.write(f"⏰ Duration: {duration} min")
    st.write(f"💬 Messages: {len(st.session_state.messages)}")
    
    if st.button("🔄 Reset Session", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != 'rag' and key != 'rag_initialized':
                del st.session_state[key]
        st.rerun()

# Main content area
if not api_key:
    st.markdown("""
    <div class="welcome-box">
        <h2>👋 Welcome to Your Knee Arthritis Exercise Guide!</h2>
        <p style="font-size: 1.1rem; margin: 1rem 0;">
            I'm your personal AI exercise coach, here to help you manage knee arthritis through safe, effective exercises.
        </p>
        <p style="font-size: 1rem;">
            <strong>To get started:</strong><br>
            👈 Enter your OpenAI API key in the sidebar
        </p>
    </div>
    
    <div class="info-box">
        <h3 style="margin-top:0;">🎯 What I Can Do For You:</h3>
        <ul>
            <li>Create personalized exercise plans based on your condition</li>
            <li>Guide you through exercises step-by-step</li>
            <li>Track your progress and adapt recommendations</li>
            <li>Answer your questions about knee arthritis management</li>
            <li>Provide safety guidance and modifications</li>
        </ul>
    </div>
    
    <div class="warning-box">
        <strong>⚠️ Important Medical Disclaimer:</strong><br>
        This tool provides educational information only. Always consult your healthcare provider before starting any exercise program.
    </div>
    """, unsafe_allow_html=True)
    
elif st.session_state.rag_initialized:
    
    # Welcome message for new users
    if len(st.session_state.messages) == 0:
        welcome_message = """
👋 **Hello! Welcome to your Knee Arthritis Exercise Coach!**

I'm here to help you manage your knee arthritis with personalized exercises. Let's start by getting to know you better.

**Could you please tell me:**
1. Your name
2. Your age
3. A brief description of your knee condition (pain level, symptoms, limitations)

For example: *"Hi, I'm Sarah, 65 years old. I have moderate knee pain, especially when climbing stairs, and my knee sometimes swells up after walking."*
        """
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome_message
        })
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message-user">
                <strong>🗣️ You:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message-assistant">
                <strong>🤖 Coach:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Show thinking spinner
        with st.spinner("🤔 Thinking..."):
            try:
                # Extract patient info if first real message
                if not st.session_state.patient_profile:
                    st.session_state.patient_profile = st.session_state.rag.extract_patient_info(user_input)
                    
                    # Try to extract name from message
                    if not st.session_state.user_name:
                        # Simple name extraction (you can make this more sophisticated)
                        words = user_input.split()
                        if "I'm" in user_input or "I am" in user_input or "my name is" in user_input.lower():
                            for i, word in enumerate(words):
                                if word.lower() in ["i'm", "i am", "name", "is"] and i + 1 < len(words):
                                    potential_name = words[i + 1].strip(',.')
                                    if potential_name[0].isupper():
                                        st.session_state.user_name = potential_name
                                        break
                    
                    # Retrieve context and create plan
                    context = st.session_state.rag.retrieve_context(
                        user_input, 
                        st.session_state.patient_profile
                    )
                    st.session_state.current_plan = st.session_state.rag.create_exercise_plan(
                        st.session_state.patient_profile,
                        context
                    )
                    
                    # Generate personalized welcome response
                    name_greeting = f"{st.session_state.user_name}" if st.session_state.user_name else "there"
                    response = st.session_state.rag.generate_response(
                        user_input,
                        st.session_state.patient_profile,
                        context,
                        st.session_state.messages
                    )
                    
                else:
                    # Normal conversation
                    context = st.session_state.rag.retrieve_context(
                        user_input,
                        st.session_state.patient_profile
                    )
                    
                    response = st.session_state.rag.generate_response(
                        user_input,
                        st.session_state.patient_profile,
                        context,
                        st.session_state.messages
                    )
                
                # Add assistant response
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Error: {e}")
        
        # Rerun to update chat
        st.rerun()

else:
    st.info("⏳ Initializing... This may take a moment.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>⚠️ Medical Disclaimer:</strong> This tool provides educational information only. Always consult your healthcare provider before starting any exercise program.</p>
    <p>🔒 Your data is not stored. Each session is private and temporary.</p>
    <p style="font-size: 0.9rem; margin-top: 1rem;">Made with ❤️ for better knee health</p>
</div>
""", unsafe_allow_html=True)
