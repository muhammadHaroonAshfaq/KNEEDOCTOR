"""Profile & Settings screens."""
import streamlit as st
from design import go, badge, PRIMARY, MUTED, TEXT, GREEN, RED, AMBER, BORDER, CARD_BG


def screen_profile():
    profile = st.session_state.patient_profile
    ptabs   = st.tabs(["👤 Profile", "⚙️ Settings", "📋 My Plan", "🔗 Integrations", "🆘 Support"])

    with ptabs[0]: _profile_overview(profile)
    with ptabs[1]: _settings(profile)
    with ptabs[2]: _plan_settings(profile)
    with ptabs[3]: _integrations()
    with ptabs[4]: _support()


def _profile_overview(profile):
    st.markdown(f"<h3 style='margin:0 0 1rem;'>👤 My Profile</h3>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown("<div style='font-size:4rem;text-align:center;'>👤</div>", unsafe_allow_html=True)
        if st.button("📸 Change Photo"):
            st.toast("Camera upload available in the mobile app.", icon="📸")
    with c2:
        st.markdown(f"<h2 style='margin:0;'>{profile.get('name','—')}</h2>", unsafe_allow_html=True)
        pain_colour = 'red' if profile.get('pain_level', 0) >= 7 else 'green'
        pain_badge  = badge(f"Pain: {profile.get('pain_level','—')}/10", pain_colour)
        st.markdown(f"{badge(profile.get('stage','—'),'blue')}{pain_badge}",
                    unsafe_allow_html=True)

        st.markdown(f"<p style='color:{MUTED};font-size:0.88rem;margin-top:0.4rem;'>"
                    f"Knee: {profile.get('knee','—')} | Condition: {profile.get('diagnosis','—')} | "
                    f"Streak: {profile.get('streak',0)} days</p>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#E2E8F0;'>", unsafe_allow_html=True)

    # Edit personal info
    with st.expander("✏️ Edit Personal Information"):
        with st.form("edit_profile"):
            name   = st.text_input("First Name", value=profile.get("name",""))
            c1, c2 = st.columns(2)
            with c1: h = st.number_input("Height (cm)", 100, 220, value=int(profile.get("height",165)))
            with c2: w = st.number_input("Weight (kg)", 30, 200, value=int(profile.get("weight",70)))
            if st.form_submit_button("Save Changes"):
                profile.update({"name":name,"height":h,"weight":w})
                st.session_state.patient_profile = profile
                st.success("Profile updated!")

    # My Conditions card
    with st.expander("🦵 My Conditions"):
        st.markdown(f"**Knee:** {profile.get('knee','—')}")
        st.markdown(f"**Diagnosis:** {profile.get('diagnosis','—')}")
        st.markdown(f"**Duration:** {profile.get('duration','—')}")
        st.markdown(f"**Surgery:** {profile.get('surgery','—')}")
        st.markdown(f"**Medical Conditions:** {', '.join(profile.get('medical_conditions',[]))  or 'None'}")
        if st.button("♻️ Re-do Assessment"):
            st.session_state.ob_step = 2
            st.session_state.current_page = "onboarding"
            st.rerun()

    # My Goals card
    with st.expander("🎯 My Goals"):
        for g in profile.get("goals", ["Not set"]):
            st.markdown(f"  ✓ {g}")
        st.markdown(f"**Timeline:** {profile.get('timeline','—')}")
        if st.button("✏️ Edit Goals"):
            st.session_state.ob_step = 6
            st.session_state.current_page = "onboarding"
            st.rerun()

    # Doctor contacts
    with st.expander("🩺 My Doctors"):
        st.text_input("Doctor's Name", placeholder="Dr. Sarah Ahmed")
        st.text_input("Phone", placeholder="+1 555 000 0000")
        if st.button("💾 Save Doctor Contact"):
            st.success("Doctor contact saved!")


def _settings(profile):
    st.markdown(f"<h3 style='margin:0 0 1rem;'>⚙️ App Settings</h3>", unsafe_allow_html=True)

    with st.expander("🔔 Notifications", expanded=True):
        st.toggle("Daily session reminder", value=True)
        st.time_input("Reminder time", value=None, label_visibility="collapsed")
        st.toggle("Pain check-in reminder", value=True)
        st.toggle("Streak alerts", value=True)
        st.toggle("Weekly progress report", value=True)
        st.toggle("Flare-up follow-up tips", value=True)
        st.toggle("Milestone achievements", value=True)

    with st.expander("♿ Accessibility"):
        st.slider("Text size", 14, 24, value=16, help="Adjust the base text size")
        st.toggle("High contrast mode", value=False)
        st.toggle("Voice navigation", value=False, help="Available on mobile app")
        st.toggle("Reduce motion (animations)", value=False)

    with st.expander("🎵 Session Settings"):
        st.toggle("Audio cues during session", value=True)
        st.toggle("Haptic feedback", value=True, help="Mobile app only")
        st.toggle("Background music", value=False)
        st.slider("Music volume", 0, 100, value=40)
        st.selectbox("Rest timer sound", ["Soft bell","Chime","Silent","Beep"])
        st.selectbox("Camera view", ["Front camera","Back camera"])

    with st.expander("🌍 Units & Language"):
        st.radio("Units", ["Metric (kg / cm)","Imperial (lbs / ft)"], horizontal=True)
        st.selectbox("Language", ["English","Urdu","Arabic","Spanish","French"])

    # Weather / flare mode
    st.markdown("<hr style='border-color:#E2E8F0;'>", unsafe_allow_html=True)
    weather = st.toggle("🌧️ Flare / Weather Mode",
                        value=profile.get("weather_mode", False),
                        help="Activates gentler protocol on bad weather or inflammation days")
    profile["weather_mode"] = weather
    st.session_state.patient_profile = profile


def _plan_settings(profile):
    st.markdown(f"<h3 style='margin:0 0 1rem;'>📋 My Recovery Plan</h3>", unsafe_allow_html=True)

    stage_map = {"Acute":"🔴 Acute","Sub-Acute":"🟡 Sub-Acute","Chronic":"🟢 Chronic"}
    st.markdown(f"**Current Stage:** {badge(profile.get('stage','Sub-Acute'),'blue')}", unsafe_allow_html=True)

    freq = st.select_slider("Sessions per week", ["3×","4×","5×","Daily"],
                             value=profile.get("freq","5×"))
    dur  = st.select_slider("Session duration", ["10 min","20 min","30 min","45 min"],
                             value=profile.get("session_dur","20 min"))

    if st.button("💾 Save Preferences"):
        profile.update({"freq":freq,"session_dur":dur})
        st.session_state.patient_profile = profile
        st.success("Plan preferences saved!")

    st.markdown("<div style='margin:1rem 0;'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Reset My Plan", use_container_width=True):
            if st.session_state.get("rag_initialized"):
                plan = st.session_state.rag.build_session_plan(profile)
            else:
                from screens.onboarding import _fallback_plan
                plan = _fallback_plan(profile)
            st.session_state.session_plan = plan
            st.success("Plan regenerated with latest profile!")
    with c2:
        if st.button("⏸️ Pause Plan", use_container_width=True):
            st.info("Select your vacation dates below:")
            st.date_input("Pause from / to", [])


def _integrations():
    st.markdown(f"<h3 style='margin:0 0 1rem;'>🔗 Health Integrations</h3>", unsafe_allow_html=True)

    integ = [
        ("🍎","Apple Health","Sync steps, active minutes, heart rate"),
        ("🤖","Google Fit","Sync activity and wellness data"),
        ("⌚","Apple Watch","Sync workout sessions and HR"),
        ("📱","Fitbit","Sync sleep and daily activity"),
        ("🏃","Garmin","Sync running and activity data"),
    ]
    for icon, name, desc in integ:
        col1, col2, col3 = st.columns([1,4,2])
        with col1: st.markdown(f"<div style='font-size:1.8rem;'>{icon}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{name}**")
            st.markdown(f"<span style='font-size:0.82rem;color:{MUTED};'>{desc}</span>", unsafe_allow_html=True)
        with col3:
            st.toggle("Connect", value=False, key=f"integ_{name}")
        st.markdown("<hr style='border-color:#E2E8F0;margin:0.3rem 0;'>", unsafe_allow_html=True)

    st.markdown(f"<p style='font-size:0.82rem;color:{MUTED};margin-top:0.5rem;'>🔒 We only read relevant health metrics. Your data is never sold or shared.</p>",
                unsafe_allow_html=True)

    # Privacy section
    with st.expander("🔒 Data Privacy"):
        st.markdown("Your data is processed locally. Your OpenAI key is never stored on external servers.")
        st.toggle("Share anonymised data to improve AI models", value=False)
        if st.button("⬇️ Download My Data"):
            st.info("Data export will be emailed to you within 24 hours.")
        st.markdown(f"<a href='#' style='color:{RED};'>🗑️ Delete My Account</a>", unsafe_allow_html=True)


def _support():
    st.markdown(f"<h3 style='margin:0 0 1rem;'>🆘 Support & Feedback</h3>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("💬 Chat with Support", use_container_width=True):
            st.info("Support chat — available Monday–Friday 9am–5pm.")
    with c2:
        if st.button("⭐ Rate the App", use_container_width=True):
            st.toast("Thank you! Redirecting to app store…", icon="⭐")

    with st.expander("📝 Submit Feedback"):
        fb_type = st.selectbox("Category", ["General Feedback","Bug Report","Feature Request","Medical Concern"])
        fb_text = st.text_area("Your feedback", placeholder="Tell us what you think…")
        if st.button("Submit Feedback"):
            if fb_text:
                st.success("Thank you! Your feedback has been submitted.")
            else:
                st.error("Please enter your feedback.")

    st.markdown("#### ❓ FAQ")
    faqs = [
        ("Is this a medical app?","No — KneeDoc AI is an AI-assisted educational tool. Always consult your physician before starting any exercise programme."),
        ("Does it need equipment?","Most exercises are chair-based or bodyweight. No gym equipment required."),
        ("Is my data stored?","Your data stays on your device. Your OpenAI key is used only to power AI responses and is never retained."),
        ("Can I use it post-surgery?","Yes, but always get clearance from your surgeon first. Select 'Post-Surgery' in your assessment."),
        ("What's the difference between stages?","Acute = recent injury/flare. Sub-Acute = improving but still symptomatic. Chronic = long-term management."),
    ]
    for q, a in faqs:
        with st.expander(q):
            st.write(a)

    st.markdown(f"""
    <div style='background:#FFF5F5;border:1px solid #FEB2B2;border-radius:12px;padding:1rem;margin-top:1rem;'>
      <strong style='color:{RED};'>🚨 Report a Medical Concern</strong><br>
      <span style='font-size:0.88rem;color:{MUTED};'>If you are experiencing a medical emergency, call 911 immediately. For non-emergency medical questions, contact your doctor directly.</span>
    </div>""", unsafe_allow_html=True)
