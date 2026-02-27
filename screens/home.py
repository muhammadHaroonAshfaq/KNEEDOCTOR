"""Home Dashboard screen."""
import streamlit as st
from datetime import datetime
from design import card, badge, go, PRIMARY, MUTED, TEXT, GREEN, RED, AMBER, BORDER


def screen_home():
    profile = st.session_state.patient_profile
    name    = profile.get("name", "there")
    pain    = profile.get("pain_level", 5)
    stage   = profile.get("stage", "Sub-Acute")
    streak  = profile.get("streak", 0)
    hour    = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    # ── Header ────────────────────────────────────────────────────────────────
    col_h, col_bell = st.columns([5, 1])
    with col_h:
        st.markdown(f"<h2 style='margin:0;'>{greeting}, {name}! 👋</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{MUTED};font-size:0.88rem;margin-top:0.1rem;'>"
                    f"{datetime.now().strftime('%A, %B %d')} &nbsp;|&nbsp; "
                    f"{badge(stage,'blue' if stage=='Sub-Acute' else 'red' if stage=='Acute' else 'green')}"
                    f"</p>", unsafe_allow_html=True)
    with col_bell:
        if st.button("🔔", help="Notifications"):
            st.toast("No new notifications.", icon="🔔")

    st.markdown("<hr style='border-color:#E2E8F0;margin:0.8rem 0;'>", unsafe_allow_html=True)

    # ── Flare-up banner ────────────────────────────────────────────────────────
    if pain >= 8:
        st.markdown(f"""
        <div class='flare-banner'>
          🚨 <strong>High Pain Day Detected</strong> — Your plan has been switched to passive recovery.
          <a href='#' style='color:{RED};'>View Flare-Up Protocol →</a>
        </div>""", unsafe_allow_html=True)
        if st.button("🆘 Open Flare-Up Protocol", use_container_width=True):
            st.session_state.therapy_page = "flareup"
            go("therapy")

    # ── Morning pain check-in ─────────────────────────────────────────────────
    with st.expander("📝 Daily Pain Check-In", expanded=(not st.session_state.get("checkin_done"))):
        emojis = ["😊","🙂","😐","😕","😟","😣","😖","😭","🤯","💀","☠️"]
        new_pain = st.slider("How is your pain right now? (0–10)", 0, 10, pain, key="home_pain")
        st.markdown(f"<div style='text-align:center;font-size:2.5rem;'>{emojis[new_pain]}</div>", unsafe_allow_html=True)
        if st.button("✅ Submit & Update Plan", use_container_width=True):
            profile["pain_level"] = new_pain
            st.session_state.patient_profile = profile
            today = f"Day {len(st.session_state.pain_log)+1}"
            st.session_state.pain_log.append({"date": today, "pain": new_pain})
            if st.session_state.get("rag_initialized"):
                st.session_state.session_plan = st.session_state.rag.build_session_plan(profile)
            st.session_state.checkin_done = True
            st.success("✅ Pain logged. Your plan has been updated!")
            st.rerun()

    # ── Quick stats row ────────────────────────────────────────────────────────
    plan    = st.session_state.get("session_plan", [])
    done    = sum(1 for e in plan if e.get("completed"))
    rom_log = st.session_state.get("rom_log", [])
    avg_pain = round(sum(e["pain"] for e in st.session_state.get("pain_log",[])[-7:]) /
                     max(1, len(st.session_state.get("pain_log",[])[-7:])), 1)

    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl, icon in [
        (c1, f"{streak}", "Day Streak", "🔥"),
        (c2, f"{rom_log[-1]['rom'] if rom_log else 85}°", "ROM Today", "📐"),
        (c3, f"{avg_pain}/10", "Avg Pain (7d)", "😌"),
        (c4, f"{st.session_state.get('completed_sessions',0)}", "Sessions Done", "✅"),
    ]:
        with col:
            st.markdown(f"""
            <div class='stat-chip'>
              <div style='font-size:1.3rem;'>{icon}</div>
              <div class='stat-chip-val'>{val}</div>
              <div class='stat-chip-lbl'>{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # ── Today's therapy card ────────────────────────────────────────────────────
    col_t, col_ai = st.columns([3, 2])
    with col_t:
        pct = int(done / max(1, len(plan)) * 100)
        diff_label = "Easy" if profile.get("pain_level",5) >= 7 else "Moderate"
        st.markdown(f"""
        <div class='kd-card'>
          <div class='kd-card-title'>TODAY'S THERAPY SESSION</div>
          <div style='font-size:1.3rem;font-weight:700;color:{TEXT};'>{stage} — Session {st.session_state.get('completed_sessions',0)+1}</div>
          <div style='margin:0.5rem 0;'>
            {badge(diff_label,'green' if diff_label=='Easy' else 'amber')}
            {badge(f"{len(plan)} exercises",'blue')}
            {badge(f"{sum(int(e.get('sets',2))*int(e.get('reps',10)) for e in plan[:4])} reps",'grey')}

          </div>
          <div style='background:{BORDER};border-radius:4px;height:6px;overflow:hidden;margin-bottom:0.6rem;'>
            <div style='width:{pct}%;background:{GREEN};height:6px;border-radius:4px;'></div>
          </div>
          <div style='font-size:0.82rem;color:{MUTED};'>{done}/{len(plan)} exercises complete today</div>
        </div>""", unsafe_allow_html=True)
        c_a, c_b = st.columns(2)
        with c_a:
            if st.button("▶️  Start Session", use_container_width=True):
                go("therapy")
        with c_b:
            if st.button("👁️  Preview", use_container_width=True):
                st.session_state.therapy_page = "day"
                go("therapy")

    with col_ai:
        rag = st.session_state.get("rag")
        insight = (rag.get_daily_insight(profile) if rag
                   else f"💡 Keep moving, {name}! Even gentle daily movement significantly reduces OA pain over time.")
        st.markdown(f"""
        <div class='insight-card'>
          <div style='font-size:0.75rem;font-weight:600;color:{PRIMARY};text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem;'>💡 AI INSIGHT OF THE DAY</div>
          {insight}
        </div>""", unsafe_allow_html=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            if st.button("👍", key="ins_up"):   st.toast("Thanks for the feedback!", icon="👍")
        with fc2:
            if st.button("👎", key="ins_dn"):   st.toast("We'll improve the suggestions.", icon="👎")

    # ── Weekly calendar strip ─────────────────────────────────────────────────
    st.markdown("#### 📅 This Week")
    pain_log = st.session_state.get("pain_log", [])
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    today_idx = datetime.now().weekday()
    cols = st.columns(7)
    for i, (col, day) in enumerate(zip(cols, days)):
        with col:
            if i < today_idx:
                cls = "week-done"; icon2 = "✅"
            elif i == today_idx:
                cls = "week-sched"; icon2 = "📍"
            elif i == 6:
                cls = "week-rest"; icon2 = "😴"
            else:
                cls = "week-miss"; icon2 = "○"
            st.markdown(f"<div class='{cls} week-day'><div style='font-size:1rem;'>{icon2}</div><div>{day}</div></div>",
                        unsafe_allow_html=True)

    # ── Emergency banner ────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:#FFF5F5;border:1px solid #FEB2B2;border-radius:12px;padding:0.8rem 1.2rem;
                display:flex;align-items:center;justify-content:space-between;'>
      <span style='color:{RED};font-weight:600;'>🚨 Having a bad pain day?</span>
    </div>""", unsafe_allow_html=True)
    if st.button("Open Flare-Up Protocol →", key="home_flare"):
        st.session_state.therapy_page = "flareup"
        go("therapy")
