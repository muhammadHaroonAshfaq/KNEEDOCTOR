"""Therapy module: Plan, Day Detail, Active Session, Exercise Preview, Flare-Up."""
import streamlit as st
import time
import random
from design import card, badge, go, PRIMARY, MUTED, TEXT, GREEN, RED, AMBER, BORDER, CARD_BG


def screen_therapy():
    tpage = st.session_state.get("therapy_page", "plan")
    if   tpage == "plan":    _plan()
    elif tpage == "day":     _day()
    elif tpage == "session": _session()
    elif tpage == "preview": _preview()
    elif tpage == "flareup": _flareup()


# ── Plan Overview ─────────────────────────────────────────────────────────────
def _plan():
    profile = st.session_state.patient_profile
    stage   = profile.get("stage","Sub-Acute")
    plan    = st.session_state.get("session_plan", [])

    st.markdown(f"<h2 style='margin:0;'>🦵 Therapy Plan</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};margin-bottom:0.8rem;'>{stage} Recovery Protocol</p>", unsafe_allow_html=True)

    # Week tabs (mock)
    week_tab = st.radio("Week", ["Week 1","Week 2","Week 3","Week 4"], horizontal=True, label_visibility="collapsed")

    # Filter
    ftype = st.selectbox("Filter exercises", ["All","Strength","Flexibility","Balance","Cardio"], label_visibility="collapsed")

    filtered = plan if ftype == "All" else [e for e in plan if e.get("category","") == ftype]

    st.markdown(f"**{len(filtered)} exercises in today's session**", unsafe_allow_html=True)
    for ex in filtered:
        done = ex.get("completed", False)
        cls  = "done" if done else ""
        st.markdown(f"""
        <div class='ex-card {cls}'>
          <div style='display:flex;justify-content:space-between;align-items:center;'>
            <div>
              <div class='ex-card-name'>{"✅ " if done else ""}{ex["name"]}</div>
              <div class='ex-benefit'>🎯 {ex.get("primary_benefit","")}</div>
              <div class='ex-meta'>💪 {ex.get("sets","—")}×{ex.get("reps","—")} reps
                &nbsp;|&nbsp; {badge(ex.get("category","General"),"blue")}</div>
            </div>
            <div style='font-size:1.8rem;'>{"✅" if done else "🏋️"}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ Start Full Session", use_container_width=True):
            st.session_state.active_ex_idx = 0
            # Reset completion
            for e in plan: e["completed"] = False
            st.session_state.session_plan = plan
            st.session_state.therapy_page = "session"
            st.rerun()
    with c2:
        if st.button("🔄 Request Plan Change", use_container_width=True):
            st.session_state.current_page = "coach"
            st.rerun()


# ── Day Session Detail ────────────────────────────────────────────────────────
def _day():
    profile = st.session_state.patient_profile
    plan    = st.session_state.get("session_plan", [])
    st.markdown(f"<h2 style='margin:0;'>📋 Today's Session</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};'>Preview all exercises before starting.</p>", unsafe_allow_html=True)

    total_reps = sum(int(e.get("sets",2))*int(e.get("reps",10)) for e in plan)

    st.markdown(f"""
    <div class='kd-card' style='background:{PRIMARY};'>
      <div style='color:rgba(255,255,255,0.8);font-size:0.82rem;text-transform:uppercase;letter-spacing:0.05em;'>SESSION SUMMARY</div>
      <div style='color:#fff;font-size:1.4rem;font-weight:700;margin:0.3rem 0;'>{len(plan)} Exercises · {total_reps} Total Reps</div>
      <div>{badge("No equipment needed","grey")}{badge(profile.get("stage","Sub-Acute"),"blue")}</div>
    </div>""", unsafe_allow_html=True)

    for i, ex in enumerate(plan):
        with st.expander(f"{i+1}. {ex['name']} — {ex.get('sets','—')}×{ex.get('reps','—')}", expanded=False):
            st.markdown(f"🎯 **Benefit:** {ex.get('primary_benefit','')}")
            st.markdown(f"**Instructions:**")
            for instr in ex.get("instructions",[]):
                st.markdown(f"  • {instr}")
            tips = ex.get("form_tips",[])
            if tips:
                st.markdown(f"💡 **Form Tips:** {' · '.join(tips)}")
            if st.button("👁️ Full Preview", key=f"prev_{i}"):
                st.session_state.preview_ex = ex
                st.session_state.therapy_page = "preview"
                st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back to Plan"):
            st.session_state.therapy_page = "plan"; st.rerun()
    with c2:
        if st.button("▶️ Start Session", use_container_width=True):
            st.session_state.active_ex_idx = 0
            for e in plan: e["completed"] = False
            st.session_state.therapy_page = "session"; st.rerun()


# ── Active Session ─────────────────────────────────────────────────────────────
def _session():
    profile = st.session_state.patient_profile
    plan    = st.session_state.get("session_plan", [])
    idx     = st.session_state.get("active_ex_idx", 0)

    if idx >= len(plan):
        _session_complete(profile, plan); return

    ex      = plan[idx]
    total   = len(plan)

    # Top bar
    c_title, c_exit = st.columns([4,1])
    with c_title:
        st.markdown(f"<h3 style='margin:0;'>Exercise {idx+1} of {total}</h3>", unsafe_allow_html=True)
    with c_exit:
        if st.button("✕  Exit"):
            st.session_state.therapy_page = "plan"; st.rerun()

    # Progress
    pct = int(idx/total*100)
    st.markdown(f"<div style='background:{BORDER};border-radius:4px;height:6px;margin-bottom:1rem;overflow:hidden;'>"
                f"<div style='width:{pct}%;background:{PRIMARY};height:6px;'></div></div>", unsafe_allow_html=True)

    # Pose detection placeholder (camera unavailable in web Streamlit)
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;
                padding:2.5rem;text-align:center;color:white;margin-bottom:1rem;'>
      <div style='font-size:3rem;'>{random.choice(["🦵","💪","🏃","⚖️"])}</div>
      <div style='font-size:1.1rem;font-weight:600;margin-top:0.5rem;'>{ex["name"]}</div>
      <div style='font-size:0.85rem;opacity:0.7;margin-top:0.3rem;'>
        AI Pose Detection available in the mobile app
      </div>
      <div style='margin-top:1rem;padding:0.5rem 1rem;background:rgba(56,161,105,0.3);
                  border-radius:8px;border:1px solid rgba(56,161,105,0.6);display:inline-block;'>
        ✅ Good posture — keep going!
      </div>
    </div>""", unsafe_allow_html=True)

    # Rep counter
    st.markdown(f"""
    <div style='text-align:center;margin:1rem 0;'>
      <div class='big-counter'>{ex.get('reps',10)}</div>
      <div class='big-counter-lbl'>reps &nbsp;×&nbsp; {ex.get('sets',2)} sets</div>
      <div style='margin-top:0.4rem;'>{badge(ex.get("category","Strength"),"blue")}{badge(f"Difficulty {ex.get('difficulty',2)}/4","grey")}</div>
    </div>""", unsafe_allow_html=True)

    # Instructions
    with st.expander("📋 Instructions", expanded=True):
        for i, instr in enumerate(ex.get("instructions",[]), 1):
            st.markdown(f"**{i}.** {instr}")
        for tip in ex.get("form_tips",[]):
            st.markdown(f"💡 _{tip}_")

    # Action buttons
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("😓 Too Hard", use_container_width=True):
            plan[idx]["reps"] = max(4, ex.get("reps",10) - 3)
            plan[idx]["sets"] = max(1, ex.get("sets",2) - 1)
            st.session_state.session_plan = plan
            st.toast("Intensity reduced. You're doing great — listen to your body!", icon="💙")
            st.rerun()
    with col_b:
        if st.button("😤 Too Easy", use_container_width=True):
            plan[idx]["reps"] = ex.get("reps",10) + 3
            st.session_state.session_plan = plan
            st.toast("Great! Reps increased.", icon="💪")
            st.rerun()
    with col_c:
        st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
        if st.button("🚨 Pain!", use_container_width=True):
            st.session_state.therapy_page = "flareup"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
    if st.button("✅  Mark Complete & Continue →", use_container_width=True):
        plan[idx]["completed"] = True
        st.session_state.session_plan = plan
        st.session_state.active_ex_idx = idx + 1
        import math
        new_rom = min(140, st.session_state.patient_profile.get("current_rom",85) + 1.5)
        profile["current_rom"] = new_rom
        st.session_state.rom_log.append({"date":f"Day {len(st.session_state.rom_log)+1}","rom":round(new_rom,1)})
        st.rerun()


def _session_complete(profile, plan):
    completed = sum(1 for e in plan if e.get("completed"))
    st.balloons()
    st.markdown(f"""
    <div style='text-align:center;padding:2rem;'>
      <div style='font-size:4rem;'>🎉</div>
      <h2>Session Complete!</h2>
      <p style='color:{MUTED};'>Amazing work — consistency is building long-term joint health.</p>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    for col,val,lbl in [(c1,f"{completed}/{len(plan)}","Exercises Done"),
                        (c2,f"{profile.get('current_rom',85):.0f}°","ROM Reached"),
                        (c3,f"+{completed}","Streak Points")]:
        with col:
            st.markdown(f"<div class='stat-chip'><div class='stat-chip-val'>{val}</div><div class='stat-chip-lbl'>{lbl}</div></div>",unsafe_allow_html=True)

    st.markdown("<div style='margin:1rem 0;'></div>",unsafe_allow_html=True)
    post_pain = st.slider("How do you feel now? (0–10)", 0, 10, value=max(0, profile.get("pain_level",5)-1))
    notes = st.text_area("Log session notes (optional)", placeholder="Any observations about today's session…")

    if st.button("💾 Save & Return Home", use_container_width=True):
        profile["pain_level"] = post_pain
        profile["streak"] = profile.get("streak",0) + 1
        st.session_state.completed_sessions = st.session_state.get("completed_sessions",0)+1
        st.session_state.pain_log.append({"date":f"Day {len(st.session_state.pain_log)+1}","pain":post_pain})
        st.session_state.therapy_page = "plan"
        go("home")


# ── Exercise Preview ──────────────────────────────────────────────────────────
def _preview():
    ex = st.session_state.get("preview_ex", {})
    if not ex:
        st.session_state.therapy_page = "day"; st.rerun()

    if st.button("← Back"):
        st.session_state.therapy_page = "day"; st.rerun()

    st.markdown(f"<h2 style='margin:0;'>{ex.get('name','Exercise')}</h2>", unsafe_allow_html=True)
    diff_badge = badge(f"Difficulty {ex.get('difficulty', 2)}/4", 'grey')
    st.markdown(f"{badge(ex.get('category','General'),'blue')}{diff_badge}", unsafe_allow_html=True)


    st.markdown(f"""
    <div style='background:#1a1a2e;border-radius:16px;padding:3rem;text-align:center;color:white;margin:1rem 0;'>
      <div style='font-size:4rem;'>🦵</div>
      <div style='opacity:0.7;font-size:0.9rem;margin-top:0.5rem;'>Exercise demonstration</div>
    </div>""",unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown(f"**🎯 Primary Benefit**")
        st.markdown(ex.get("primary_benefit",""))
        st.markdown(f"**📋 Instructions**")
        for i,instr in enumerate(ex.get("instructions",[]),1):
            st.markdown(f"{i}. {instr}")
    with c2:
        st.markdown(f"**💡 Form Tips**")
        for tip in ex.get("form_tips",[]):
            st.markdown(f"✓ {tip}")
        st.markdown(f"**⚠️ Contraindicated if**")
        ci = ex.get("contraindications",[])
        st.markdown(", ".join(ci) if ci else "No specific contraindications listed")
        st.markdown(f"""**📌 Sets & Reps**
        - {ex.get("sets",2)} sets × {ex.get("reps",10)} reps
        - Duration: ~{ex.get("duration",30)}s per set""")


# ── Flare-Up Protocol Screen ──────────────────────────────────────────────────
def _flareup():
    if st.button("← Back to Plan"):
        st.session_state.therapy_page = "plan"; st.rerun()

    st.markdown(f"""
    <div style='text-align:center;background:#FFF5F5;border:1px solid #FEB2B2;
                border-radius:20px;padding:2rem;margin-bottom:1.5rem;'>
      <div style='font-size:3rem;'>🧊</div>
      <h2 style='color:{RED};margin:0.5rem 0;'>Rest Mode Activated</h2>
      <p style='color:{MUTED};'>High pain detected. Follow the steps below to manage your flare-up safely.</p>
    </div>""", unsafe_allow_html=True)

    steps = [
        ("🛑","Rest","Stop all weight-bearing activity. Sit or lie down comfortably."),
        ("🧊","Ice","Apply an ice pack (wrapped in cloth) to your knee for 15–20 minutes. Repeat every 2–3 hours."),
        ("🩹","Compress","Apply a light compression bandage to reduce swelling. Don't wrap too tight."),
        ("⬆️","Elevate","Elevate your leg above heart level using pillows. Rest for at least 20 minutes."),
    ]
    for icon,title,desc in steps:
        st.markdown(f"""
        <div class='kd-card' style='border-left:4px solid {RED};'>
          <div style='display:flex;align-items:flex-start;gap:1rem;'>
            <div style='font-size:1.8rem;'>{icon}</div>
            <div><strong>{title}</strong><br><span style='color:{MUTED};font-size:0.9rem;'>{desc}</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("**Gentle Passive Movements (if pain < 7/10):**")
    for mov in ["Ankle pumps — flex/point foot 20×","Gentle knee pendulum — dangle leg and let gravity gently swing it","Quad sets — gently tighten thigh muscle while lying flat, hold 5s"]:
        st.markdown(f"  • {mov}")

    st.markdown("<div style='margin:1rem 0'></div>",unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        if st.button("📞 Call My Doctor", use_container_width=True):
            st.info("Open your phone and call your doctor's stored number.")
    with c2:
        if st.button("📅 Resume Plan Tomorrow", use_container_width=True):
            st.success("Your plan will resume tomorrow. Rest well!")
            st.session_state.therapy_page = "plan"
            st.rerun()

    st.markdown("<div style='margin:0.5rem 0'></div>",unsafe_allow_html=True)
    if st.button("🔴 Log This Flare-Up", use_container_width=True):
        import datetime
        st.session_state.flare_log = st.session_state.get("flare_log",[])
        st.session_state.flare_log.append({"date":datetime.datetime.now().strftime("%Y-%m-%d"),"pain":st.session_state.patient_profile.get("pain_level",8)})
        st.success("Flare-up logged to your medical history.")
