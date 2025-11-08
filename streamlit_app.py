import streamlit as st
import json
from datetime import datetime
import os
import chromadb

# --- RAG/LangChain Imports (Required for Deployment) ---
# NOTE: These packages must be in your requirements.txt
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.prompts import PromptTemplate
# -----------------------------------------------------

# Page config
st.set_page_config(
    page_title="Knee Arthritis Exercise Guide",
    page_icon="🦵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (kept as is)
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .exercise-card {
        background: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .chat-message-user {
        background: #e6f3ff;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .chat-message-assistant {
        background: #f0f0f0;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .progress-bar {
        background: #4CAF50;
        height: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        line-height: 30px;
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

# --- CORE RAG MODEL FUNCTION ---
@st.cache_resource
def load_rag_components():
    # 1. Load API keys from Streamlit secrets
    try:
        openai_api_key = st.secrets["OPENAI_API_KEY"]
        # Assuming ANTHROPIC_API_KEY might be used for other components later
        # anthropic_api_key = st.secrets["ANTHROPIC_API_KEY"] 
    except KeyError as e:
        st.error(f"Missing API key in .streamlit/secrets.toml: {e}. Please check your secrets.")
        # Halt execution if keys are missing
        st.stop()

    # 2. Initialize Embeddings Model (Must match what was used for indexing)
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # 3. Initialize Vector Store (ChromaDB)
    # The 'persist_directory' must match the folder you upload to GitHub
    try:
        vectorstore = Chroma(
            persist_directory="db_chroma",
            embedding_function=embeddings
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    except Exception as e:
        st.error(f"Could not load vector store from 'db_chroma'. Did you upload the folder to GitHub? Error: {e}")
        st.stop()


    # 4. Initialize LLM (OpenAI)
    llm = ChatOpenAI(
        api_key=openai_api_key,
        model_name="gpt-3.5-turbo", 
        temperature=0.0
    )

    # 5. Define Custom RAG Prompt for the Exercise Coach Persona
    coach_template = """
    You are an AI Knee Arthritis Exercise Coach. Your goal is to be encouraging, informative, and safe.
    Use the following retrieved context ONLY to inform your answers about knee arthritis exercises.
    If the context does not contain the answer, state that you cannot provide specific medical advice based on the available information and recommend seeing a physical therapist or doctor.

    Retrieved Context:
    {context}

    Patient's Question/Input: {question}

    Your Coaching Response:
    """
    
    coach_prompt = PromptTemplate(
        template=coach_template, 
        input_variables=["context", "question"]
    )

    # 6. Create the RetrievalQA Chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False, # Set to True if you want to display sources
        chain_type_kwargs={"prompt": coach_prompt}
    )

    return qa_chain

# Load the RAG chain
try:
    interactive_rag_chain = load_rag_components()
except Exception as e:
    # Error handling for the case where st.stop() wasn't enough or a runtime error occurred
    st.error(f"An error occurred during RAG component loading: {e}")
    st.info("Please ensure your `db_chroma` folder is in the root directory and your API keys are set.")


# Header
st.markdown('<h1 class="main-header">🦵 Knee Arthritis Exercise Guide</h1>', unsafe_allow_html=True)

# Sidebar (kept as is)
with st.sidebar:
    st.header("📊 Your Profile")
    
    if st.session_state.patient_profile:
        st.write(f"**Age:** {st.session_state.patient_profile.get('age', 'N/A')}")
        st.write(f"**Severity:** {st.session_state.patient_profile.get('severity', 'N/A')}/4")
        st.write(f"**Pain Level:** {st.session_state.patient_profile.get('pain_level', 'N/A')}/10")
    else:
        st.info("👋 Start chatting to create your profile!")
    
    st.markdown("---")
    
    st.header("📋 Exercise Plan")
    if st.session_state.current_plan:
        exercises = st.session_state.current_plan.get('exercises', [])
        completed = sum(1 for ex in exercises if ex.get('completed', False))
        total = len(exercises)
        
        progress = (completed / total * 100) if total > 0 else 0
        st.markdown(f'<div class="progress-bar" style="width: {progress}%">{completed}/{total} Done</div>', 
                   unsafe_allow_html=True)
        
        st.markdown("---")
        for i, ex in enumerate(exercises, 1):
            status = "✅" if ex.get('completed', False) else "⭕"
            st.write(f"{status} {i}. {ex['name']}")
    
    st.markdown("---")
    
    if st.button("🔄 Reset Session"):
        st.session_state.messages = []
        st.session_state.patient_profile = None
        st.session_state.current_plan = None
        st.session_state.exercise_progress = {}
        st.rerun()

# Main chat area
st.header("💬 Chat with Your Exercise Coach")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-message-user">🗣️ You: {message["content"]}</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message-assistant">🤖 Coach: {message["content"]}</div>', 
                   unsafe_allow_html=True)

# Quick action buttons (Placeholder - you might want to wire these up)
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📋 Show Plan"):
        # This will trigger the chat input logic below
        user_input_from_button = "Show me my current exercise plan."
    else:
        user_input_from_button = None
with col2:
    if st.button("🏋️ Exercise 1"):
        user_input_from_button = "Tell me more about Exercise 1 in my plan."
    else:
        user_input_from_button = None
with col3:
    if st.button("▶️ START"):
        user_input_from_button = "I'm ready to start my workout."
    else:
        user_input_from_button = None
with col4:
    if st.button("✅ DONE"):
        user_input_from_button = "I finished all my exercises today. How should I update my progress?"
    else:
        user_input_from_button = None

# Chat input
user_input = st.chat_input("Type your message here...")

# Handle combined input (chatbox or button)
final_user_input = user_input or user_input_from_button

if final_user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": final_user_input})
    
    # Generate response (using the RAG chain)
    with st.spinner("🤖 Coach is thinking..."):
        try:
            # Call the RAG chain
            result = interactive_rag_chain.invoke(final_user_input)
            response = result['result']
        except Exception as e:
            response = f"Sorry, the RAG model failed to generate a response. Please check your API key and model setup. Error: {e}"

    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to update chat
    st.rerun()

# Footer
st.markdown("---")
st.caption("⚠️ This tool provides educational information only. Always consult your healthcare provider before starting any exercise program.")