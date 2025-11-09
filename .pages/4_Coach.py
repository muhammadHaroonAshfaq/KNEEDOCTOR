import streamlit as st
import time

st.set_page_config(page_title="AI Coach - KneeDoc AI", page_icon="🤖", layout="wide")

# --- Global styling ---
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #000000 0%, #001a33 100%) !important;
    color: white !important;
}

/* Chat container */
.chat-area {
    max-width: 900px;
    margin: 3rem auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

/* Chat bubbles */
.chat-bubble {
    padding: 1rem 1.3rem;
    border-radius: 14px;
    max-width: 75%;
    word-wrap: break-word;
    line-height: 1.5;
    animation: fadeIn 0.4s ease;
}
.user-bubble {
    background: linear-gradient(135deg, #0077ff, #33ccff);
    align-self: flex-end;
    color: white;
    border-bottom-right-radius: 4px;
}
.ai-bubble {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(0,153,255,0.3);
    align-self: flex-start;
    color: #e0e0e0;
    border-bottom-left-radius: 4px;
}
.typing {
    font-style: italic;
    color: #33ccff;
    padding: 0.6rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0077ff, #33ccff);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.7rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 12px rgba(0,153,255,0.7);
}

/* Animations */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}

/* Confidence badge */
.confidence-badge {
    font-size: 0.8rem;
    color: #8ab4f8;
    margin-top: -0.6rem;
    margin-bottom: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# --- Initialization ---
if "rag" not in st.session_state or not st.session_state.get("rag_initialized"):
    st.warning("⚠️ Please log in again from the main page to access the AI Coach.")
    st.stop()

rag = st.session_state.rag

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 KneeDoc AI Coach")
st.markdown("<p style='color:#aaa;'>Ask me anything about knee arthritis exercises, pain relief, or mobility improvement.</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- Chat display ---
chat_container = st.container()
with chat_container:
    st.markdown("<div class='chat-area'>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        conf = msg.get("confidence", None)
        if role == "assistant":
            st.markdown(f"<div class='chat-bubble ai-bubble'>{content}</div>", unsafe_allow_html=True)
            if conf is not None:
                st.markdown(f"<div class='confidence-badge'>Confidence: {conf*100:.0f}%</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble user-bubble'>{content}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Input area ---
user_input = st.chat_input("Type your question or describe your symptoms...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("KneeDoc is thinking..."):
        typing_placeholder = st.empty()
        typing_placeholder.markdown("<div class='typing'>KneeDoc is typing...</div>", unsafe_allow_html=True)
        time.sleep(1.1)
        typing_placeholder.empty()

        # --- Guardrails and AI response ---
        patient = st.session_state.get("patient_profile", {"age": 65, "severity": 3, "pain_level": 5, "goals": ["reduce pain"]})
        context = rag.retrieve_context(user_input, patient)
        response = rag.generate_response(user_input, patient, context, st.session_state.messages)
        confidence = rag.get_confidence(context["exercises"])

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "confidence": confidence
        })

    st.rerun()

# --- Footer tools ---
st.markdown("<hr>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("📄 Summarize My Session", use_container_width=True):
        with st.spinner("Generating summary..."):
            summary = rag.summarize_session(st.session_state.messages)
            st.markdown(f"<div class='chat-bubble ai-bubble'>{summary}</div>", unsafe_allow_html=True)

with col2:
    if st.button("🔍 Show Similar Exercises", use_container_width=True):
        last_ex = None
        for m in reversed(st.session_state.messages):
            if "exercise" in m["content"].lower():
                last_ex = m["content"].split()[0]
                break
        if last_ex:
            sims = rag.find_similar_exercises(last_ex)
            if sims:
                sim_text = "Here are a few similar exercises you might try:\n" + ", ".join(sims)
                st.session_state.messages.append({"role": "assistant", "content": sim_text})
                st.rerun()
            else:
                st.warning("No similar exercises found.")
        else:
            st.info("Ask about a specific exercise first!")

with col3:
    if st.button("🧠 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.success("Chat cleared.")
        st.rerun()
