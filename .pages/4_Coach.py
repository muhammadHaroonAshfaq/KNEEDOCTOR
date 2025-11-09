import streamlit as st

def ai_coach_page(rag_model):
    st.title("😀 AI Coach")

    # Initialize conversation & intake states
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "intake_done" not in st.session_state:
        st.session_state.intake_done = False
    if "intake_step" not in st.session_state:
        st.session_state.intake_step = "greet"

    # Greeting message (only shown once)
    if not st.session_state.conversation:
        st.session_state.conversation.append({
            "role": "assistant",
            "content": "👋 Hi! I'm your KneeDoc AI Coach. Let's get started with a few quick questions!"
        })

    # Chat input
    user_message = st.chat_input("Type your message...")

    if user_message:
        st.session_state.conversation.append({"role": "user", "content": user_message})

        # Step 1: Use intake system until done
        if not st.session_state.intake_done:
            reply, step = rag_model.conversational_intake(user_message)
            st.session_state.conversation.append({"role": "assistant", "content": reply})
            if step in ["done", "recommend"]:
                st.session_state.intake_done = True

        # Step 2: After intake, use the RAG model for Q&A
        else:
            patient_info = st.session_state.get("patient_profile", {})
            context = rag_model.retrieve_context(user_message, patient_info)
            reply = rag_model.generate_response(
                user_message,
                patient_info,
                context,
                st.session_state.conversation
            )
            st.session_state.conversation.append({"role": "assistant", "content": reply})

    # Display chat
    for msg in st.session_state.conversation:
        if msg["role"] == "user":
            st.chat_message("user").markdown(msg["content"])
        else:
            st.chat_message("assistant").markdown(msg["content"])
