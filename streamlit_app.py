# streamlit_app.py
"""Modern ChatGPT-style interface for Knee Arthritis Exercise Guide - Fixed Interactive Version"""

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

# Modern ChatGPT-style CSS (keeping the same beautiful styles)
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
    
    /* Chat Container */
    .chat-container {
        max-width: 900px;
        margin: 80px auto 120px auto;
        padding: 0 2rem;
    }
    
    /* Welcome Hero Section */
    .hero-section {
        text-align: center;
        padding: 4rem 2rem 2rem 2rem;
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
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #8b92a8;
        margin-bottom: 2rem;
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
    }
    
    .exercise-item:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.1);
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
    
    /* Custom Streamlit button styling */
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
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False

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
        placeholder="sk-..."
    )
    
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
                    st.error(f"Error: {e}")
    else:
        st.info("👈 Enter your OpenAI API key to begin")
    
    st.divider()
    
    # Profile Section
    if st.session_state.patient_profile:
        st.markdown("### 📊 Your Profile")
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
                <span class="profile-label">Pain:</span>
                {profile.get('pain_level', 'N/A')}/10
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Exercise Plan
    if st.session_state.current_plan and st.session_state.current_plan.get('exercises'):
        st.markdown("### 📋 Exercise Plan")
        
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
    
    st.divider()
    
    # Session Info
    st.markdown("### ⏱️ Session")
    duration = (datetime.now() - st.session_state.session_start).seconds // 60
    st.write(f"⏰ Duration: {duration} min")
    st.write(f"💬 Messages: {len(st.session_state.messages)}")
    
    if st.button("🔄 New Session", use_container_width=True):
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
    """, unsafe_allow_html=True)
    
    # Feature Cards using Streamlit columns and buttons
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
            <div style="color: white; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Personalized Plans</div>
            <div style="color: #8b92a8; font-size: 0.9rem;">Get exercise plans tailored to your condition</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
            <div style="color: white; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Progress Tracking</div>
            <div style="color: #8b92a8; font-size: 0.9rem;">Monitor your improvement over time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
            <div style="color: white; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">AI Guidance</div>
            <div style="color: #8b92a8; font-size: 0.9rem;">Step-by-step exercise instructions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚕️</div>
            <div style="color: white; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Safety First</div>
            <div style="color: #8b92a8; font-size: 0.9rem;">Evidence-based, safe recommendations</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Get Started Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Get Started", use_container_width=True, type="primary"):
            st.session_state.show_chat = True
            st.info("👈 Please enter your OpenAI API key in the sidebar to begin!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-card">
        <strong>⚠️ Medical Disclaimer:</strong> This is an educational tool. Always consult your healthcare provider before starting any exercise program.
    </div>
    """, unsafe_allow_html=True)

else:
    # Chat Interface
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
    
    # Chat input at bottom
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    user_input = st.chat_input("Type your message here...", key="chat_input")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("🤔 Thinking..."):
            try:
                if not st.session_state.patient_profile:
                    st.session_state.patient_profile = st.session_state.rag.extract_patient_info(user_input)
                    
                    # Extract name
                    words = user_input.split()
                    for i, word in enumerate(words):
                        if word.lower() in ["i'm", "i am", "name", "is"] and i + 1 < len(words):
                            potential_name = words[i + 1].strip(',.')
                            if potential_name and potential_name[0].isupper():
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
