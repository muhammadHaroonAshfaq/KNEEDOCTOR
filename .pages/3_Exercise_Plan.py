import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Exercise Plan - KneeDoc AI", page_icon="💪", layout="wide")

# --- Styling ---
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #000000 0%, #001a33 100%) !important;
    color: white !important;
}
h1, h2, h3, h4, h5, h6 { color: white !important; }
p, div, span, label { color: #cccccc !important; }
.exercise-card {
    background: rgba(0, 51, 102, 0.4);
    border: 1px solid rgba(0,153,255,0.3);
    border-radius: 14px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 0 10px rgba(0,153,255,0.3);
}
.done {
    border: 1px solid #00ff99;
    background: rgba(0,255,153,0.1);
}
.progress-bar {
    background: rgba(255,255,255,0.1);
    height: 22px;
    border-radius: 10px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    text-align: center;
    font-weight: bold;
    color: white;
    background: linear-gradient(135deg, #00aaff, #0077ff);
}
.stButton > button {
    background: linear-gradient(135deg, #0077ff, #33ccff);
    color: white; border: none; border-radius: 10px;
    padding: 0.5rem 1.5rem; font-weight: 600; font-size: 1rem;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 15px rgba(0,153,255,0.8);
}
</style>
""", unsafe_allow_html=True)

# --- Logic ---
if "rag" not in st.session_state or not st.session_state.get("rag_initialized"):
    st.warning("⚠️ Please log in again to view your personalized exercise plan.")
    st.stop()

rag = st.session_state.rag
patient = st.session_state.get("patient_profile", {"age": 65, "severity": 3, "pain_level": 5})
context = rag.retrieve_context("knee arthritis exercises", patient)
plan = rag.create_exercise_plan(patient, context)

st.title("💪 Your Personalized Exercise Plan")
st.markdown("<p style='color:#aaa;'>These exercises are tailored based on your current knee condition and safety guidelines.</p>", unsafe_allow_html=True)

exercises = plan["exercises"]
completed = sum(1 for e in exercises if e.get("completed", False))
total = len(exercises)
progress = int((completed / total) * 100) if total > 0 else 0

# --- Progress Bar ---
st.markdown("<h4>Progress</h4>", unsafe_allow_html=True)
st.markdown(f"""
<div class='progress-bar'>
  <div class='progress-fill' style='width:{progress}%'>{completed}/{total} Done</div>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- Display Exercises ---
for i, ex in enumerate(exercises, 1):
    with st.container():
        card_class = "exercise-card done" if ex.get("completed") else "exercise-card"
        st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
        st.markdown(f"### {i}. {ex['name']}")
        st.markdown(f"**Category:** {ex['category']} | **Difficulty:** {ex['difficulty']}/4")
        st.markdown(f"**Reps:** {ex['reps']} × **Sets:** {ex['sets']}")
        st.markdown("<br>".join([f"- {s}" for s in ex["instructions"][:3]]), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        cols = st.columns([1, 1, 1])
        with cols[0]:
            if st.button(f"🏋️ View Details {i}", key=f"details_{i}"):
                st.markdown(rag.get_exercise_guidance(ex["id"]), unsafe_allow_html=True)
        with cols[1]:
            if st.button(f"✅ Mark Done {i}", key=f"done_{i}"):
                ex["completed"] = True
                st.session_state.exercise_progress = plan
                st.rerun()
        with cols[2]:
            if st.button(f"🔍 Similar {i}", key=f"similar_{i}"):
                sims = rag.find_similar_exercises(ex["name"])
                if sims:
                    st.info("Similar exercises: " + ", ".join(sims))
                else:
                    st.warning("No similar exercises found.")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption(f"Plan generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | Severity level {patient['severity']}/4")
