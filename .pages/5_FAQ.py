import streamlit as st

st.title("❓ Frequently Asked Questions")

faq = {
    "Is KneeDoc AI a medical app?": "No, it's an educational tool. Always consult a healthcare provider before starting any exercise.",
    "Do I need equipment?": "Most exercises are bodyweight-based, but a mat or chair can help.",
    "Can I track my progress?": "Yes! Your personalized plan updates as you interact with the AI Coach.",
    "Is my data safe?": "Yes, your data stays local and isn't shared externally."
}

for q, a in faq.items():
    with st.expander(q):
        st.write(a)
