# app.py
"""Streamlit app for Knee Arthritis Exercise Guide"""

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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    .chat-message-user {
        background: #e6f3ff;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .chat-message-assistant {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
    }
    .exercise-card {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #1f77b4;
    }
    .stats-box {
        background: #fff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
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
st.markdown('<h1 class="main-header">🦵 Knee Arthritis Exercise Guide</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key input
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key. Get one at https://platform.openai.com/api-keys"
    )
    
    if api_key:
        st.success("✅ API Key configured")
        
        # Initialize RAG only once
        if not st.session_state.rag_initialized:
            with st.spinner("Loading exercise database..."):
                try:
                    loader = load_data()
                    st.session_state.rag = initialize_rag(loader, api_key)
                    st.session_state.rag_initialized = True
                    st.success(f"✅ Loaded {len(loader.exercises)} exercises")
                except Exception as e:
                    st.error(f"Error initializing: {e}")
    else:
        st.warning("⚠️ Please enter your OpenAI API key to start")
        st.info("💡 Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)")
    
    st.divider()
    
    # Patient Profile
    st.header("📊 Your Profile")
    if st.session_state.patient_profile:
        profile = st.session_state.patient_profile
        st.markdown(f"""
        <div class="stats-box">
        <strong>Age:</strong> {profile.get('age', 'N/A')}<br>
        <strong>Severity:</strong> {profile.get('severity', 'N/A')}/4<br>
        <strong>Pain Level:</strong> {profile.get('pain_level', 'N/A')}/10
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("👋 Start chatting to create your profile!")
    
    st.divider()
    
    # Exercise Plan
    st.header("📋 Exercise Plan")
    if st.session_state.current_plan and st.session_state.current_plan.get('exercises'):
        exercises = st.session_state.current_plan['exercises']
        completed = sum(1 for ex in exercises if ex.get('completed', False))
        total = len(exercises)
        
        # Progress bar
        progress = (completed / total) if total > 0 else 0
        st.progress(progress)
        st.caption(f"{completed}/{total} exercises completed")
        
        # Exercise list
        for i, ex in enumerate(exercises, 1):
            status = "✅" if ex.get('completed', False) else "⭕"
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.write(status)
                with col2:
                    st.write(f"**{i}. {ex['name']}**")
                    st.caption(f"Difficulty: {ex['difficulty']}/4")
    else:
        st.info("💡 Chat to get your personalized plan")
    
    st.divider()
    
    # Session info
    st.header("⏱️ Session")
    duration = (datetime.now() - st.session_state.session_start).seconds // 60
    st.write(f"Duration: {duration} min")
    st.write(f"Messages: {len(st.session_state.messages)}")
    
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.patient_profile = None
        st.session_state.current_plan = None
        st.session_state.exercise_progress = {}
        st.session_state.session_start = datetime.now()
        st.rerun()

# Main content area
if not api_key:
    st.info("👈 Please enter your OpenAI API key in the sidebar to begin")
    st.markdown("""
    ### Welcome to Your Knee Arthritis Exercise Guide! 🦵
    
    This AI-powered assistant helps you:
    - Get personalized exercise recommendations
    - Learn proper exercise techniques
    - Track your progress
    - Stay motivated and safe
    
    **To get started:**
    1. Enter your OpenAI API key in the sidebar
    2. Tell me about your knee condition
    3. Get your personalized exercise plan
    4. Start exercising with guided instructions
    
    ⚠️ **Important:** This tool provides educational information only. Always consult your healthcare provider before starting any exercise program.
    """)
    
elif st.session_state.rag_initialized:
    # Quick action buttons
    st.subheader("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Show Plan", use_container_width=True):
            if st.session_state.current_plan:
                plan_text = "### 📋 Your Exercise Plan\n\n"
                for i, ex in enumerate(st.session_state.current_plan['exercises'], 1):
                    status = "✅" if ex.get('completed', False) else "⭕"
                    plan_text += f"{status} **{i}. {ex['name']}**\n"
                    plan_text += f"   - {ex['reps']} reps, {ex['sets']} sets\n"
                    plan_text += f"   - Difficulty: {ex['difficulty']}/4\n\n"
                st.markdown(plan_text)
            else:
                st.warning("No plan created yet. Tell me about your condition first!")
    
    with col2:
        if st.button("🏋️ Exercise 1", use_container_width=True):
            if st.session_state.current_plan and st.session_state.current_plan['exercises']:
                ex = st.session_state.current_plan['exercises'][0]
                guidance = st.session_state.rag.get_exercise_guidance(ex['id'])
                st.markdown(guidance)
            else:
                st.warning("No plan available. Start chatting first!")
    
    with col3:
        if st.button("▶️ START", use_container_width=True):
            st.info("⏱️ Exercise started! Follow the instructions and take your time.")
    
    with col4:
        if st.button("✅ DONE", use_container_width=True):
            if st.session_state.current_plan and st.session_state.current_plan['exercises']:
                # Mark first incomplete exercise as done
                for ex in st.session_state.current_plan['exercises']:
                    if not ex.get('completed', False):
                        ex['completed'] = True
                        st.success(f"✅ Great job completing {ex['name']}!")
                        st.balloons()
                        break
            else:
                st.warning("No active exercise to complete")
    
    st.divider()
    
    # Chat interface
    st.subheader("💬 Chat with Your Exercise Coach")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message-user"><strong>🗣️ You:</strong><br>{message["content"]}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message-assistant"><strong>🤖 Coach:</strong><br>{message["content"]}</div>', 
                       unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Type your message here... (e.g., 'I'm 68 with moderate knee arthritis')")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Show thinking spinner
        with st.spinner("🤔 Thinking..."):
            try:
                # Extract patient info if first message
                if not st.session_state.patient_profile:
                    st.session_state.patient_profile = st.session_state.rag.extract_patient_info(user_input)
                    
                    # Retrieve context and create plan
                    context = st.session_state.rag.retrieve_context(
                        user_input, 
                        st.session_state.patient_profile
                    )
                    st.session_state.current_plan = st.session_state.rag.create_exercise_plan(
                        st.session_state.patient_profile,
                        context
                    )
                
                # Check for special commands
                upper_input = user_input.upper().strip()
                
                if "EXERCISE" in upper_input and st.session_state.current_plan:
                    # Extract exercise number
                    try:
                        num = int(''.join(filter(str.isdigit, upper_input)))
                        if 0 < num <= len(st.session_state.current_plan['exercises']):
                            ex = st.session_state.current_plan['exercises'][num-1]
                            response = st.session_state.rag.get_exercise_guidance(ex['id'])
                        else:
                            response = f"❌ Invalid exercise number. Please choose 1-{len(st.session_state.current_plan['exercises'])}"
                    except:
                        response = "❌ Please specify exercise number (e.g., 'EXERCISE 1')"
                
                else:
                    # Generate normal response
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
st.caption("⚠️ **Disclaimer:** This tool provides educational information only. Always consult your healthcare provider before starting any exercise program.")
st.caption("🔒 Your data is not stored. Each session is private and temporary.")
