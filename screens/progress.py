"""Progress analytics: Dashboard, Session History, Doctor Report."""
import streamlit as st
from datetime import datetime
import plotly.graph_objects as pgo
import plotly.express as px
from design import card, badge, go, PRIMARY, MUTED, TEXT, GREEN, RED, AMBER, BORDER



def screen_progress():
    ppage = st.session_state.get("progress_page", "dashboard")
    tabs  = st.tabs(["📊 Analytics", "📋 Session History", "🩺 Doctor Report"])
    with tabs[0]: _dashboard()
    with tabs[1]: _history()
    with tabs[2]: _report()


def _dashboard():
    profile  = st.session_state.patient_profile
    pain_log = st.session_state.get("pain_log", [])
    rom_log  = st.session_state.get("rom_log",  [])

    st.markdown(f"<h3 style='margin:0 0 1rem;'>📈 Your Progress</h3>", unsafe_allow_html=True)

    # Time filter
    tf = st.radio("Period", ["7 Days","1 Month","3 Months","All Time"], horizontal=True, label_visibility="collapsed")
    n  = {"7 Days":7,"1 Month":30,"3 Months":90,"All Time":9999}[tf]
    pl = pain_log[-n:]
    rl = rom_log[-n:]

    # Pain trend
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='kd-card-title'>PAIN TREND (VAS)</div>", unsafe_allow_html=True)
        if pl:
            fig = pgo.Figure()
            fig.add_trace(pgo.Scatter(
                x=[e["date"] for e in pl], y=[e["pain"] for e in pl],
                mode="lines+markers",
                line=dict(color=RED, width=2.5, shape="spline"),
                marker=dict(color=RED, size=7),
                fill="tozeroy", fillcolor="rgba(229,62,62,0.07)"
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(color=TEXT, family="Inter"),
                              yaxis=dict(range=[0,10], gridcolor="#E2E8F0", zeroline=False),
                              xaxis=dict(gridcolor="#E2E8F0"),
                              margin=dict(l=0,r=0,t=10,b=0), height=200, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"<div class='kd-card-title'>RANGE OF MOTION (°)</div>", unsafe_allow_html=True)
        if rl:
            fig2 = pgo.Figure()
            fig2.add_trace(pgo.Bar(
                x=[e["date"] for e in rl], y=[e["rom"] for e in rl],
                marker_color=[f"rgba(56,161,105,{0.4+0.06*i})" for i in range(len(rl))]
            ))
            fig2.add_hline(y=120, line_dash="dash", line_color="#2B6CB0",
                           annotation_text="Target 120°", annotation_font_color=PRIMARY)
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(color=TEXT, family="Inter"),
                              yaxis=dict(range=[60,145], gridcolor="#E2E8F0", zeroline=False),
                              xaxis=dict(gridcolor="#E2E8F0"),
                              margin=dict(l=0,r=0,t=10,b=0), height=200, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    # Summary stats
    c1,c2,c3 = st.columns(3)
    if pl:
        imp = round(pl[0]["pain"]-pl[-1]["pain"],1)
        with c1:
            colour = GREEN if imp >= 0 else RED
            st.markdown(f"<div class='stat-chip'><div class='stat-chip-val' style='color:{colour};'>{'+' if imp>=0 else ''}{imp}</div><div class='stat-chip-lbl'>Pain Improvement</div></div>",unsafe_allow_html=True)
    if rl:
        gain = round(rl[-1]["rom"]-rl[0]["rom"],1)
        with c2:
            st.markdown(f"<div class='stat-chip'><div class='stat-chip-val' style='color:{GREEN};'>+{gain}°</div><div class='stat-chip-lbl'>ROM Gained</div></div>",unsafe_allow_html=True)
    with c3:
        sess = st.session_state.get("completed_sessions",0)
        st.markdown(f"<div class='stat-chip'><div class='stat-chip-val'>{sess}</div><div class='stat-chip-lbl'>Sessions Done</div></div>",unsafe_allow_html=True)

    # Milestones
    st.markdown("#### 🏅 Milestones")
    sess  = st.session_state.get("completed_sessions",0)
    streak= profile.get("streak",0)
    pain  = profile.get("pain_level",10)
    milestones = [
        ("🥇","First Session", sess>=1), ("🔥","3-Day Streak", streak>=3),
        ("💪","5 Sessions",    sess>=5),  ("⭐","1-Week Streak", streak>=7),
        ("🏆","10 Sessions",   sess>=10), ("📐","ROM > 100°", (rl[-1]["rom"]>=100 if rl else False)),
        ("🌟","Pain Halved",   pain<=5),  ("🎯","Near Recovery", sess>=20 and pain<=2),
    ]
    html = "<div style='display:flex;flex-wrap:wrap;gap:0.5rem;'>"
    for icon,label,earned in milestones:
        html += f"<div class='milestone{'' if earned else ' milestone-locked'}'><div style='font-size:1.6rem;'>{icon}</div><div style='font-size:0.78rem;color:{MUTED};margin-top:0.2rem;'>{label}</div></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _history():
    st.markdown(f"<h3 style='margin:0 0 1rem;'>📋 Session History</h3>", unsafe_allow_html=True)
    sessions = st.session_state.get("completed_sessions",0)
    pain_log = st.session_state.get("pain_log",[])

    if sessions == 0:
        st.info("No completed sessions yet. Start your first therapy session!")
        return

    search = st.text_input("🔍 Search sessions", placeholder="Search by date or type…")
    for i in range(min(sessions, len(pain_log))):
        entry = pain_log[i] if i < len(pain_log) else {}
        label = f"Session {i+1}  —  {entry.get('date','—')}  |  Pain: {entry.get('pain','?')}/10"
        if search.lower() in label.lower() or not search:
            with st.expander(label):
                st.markdown(f"**Pain after session:** {entry.get('pain','?')}/10")
                st.markdown(f"**Stage:** {st.session_state.patient_profile.get('stage','—')}")
                st.markdown(f"**Exercises completed:** {len(st.session_state.get('session_plan',[]))}")

    if st.button("📤 Export History as CSV"):
        import io, csv
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Session","Date","Pain After"])
        for i,e in enumerate(pain_log,1):
            writer.writerow([i, e.get("date",""), e.get("pain","")])
        st.download_button("⬇️ Download CSV", buf.getvalue(), "session_history.csv", "text/csv")


def _report():
    profile  = st.session_state.patient_profile
    pain_log = st.session_state.get("pain_log",[])
    rom_log  = st.session_state.get("rom_log",[])
    sessions = st.session_state.get("completed_sessions",0)

    st.markdown(f"<h3 style='margin:0 0 0.5rem;'>🩺 Doctor Progress Report</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};margin-bottom:1rem;'>Generate a clinical summary to share with your physician or physiotherapist.</p>", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class='kd-card'>
        <div class='kd-card-title'>REPORT INCLUDES</div>
        <ul style='font-size:0.9rem;line-height:2;margin:0.3rem 0 0;padding-left:1.1rem;'>
          <li>Patient profile &amp; recovery stage</li>
          <li>Pain VAS trend (current &amp; average)</li>
          <li>Sessions completed &amp; streak</li>
          <li>Range of motion progress</li>
          <li>Goals &amp; timeline</li>
          <li>Flare-up log</li>
          <li>Clinical disclaimer note</li>
        </ul></div>""", unsafe_allow_html=True)

    with c2:
        if st.button("📄 Generate Clinical Report", use_container_width=True):
            avg_pain = round(sum(e["pain"] for e in pain_log)/max(1,len(pain_log)),1)
            start_rom = rom_log[0]["rom"] if rom_log else profile.get("baseline_rom",85)
            end_rom   = rom_log[-1]["rom"] if rom_log else profile.get("current_rom",85)
            flares    = len(st.session_state.get("flare_log",[]))

            report = f"""KNEE REHABILITATION PROGRESS REPORT
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PATIENT INFORMATION
  Name              : {profile.get('name','N/A')}
  Age Estimate      : {profile.get('age','N/A')}
  Recovery Stage    : {profile.get('stage','N/A')}
  Diagnosed Condition: {profile.get('diagnosis','N/A')}
  Affected Knee     : {profile.get('knee','N/A')}
  Prior Surgery     : {profile.get('surgery','N/A')}

PAIN SUMMARY
  Current Pain (VAS): {profile.get('pain_level','N/A')}/10
  Average Pain (trend): {avg_pain}/10
  Flare-Up Episodes : {flares}

MOBILITY
  Baseline ROM      : {start_rom:.0f}°
  Current ROM       : {end_rom:.0f}°
  ROM Improvement   : +{end_rom-start_rom:.1f}°

THERAPY ADHERENCE
  Sessions Completed: {sessions}
  Consecutive Streak: {profile.get('streak',0)} days

PATIENT GOALS
{chr(10).join('  • '+g for g in profile.get('goals',['Not specified']))}
  Timeline: {profile.get('timeline','N/A')}

MEDICAL CONDITIONS FLAGGED
{chr(10).join('  ⚠️ '+c for c in profile.get('medical_conditions',['None'])) or '  None'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  AI-assisted educational tool only.
Not a substitute for clinical diagnosis or treatment.
Powered by KneeDoc AI | For clinical review purposes only."""
            st.session_state.clinical_report = report
            st.success("Report generated!")

        if st.session_state.get("clinical_report"):
            st.markdown(f"<div class='report-box'>{st.session_state.clinical_report}</div>", unsafe_allow_html=True)
            st.download_button("⬇️ Download Report (.txt)",
                               st.session_state.clinical_report,
                               f"KneeDoc_Report_{profile.get('name','Patient')}_{datetime.now().strftime('%Y%m%d')}.txt",
                               "text/plain", use_container_width=True)
            if st.button("📧 Share with Doctor (copy link)"):
                st.info("Feature coming soon — share via the mobile app.")
