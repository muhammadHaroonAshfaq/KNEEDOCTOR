import streamlit as st
from datetime import datetime
import time

st.set_page_config(page_title="AI Coach - KneeDoc AI", page_icon="🤖", layout="wide")

# --- Theme ---
st.markdown("""
<style>
.stApp {background: linear-gradient(180deg, #000000 0%, #001a33 100%) !important; color: white;}
.chat-bubble-user {
    background: linear-gradient(135deg, #0077ff, #33ccff);
    color: white; padding: 0.8rem 1rem; border-radius: 15px;
    width: fit-content; max-width: 80%; margin-left: auto; margin-right: 0.5rem;
    margin-bottom: 0.6rem; font-size: 1rem;
}
.chat-bubble-bot {
    background: rgba(0, 51, 102, 0.5);
    color: white; padding: 0.8rem 1rem; border-radius: 15px;
    width: fit-content; max-width: 80%; margin-right: auto; margin-left: 0.5rem;
    margin-bottom: 0.6rem; font-size: 1rem;
    border: 1px solid rgba(0,153,255,0.3);
}
.typing {
    background: rgba(0, 153, 255, 0.1);
    border-radius: 10px;
    padding: 0.4rem 0.7rem;
    display: inline-block;
    margin: 0.5rem;
    font-style: italic;
    color: #aaa;
}
input, textarea {color: black !important;}
</style>
""", unsafe_allow_html=True)

# --- Initialize Session ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "intake_step" not in st.session_state:
    st.session_state.intake_step = "ask_age"

rag = st.session_state.get("rag")

st.title("🦵 AI Physiotherapy Coach")

# Display conversation
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-bubble-user'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-bot'>{msg['content']}</div>", unsafe_allow_html=True)

# --- User input box ---
user_input = st.chat_input("Type your message here...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Typing animation
    with st.empty():
        for dots in [".", "..", "..."]:
            st.markdown(f"<div class='typing'>KneeDoc AI is typing{dots}</div>", unsafe_allow_html=True)
            time.sleep(0.3)

    # Step-by-step intake logic
    if st.session_state.intake_step != "done":
        response, next_step = rag.conversational_intake(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.intake_step = next_step

        if next_step == "done":
            st.session_state.patient_profile = st.session_state.get("patient_profile", {})
            plan = rag.create_exercise_plan(st.session_state.patient_profile, {})
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✅ Your plan is ready! You can view it on the Exercise Plan page."
            })
    else:
        # Once intake is done, normal AI chat
        patient = st.session_state.get("patient_profile", {})
        context = rag.retrieve_context(user_input, patient)
        reply = rag.generate_response(user_input, patient, context, st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    st.rerun()
