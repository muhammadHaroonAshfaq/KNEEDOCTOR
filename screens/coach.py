"""AI Coach chat screen."""
import streamlit as st
import time
from design import go, PRIMARY, MUTED, TEXT, GREEN, RED, BORDER, LIGHT_BG


QUICK_QUESTIONS = [
    "Why does my knee hurt after sessions?",
    "Is it safe to walk today?",
    "Modify today's plan",
    "What does this exercise do?",
    "I feel worse today",
]


def screen_coach():
    st.markdown(f"<h2 style='margin:0;'>🤖 AI Physiotherapy Coach</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};font-size:0.9rem;margin-bottom:0.8rem;'>Powered by clinical RAG knowledge base. Ask anything about your knee recovery.</p>", unsafe_allow_html=True)

    profile = st.session_state.patient_profile
    rag     = st.session_state.get("rag")

    # Contraindication alerts
    if rag:
        warnings = rag.check_contraindications(profile)
        if warnings:
            with st.expander("⚠️ Active Contraindication Warnings", expanded=False):
                for w in warnings:
                    st.warning(w)

    # Tab: Chat vs Saved
    ctab, stab = st.tabs(["💬 Chat with Aria", "🔖 Saved Answers"])

    with ctab:
        # Quick question chips
        st.markdown("<div style='margin-bottom:0.5rem;font-size:0.82rem;font-weight:600;color:#718096;'>QUICK QUESTIONS</div>", unsafe_allow_html=True)
        q_cols = st.columns(len(QUICK_QUESTIONS))
        for col, q in zip(q_cols, QUICK_QUESTIONS):
            with col:
                if st.button(q[:22]+"…" if len(q)>22 else q, key=f"qq_{q[:8]}", use_container_width=True):
                    if "chat_messages" not in st.session_state:
                        st.session_state.chat_messages = []
                    st.session_state.chat_messages.append({"role":"user","content":q})
                    st.rerun()

        st.markdown("<hr style='border-color:#E2E8F0;margin:0.5rem 0;'>", unsafe_allow_html=True)

        # Init chat
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": f"👋 Hi {profile.get('name','there')}! I'm **Aria**, your AI recovery coach. I'm here to answer any questions about your knee health, exercises, or recovery plan. What's on your mind?",
                "citations": []
            })

        # Display messages
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style='display:flex;justify-content:flex-end;margin-bottom:0.5rem;'>
                  <div class='chat-bubble user-bubble'>{msg['content']}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='display:flex;align-items:flex-start;gap:0.6rem;margin-bottom:0.5rem;'>
                  <div style='font-size:1.3rem;'>🤖</div>
                  <div>
                    <div class='chat-bubble ai-bubble'>{msg['content']}</div>
                    {''.join(f"<span class='citation-badge'>{c}</span>" for c in msg.get('citations',[]))}
                  </div>
                </div>""", unsafe_allow_html=True)

                # Feedback buttons
                col_f1, col_f2, col_save = st.columns([1,1,4])
                with col_f1:
                    if st.button("👍", key=f"up_{id(msg)}"):
                        st.toast("Thanks!", icon="👍")
                with col_f2:
                    if st.button("👎", key=f"dn_{id(msg)}"):
                        st.toast("We'll improve this.", icon="👎")
                with col_save:
                    if st.button("🔖 Save", key=f"save_{id(msg)}"):
                        saved = st.session_state.get("saved_answers", [])
                        saved.append(msg)
                        st.session_state.saved_answers = saved
                        st.toast("Answer saved!", icon="🔖")

        # Handle pending user message
        msgs = st.session_state.chat_messages
        if msgs and msgs[-1]["role"] == "user":
            user_msg = msgs[-1]["content"]
            with st.spinner("Aria is thinking…"):
                time.sleep(0.5)
                if rag:
                    context = rag.retrieve_context(user_msg, profile)
                    ai_text, citations = rag.generate_response(user_msg, profile, context, msgs[-6:])
                else:
                    ai_text = _fallback_response(user_msg, profile)
                    citations = []
            msgs.append({"role":"assistant","content":ai_text,"citations":citations})
            st.rerun()

        # Input
        user_input = st.chat_input("Ask your AI coach anything about knee recovery…")
        if user_input:
            st.session_state.chat_messages.append({"role":"user","content":user_input})
            st.rerun()

        st.markdown(f"<p style='font-size:0.72rem;color:{MUTED};text-align:center;margin-top:0.5rem;'>Educational information only. Always consult a qualified physiotherapist for medical advice.</p>",
                    unsafe_allow_html=True)

    with stab:
        saved = st.session_state.get("saved_answers", [])
        if not saved:
            st.info("No saved answers yet. Tap 🔖 on any AI response to save it here.")
        else:
            search = st.text_input("🔍 Search saved", placeholder="Search…")
            for i, msg in enumerate(saved):
                if search.lower() in msg["content"].lower() or not search:
                    with st.expander(msg["content"][:60]+"…", expanded=False):
                        st.markdown(msg["content"])
                        for c in msg.get("citations",[]):
                            st.markdown(f"<span class='citation-badge'>{c}</span>", unsafe_allow_html=True)
                        if st.button("🗑️ Delete", key=f"del_saved_{i}"):
                            saved.pop(i)
                            st.session_state.saved_answers = saved
                            st.rerun()


def _fallback_response(query: str, profile: dict) -> str:
    name  = profile.get("name","there")
    pain  = profile.get("pain_level",5)
    stage = profile.get("stage","Sub-Acute")
    q     = query.lower()

    if any(w in q for w in ["hurt","pain","sore"]):
        return (f"Post-exercise soreness of 1–2/10 is normal, {name} — it's a sign your muscles are adapting. "
                f"However, sharp or worsening pain above your baseline of {pain}/10 is a warning sign. "
                "Apply ice for 15 min and rest if that happens. If it persists, consult your physiotherapist.")
    if any(w in q for w in ["walk","safe"]):
        return (f"For your {stage} stage with a pain level of {pain}/10, gentle walking on flat surfaces is generally safe. "
                "Aim for 10–15 minutes twice daily. Avoid hills and uneven terrain. Stop if pain exceeds your baseline.")
    if any(w in q for w in ["plan","modify","change"]):
        return ("I can adjust your plan! Would you like fewer exercises, lower intensity, or a focus on a specific type "
                "(strength / flexibility / balance)? Let me know and I'll rebuild your session plan.")
    if any(w in q for w in ["exercise","what does","benefit"]):
        return ("Every exercise in your plan is chosen to build quad strength, improve joint mobility, or reduce stiffness. "
                "Stronger muscles around the knee reduce joint load — 1kg of quad strength ≈ 4kg less force on your knee cartilage.")
    if any(w in q for w in ["worse","bad","flare"]):
        return (f"I'm sorry you're feeling worse, {name}. On a difficult day, switch to passive recovery: "
                "ice for 15 min, elevate your leg, and rest. Don't push through sharp pain. "
                "You can activate Flare-Up Mode from the Therapy tab.")
    return (f"Great question, {name}! Based on clinical guidelines for {stage} knee arthritis recovery, "
            "the key principles are: consistent low-impact movement, progressive loading, and listening to your body. "
            "Your current plan is designed around these principles. Is there something specific you'd like to know more about?")
