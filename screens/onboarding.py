"""7-step onboarding flow."""
import streamlit as st
from design import go, PRIMARY, MUTED, TEXT, BORDER, GREEN, RED

TOTAL_STEPS = 7


def _progress_bar(step: int):
    pct = int((step / TOTAL_STEPS) * 100)
    st.markdown(f"""
    <div style='margin-bottom:0.5rem;display:flex;justify-content:space-between;'>
      <span style='font-size:0.82rem;color:{MUTED};font-weight:600;'>Step {step} of {TOTAL_STEPS}</span>
      <span style='font-size:0.82rem;color:{PRIMARY};font-weight:600;'>{pct}%</span>
    </div>
    <div class='ob-progress-wrap'><div class='ob-progress-fill' style='width:{pct}%;'></div></div>
    """, unsafe_allow_html=True)


def _chips(label: str, key: str, options: list, multi: bool = False):
    """Render selectable chip buttons. Returns selected value(s)."""
    st.markdown(f"<div style='font-weight:600;margin-bottom:0.4rem;'>{label}</div>", unsafe_allow_html=True)
    state_key = f"chip_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = [] if multi else None

    cols = st.columns(min(len(options), 4))
    for i, opt in enumerate(options):
        with cols[i % len(cols)]:
            selected = (st.session_state[state_key] == opt) if not multi else (opt in st.session_state[state_key])
            style = f"border:2px solid {PRIMARY};background:#EBF8FF;color:{PRIMARY};font-weight:600;" if selected else f"border:2px solid {BORDER};background:#fff;"
            if st.button(opt, key=f"chip_{key}_{i}", use_container_width=True):
                if multi:
                    cur = list(st.session_state[state_key])
                    if opt in cur:
                        cur.remove(opt)
                    else:
                        cur.append(opt)
                    st.session_state[state_key] = cur
                else:
                    st.session_state[state_key] = opt
                st.rerun()
    return st.session_state[state_key]


def screen_onboarding():
    step = st.session_state.get("ob_step", 1)

    col = st.columns([1, 3, 1])[1]
    with col:
        _progress_bar(step)

        if   step == 1: _step1()
        elif step == 2: _step2()
        elif step == 3: _step3()
        elif step == 4: _step4()
        elif step == 5: _step5()
        elif step == 6: _step6()
        elif step == 7: _step7()


def _nav(back_step, next_fn):
    c1, c2 = st.columns([1, 2])
    with c1:
        if back_step and st.button("← Back", use_container_width=True):
            st.session_state.ob_step = back_step
            st.rerun()
    with c2:
        next_fn()


def _step1():
    profile = st.session_state.patient_profile
    st.markdown("### 👤 Personal Profile")
    st.markdown(f"<p style='color:{MUTED};'>Help us understand your background.</p>", unsafe_allow_html=True)

    with st.form("ob1"):
        name = st.text_input("First Name", value=profile.get("name", ""))
        c1, c2 = st.columns(2)
        with c1: height = st.number_input("Height (cm)", 100, 220, value=int(profile.get("height", 165)))
        with c2: weight = st.number_input("Weight (kg)", 30, 200, value=int(profile.get("weight", 70)))
        gender = st.selectbox("Gender", ["Female", "Male", "Non-binary", "Prefer not to say"],
                              index=["Female","Male","Non-binary","Prefer not to say"].index(profile.get("gender","Female")))
        occupation = st.selectbox("Occupation type",
                                  ["Sedentary (desk work)", "Light activity", "Moderate activity", "Physical labour"])
        if st.form_submit_button("Next →", use_container_width=True):
            profile.update({"name": name, "height": height, "weight": weight,
                           "gender": gender, "occupation": occupation})
            st.session_state.patient_profile = profile
            st.session_state.ob_step = 2
            st.rerun()


def _step2():
    profile = st.session_state.patient_profile
    st.markdown("### 🦵 Knee Condition")
    st.markdown(f"<p style='color:{MUTED};'>Tell us about your knee condition.</p>", unsafe_allow_html=True)

    knee  = _chips("Which knee?", "knee", ["Left", "Right", "Both"])
    diag  = _chips("Diagnosed condition?", "diag",
                   ["Osteoarthritis", "Rheumatoid", "Post-Surgery", "Not Diagnosed", "Other"])
    dur   = _chips("How long have you had symptoms?", "dur",
                   ["< 3 months", "3–12 months", "1–3 years", "3+ years"])
    surg  = _chips("Had knee surgery?", "surg", ["Yes", "No"])

    def _next():
        if st.button("Next →", use_container_width=True):
            profile.update({"knee": knee, "diagnosis": diag, "duration": dur, "surgery": surg})
            st.session_state.patient_profile = profile
            st.session_state.ob_step = 3
            st.rerun()
    _nav(1, _next)


def _step3():
    profile = st.session_state.patient_profile
    st.markdown("### 😣 Pain Baseline")
    st.markdown(f"<p style='color:{MUTED};'>Rate your current knee pain.</p>", unsafe_allow_html=True)

    pain = st.slider("Overall pain level (VAS)", 0, 10, value=int(profile.get("pain_level", 5)))
    emojis = ["😊","🙂","😐","😕","😟","😣","😖","😭","🤯","💀","☠️"]
    st.markdown(f"<div style='text-align:center;font-size:2rem;'>{emojis[pain]}</div>", unsafe_allow_html=True)

    _chips("Describe your pain (select all that apply)", "pain_type",
           ["Stiffness","Swelling","Sharp Pain","Dull Ache","Burning","Clicking","Weakness"], multi=True)

    c1, c2 = st.columns(2)
    with c1: morn = st.slider("Morning pain", 0, 10, value=int(profile.get("morning_pain", pain)))
    with c2: eve  = st.slider("Evening pain",  0, 10, value=int(profile.get("evening_pain", pain)))

    def _next():
        if st.button("Next →", use_container_width=True):
            profile.update({"pain_level": pain, "morning_pain": morn, "evening_pain": eve,
                           "pain_types": st.session_state.get("chip_pain_type", [])})
            st.session_state.patient_profile = profile
            st.session_state.ob_step = 4
            st.rerun()
    _nav(2, _next)


def _step4():
    profile = st.session_state.patient_profile
    st.markdown("### 📐 Mobility Baseline")
    st.markdown(f"<p style='color:{MUTED};'>Estimate your current knee bend range of motion.</p>", unsafe_allow_html=True)

    st.info("📷 Camera-guided ROM measurement requires the mobile app. Enter your ROM manually below, or skip.")
    rom = st.number_input("Estimated ROM (degrees, full bend = ~135°)", 0, 145,
                          value=int(profile.get("baseline_rom", 85)))
    st.markdown(f"<div style='background:#F7FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:1rem;margin:0.5rem 0;font-size:0.9rem;color:{MUTED};'>"
                "💡 <b>How to measure:</b> Sit in a chair, bend your knee as far as comfortable. Ask someone to estimate the angle, or use a goniometer app.</div>",
                unsafe_allow_html=True)

    def _next():
        if st.button("Next →", use_container_width=True):
            profile["baseline_rom"] = rom
            profile["current_rom"]  = rom
            st.session_state.patient_profile = profile
            st.session_state.ob_step = 5
            st.rerun()
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("← Back", use_container_width=True):
            st.session_state.ob_step = 3; st.rerun()
    with c2:
        _next()
    if st.button("Skip for now →", use_container_width=False):
        profile["baseline_rom"] = 85; profile["current_rom"] = 85
        st.session_state.patient_profile = profile
        st.session_state.ob_step = 5; st.rerun()


def _step5():
    profile = st.session_state.patient_profile
    st.markdown("### 🏃 Lifestyle & Activity")

    activity = _chips("Current activity level", "activity",
                      ["Sedentary", "Light", "Moderate", "Active"])
    steps    = _chips("Estimated daily steps", "steps",
                      ["Under 2K", "2–5K", "5–8K", "8K+"])
    aids     = _chips("Mobility aids used", "aids",
                      ["None", "Cane", "Walker", "Knee Brace"], multi=True)
    stairs   = _chips("Stairs at home?", "stairs", ["Yes", "No"])

    def _next():
        if st.button("Next →", use_container_width=True):
            profile.update({"activity_level": activity, "daily_steps": steps,
                            "mobility_aids": aids, "has_stairs": stairs})
            st.session_state.patient_profile = profile
            st.session_state.ob_step = 6
            st.rerun()
    _nav(4, _next)


def _step6():
    profile = st.session_state.patient_profile
    st.markdown("### 🎯 Recovery Goals")
    _chips("Select your goals (choose all that apply)", "goals",
           ["Reduce daily pain", "Walk without discomfort", "Return to sport",
            "Avoid surgery", "Recover from surgery", "Improve stairs", "Sleep better"], multi=True)
    timeline = _chips("Timeline", "timeline", ["4 weeks", "8 weeks", "3 months", "6 months"])

    def _next():
        if st.button("Next →", use_container_width=True):
            profile["goals"]    = st.session_state.get("chip_goals", [])
            profile["timeline"] = timeline
            st.session_state.patient_profile = profile
            st.session_state.ob_step = 7
            st.rerun()
    _nav(5, _next)


def _step7():
    profile = st.session_state.patient_profile
    st.markdown("### 🛡️ Medical Clearance")
    st.markdown(f"<p style='color:{MUTED};'>Last step — help us keep you safe.</p>", unsafe_allow_html=True)

    conditions = st.multiselect("Do you have any of these conditions?",
                                ["Heart disease", "Diabetes", "Osteoporosis", "Hypertension",
                                 "Obesity (BMI > 35)", "Peripheral artery disease", "None"],
                                default=profile.get("medical_conditions", []))
    approved = st.toggle("My doctor approves exercise therapy", value=profile.get("doctor_approved", False))
    st.markdown(f"<p style='font-size:0.82rem;color:{MUTED};'>Optional: upload a doctor's note in Profile → My Conditions after setup.</p>", unsafe_allow_html=True)

    stage_map = {"Acute": 1, "Sub-Acute": 2, "Chronic": 3}
    pain = profile.get("pain_level", 5)
    dur  = profile.get("duration", "3–12 months")
    if pain >= 7 or dur == "< 3 months":
        auto_stage = "Acute"
    elif pain <= 3 or dur == "3+ years":
        auto_stage = "Chronic"
    else:
        auto_stage = "Sub-Acute"
    profile["stage"] = auto_stage

    if st.button("🎯  Generate My Recovery Plan", use_container_width=True):
        profile.update({"medical_conditions": conditions, "doctor_approved": approved,
                        "streak": 0, "weather_mode": False, "onboarding_done": True})
        st.session_state.patient_profile = profile
        # Build plan
        if st.session_state.get("rag_initialized"):
            plan = st.session_state.rag.build_session_plan(profile)
        else:
            plan = _fallback_plan(profile)
        st.session_state.session_plan = plan
        _seed_demo_data(profile)
        st.session_state.ob_step = 1
        go("home")

    if st.button("← Back", use_container_width=False):
        st.session_state.ob_step = 6; st.rerun()


def _fallback_plan(profile):
    pain = profile.get("pain_level", 5)
    exercises = [
        {"id":"ex1","name":"Seated Leg Raises","category":"Strength","difficulty":1,
         "reps":12,"sets":2,"duration":30,"instructions":["Sit upright in a chair.",
         "Straighten one leg, hold 3 seconds, lower slowly."],"primary_benefit":"Strengthens quadriceps without joint load",
         "form_tips":["Keep your back straight","Breathe out as you lift"],"completed":False},
        {"id":"ex2","name":"Ankle Pumps","category":"Mobility","difficulty":1,
         "reps":20,"sets":2,"duration":30,"instructions":["Sit or lie down.",
         "Flex and point your foot rhythmically."],"primary_benefit":"Improves circulation and reduces swelling",
         "form_tips":["Move slowly and deliberately"],"completed":False},
        {"id":"ex3","name":"Heel Slides","category":"Flexibility","difficulty":2,
         "reps":10,"sets":2,"duration":30,"instructions":["Lie on your back.",
         "Slowly slide heel toward buttocks, hold 3s, return."],"primary_benefit":"Increases knee flexion ROM",
         "form_tips":["Go to your pain-free limit only"],"completed":False},
        {"id":"ex4","name":"Wall Slides","category":"Strength","difficulty":2,
         "reps":10,"sets":2,"duration":40,"instructions":["Stand with back to wall.",
         "Slide down to 30–45° bend, hold 5s, return."],"primary_benefit":"Builds quad and glute strength safely",
         "form_tips":["Don't go past 45° if painful","Keep knees behind toes"],"completed":False},
        {"id":"ex5","name":"Calf Raises","category":"Balance","difficulty":2,
         "reps":15,"sets":2,"duration":30,"instructions":["Stand behind a chair for support.",
         "Rise on tiptoes slowly, lower with control."],"primary_benefit":"Improves stability and calf strength",
         "form_tips":["Use chair for balance only, not support"],"completed":False},
    ]
    if pain >= 8:
        return _ice_protocol()
    return exercises[:4 if pain >= 6 else 5]


def _ice_protocol():
    return [
        {"id":"f1","name":"🧊 Ice Therapy","category":"Passive","difficulty":1,
         "reps":1,"sets":3,"duration":900,"instructions":["Apply ice pack (cloth-wrapped) to knee.","Hold 15–20 min. Repeat 3× daily."],
         "primary_benefit":"Reduce inflammation","form_tips":["Never apply ice directly to skin."],"completed":False,"is_passive":True},
        {"id":"f2","name":"🦵 Leg Elevation","category":"Passive","difficulty":1,
         "reps":1,"sets":1,"duration":1200,"instructions":["Lie flat, elevate leg on 2–3 pillows above heart level.","Rest 20–30 min."],
         "primary_benefit":"Reduce swelling","form_tips":[],"completed":False,"is_passive":True},
    ]


def _seed_demo_data(profile):
    import random
    if not st.session_state.get("pain_log"):
        base = profile.get("pain_level", 6)
        for i in range(7, 0, -1):
            noise = max(0, min(10, base - (7-i)*0.35 + random.uniform(-0.5,0.5)))
            st.session_state.pain_log.append({"date": f"Day {8-i}", "pain": round(noise,1)})
            st.session_state.rom_log.append({"date": f"Day {8-i}", "rom": round(85+(7-i)*2.5+random.uniform(-2,2),1)})
