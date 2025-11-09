# streamlit_app.py
"""Modern ChatGPT-style interface for Knee Arthritis Exercise Guide"""

import streamlit as st
from datetime import datetime
import os
from data_loader import KneeArthritisDataLoader
from rag_model import KneeArthritisRAG

# Page configuration
st.set_page_config(
    page_title="KneeDoc AI",
    page_icon="🦵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern ChatGPT-style CSS
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global styles */
    .stApp {
        background-color: #0d1117;
    }
    
    .main {
        background-color: #0d1117;
        padding: 0;
    }
    
    /* Top Navigation Bar */
    .top-nav {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background: linear-gradient(135deg, #1a1f35 0%, #0d1117 100%);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        display: flex;
        align-items: center;
        padding: 0 2rem;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .logo {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .nav-items {
        margin-left: auto;
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    .nav-button {
        background: rgba(255,255,255,0.1);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.2);
        cursor: pointer;
        transition: all 0.3s;
        font-size: 0.9rem;
    }
    
    .nav-button:hover {
        background: rgba(255,255,255,0.2);
        border-color: #667eea;
    }
    
    /* Chat Container */
    .chat-container {
        max-width: 900px;
        margin: 80px auto 100px auto;
        padding: 0 2rem;
    }
    
    /* Welcome Hero Section */
    .hero-section {
        text-align: center;
        padding: 4rem 2rem;
        margin: 2rem 0;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        animation: fadeInUp 0.8s ease;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #8b92a8;
        margin-bottom: 3rem;
        animation: fadeInUp 1s ease;
    }
    
    .feature-cards {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-top: 3rem;
    }
    
    .feature-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        border-color: #667eea;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-size: 0.9rem;
        color: #8b92a8;
    }
    
    /* Chat Messages */
    .message-wrapper {
        display: flex;
        margin: 2rem 0;
        animation: fadeInUp 0.5s ease;
    }
    
    .message-user {
        justify-content: flex-end;
    }
    
    .message-assistant {
        justify-content: flex-start;
    }
    
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
        margin: 0 1rem;
    }
    
    .avatar-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .avatar-assistant {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    }
    
    .message-content {
        max-width: 70%;
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .message-user .message-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom-right-radius: 4px;
    }
    
    .message-assistant .message-content {
        background: rgba(255,255,255,0.05);
        color: #e6e8eb;
        border: 1px solid rgba(255,255,255,0.1);
        border-bottom-left-radius: 4px;
    }
    
    /* Input Container */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to top, #0d1117 0%, rgba(13, 17, 23, 0.95) 100%);
        padding: 1.5rem 2rem 2rem 2rem;
        border-top: 1px solid rgba(255,255,255,0.1);
        z-index: 999;
    }
    
    .input-wrapper {
        max-width: 900px;
        margin: 0 auto;
        position: relative;
    }
    
    /* Sidebar styling */
    .sidebar-content {
        background: #161b22;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .sidebar-title {
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .profile-item {
        background: rgba(255,255,255,0.05);
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: #8b92a8;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .profile-label {
        color: #667eea;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .progress-bar-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        height: 30px;
        margin: 1rem 0;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .progress-bar-fill {
        background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 0.9rem;
        transition: width 0.5s ease;
    }
    
    .exercise-item {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .exercise-item:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.1);
        transform: translateX(5px);
    }
    
    .exercise-completed {
        border-color: #4CAF50;
        background: rgba(76, 175, 80, 0.1);
    }
    
    .exercise-title {
        color: white;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    
    .exercise-meta {
        color: #8b92a8;
        font-size: 0.85rem;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .typing-indicator {
        display: inline-flex;
        gap: 4px;
        padding: 1rem;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #667eea;
        animation: pulse 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    /* Custom Streamlit input styling */
    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        color: white;
        padding: 1rem 1.5rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Info boxes */
    .info-card {
        background: rgba(33, 150, 243, 0.1);
        border: 1px solid rgba(33, 150, 243, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #e6e8eb;
    }
    
    .success-card {
        background: rgba(76, 175, 80, 0.1);
        border: 1px solid rgba(76, 175, 80, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #e6e8eb;
    }
    
    .warning-card {
        background: rgba(255, 152, 0, 0.1);
        border: 1px solid rgba(255, 152, 0, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #e6e8eb;
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
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'show_welcome' not in st.session_state:
    st.session_state.show_welcome = True

# Load data and initialize RAG (cached)
@st.cache_resource
def load_data():
    loader = KneeArthritisDataLoader(data_dir="data")
    loader.load_all()
    return loader

@st.cache_resource
def initialize_rag(_loader, api_key):
    return KneeArthritisRAG(_loader, api_key)

# Top Navigation Bar
st.markdown("""
<div class="top-nav">
    <div class="logo">🦵 KneeDoc AI</div>
    <div class="nav-items">
        <div class="nav-button">💬 Chat</div>
        <div class="nav-button">📋 My Plan</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙️ Settings</div>', unsafe_allow_html=True)
    
    # API Key
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key",
        label_visibility="collapsed",
        placeholder="Enter OpenAI API Key..."
    )
    
    if api_key:
        st.markdown('<div class="success-card">✅ API Key configured</div>', unsafe_allow_html=True)
        
        if not st.session_state.rag_initialized:
            with st.spinner("Loading..."):
                try:
                    loader = load_data()
                    st.session_state.rag = initialize_rag(loader, api_key)
                    st.session_state.rag_initialized = True
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.markdown('<div class="info-card">ℹ️ Enter API key to start</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Profile Section
    if st.session_state.patient_profile:
        st.markdown('<div class="sidebar-title">📊 Your Profile</div>', unsafe_allow_html=True)
        profile = st.session_state.patient_profile
        
        st.markdown(f"""
        <div class="sidebar-content">
            <div class="profile-item">
                <span class="profile-label">Name:</span>
                {st.session_state.user_name or 'Not set'}
            </div>
            <div class="profile-item">
                <span class="profile-label">Age:</span>
                {profile.get('age', 'N/A')} years
            </div>
            <div class="profile-item">
                <span class="profile-label">Severity:</span>
                {profile.get('severity', 'N/A')}/4
            </div>
            <div class="profile-item">
                <span class="profile-label">Pain Level:</span>
                {profile.get('pain_level', 'N/A')}/10
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Exercise Plan
    if st.session_state.current_plan and st.session_state.current_plan.get('exercises'):
        st.markdown('<div class="sidebar-title">📋 Exercise Plan</div>', unsafe_allow_html=True)
        
        exercises = st.session_state.current_plan['exercises']
        completed = sum(1 for ex in exercises if ex.get('completed', False))
        total = len(exercises)
        progress = (completed / total * 100) if total > 0 else 0
        
        st.markdown(f"""
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {progress}%">
                {completed}/{total} Done
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        for i, ex in enumerate(exercises, 1):
            completed_class = "exercise-completed" if ex.get('completed', False) else ""
            status = "✅" if ex.get('completed', False) else "⭕"
            
            st.markdown(f"""
            <div class="exercise-item {completed_class}">
                <div class="exercise-title">{status} {i}. {ex['name']}</div>
                <div class="exercise-meta">Difficulty: {ex['difficulty']}/4 • {ex['reps']} reps</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Session Info
    st.markdown('<div class="sidebar-title">⏱️ Session</div>', unsafe_allow_html=True)
    duration = (datetime.now() - st.session_state.session_start).seconds // 60
    st.markdown(f"""
    <div class="sidebar-content">
        <div class="profile-item">⏰ Duration: {duration} min</div>
        <div class="profile-item">💬 Messages: {len(st.session_state.messages)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 New Session"):
        for key in list(st.session_state.keys()):
            if key not in ['rag', 'rag_initialized']:
                del st.session_state[key]
        st.rerun()

# Main Chat Area
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if not api_key or not st.session_state.rag_initialized:
    # Hero Welcome Section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Welcome to KneeDoc AI</h1>
        <p class="hero-subtitle">Your Personal AI Exercise Coach for Knee Arthritis Management</p>
    </div>
    
    <div class="feature-cards">
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Personalized Plans</div>
            <div class="feature-desc">Get exercise plans tailored to your condition</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Progress Tracking</div>
            <div class="feature-desc">Monitor your improvement over time</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI Guidance</div>
            <div class="feature-desc">Step-by-step exercise instructions</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚕️</div>
            <div class="feature-title">Safety First</div>
            <div class="feature-desc">Evidence-based, safe recommendations</div>
        </div>
    </div>
    
    <div class="warning-card" style="margin-top: 3rem;">
        <strong>⚠️ Medical Disclaimer:</strong> This is an educational tool. Always consult your healthcare provider before starting any exercise program.
    </div>
    """, unsafe_allow_html=True)

else:
    # Initial welcome message
    if len(st.session_state.messages) == 0:
        welcome = """👋 **Hello! I'm your KneeDoc AI Coach.**

I'm here to create a personalized exercise program for your knee arthritis. Let's start by getting to know you!

**Please tell me:**
- Your name
- Your age  
- A brief description of your knee condition

*Example: "Hi, I'm Sarah, 65 years old. I have moderate knee pain when climbing stairs and occasional swelling."*"""
        
        st.session_state.messages.append({"role": "assistant", "content": welcome})
    
    # Display messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="message-wrapper message-user">
                <div class="message-content">{message["content"]}</div>
                <div class="avatar avatar-user">👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-wrapper message-assistant">
                <div class="avatar avatar-assistant">🤖</div>
                <div class="message-content">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Fixed Input at Bottom
if api_key and st.session_state.rag_initialized:
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
    
    user_input = st.chat_input("Type your message...", key="chat_input")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner(""):
            try:
                if not st.session_state.patient_profile:
                    st.session_state.patient_profile = st.session_state.rag.extract_patient_info(user_input)
                    
                    # Extract name
                    words = user_input.split()
                    for i, word in enumerate(words):
                        if word.lower() in ["i'm", "i am", "name", "is"] and i + 1 < len(words):
                            potential_name = words[i + 1].strip(',.')
                            if potential_name[0].isupper():
                                st.session_state.user_name = potential_name
                                break
                    
                    context = st.session_state.rag.retrieve_context(user_input, st.session_state.patient_profile)
                    st.session_state.current_plan = st.session_state.rag.create_exercise_plan(
                        st.session_state.patient_profile, context
                    )
                    response = st.session_state.rag.generate_response(
                        user_input, st.session_state.patient_profile, context, st.session_state.messages
                    )
                else:
                    context = st.session_state.rag.retrieve_context(user_input, st.session_state.patient_profile)
                    response = st.session_state.rag.generate_response(
                        user_input, st.session_state.patient_profile, context, st.session_state.messages
                    )
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Error: {e}")
        
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
