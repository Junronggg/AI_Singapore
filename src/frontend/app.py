import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="Water Infrastructure Monitoring Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Styling
# ---------------------------
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(180deg, #f6fbff 0%, #eef5fb 100%);
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
        max-width: 1400px;
    }

    .app-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.15rem;
    }

    .app-subtitle {
        font-size: 1rem;
        color: #475569;
        margin-bottom: 1rem;
    }

    .status-banner {
        border-radius: 18px;
        padding: 1rem 1.2rem;
        color: white;
        font-weight: 700;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12);
        margin-bottom: 1rem;
    }

    .status-critical {
        background: linear-gradient(135deg, #dc2626, #ef4444);
    }

    .status-warning {
        background: linear-gradient(135deg, #d97706, #f59e0b);
    }

    .status-normal {
        background: linear-gradient(135deg, #059669, #10b981);
    }

    .card {
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 22px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
        backdrop-filter: blur(8px);
    }

    .card-title {
        font-size: 0.92rem;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }

    .card-value {
        font-size: 1.8rem;
        color: #0f172a;
        font-weight: 800;
        line-height: 1.1;
    }

    .small-muted {
        font-size: 0.9rem;
        color: #64748b;
    }

    .section-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.8rem;
    }

    .pill {
        display: inline-block;
        padding: 0.28rem 0.7rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-right: 0.35rem;
        margin-bottom: 0.4rem;
    }

    .pill-red {
        background: #fee2e2;
        color: #b91c1c;
    }

    .pill-yellow {
        background: #fef3c7;
        color: #b45309;
    }

    .pill-green {
        background: #dcfce7;
        color: #15803d;
    }

    .trace-box {
        border-left: 4px solid #3b82f6;
        padding-left: 0.8rem;
        margin-bottom: 0.8rem;
    }

    .action-box {
        background: linear-gradient(135deg, #eff6ff, #f8fbff);
        border: 1px solid #bfdbfe;
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.8rem;
    }

    .network-node {
        display: inline-block;
        min-width: 90px;
        text-align: center;
        padding: 0.65rem 0.7rem;
        margin: 0.35rem 0.35rem 0.35rem 0;
        border-radius: 14px;
        font-weight: 700;
        font-size: 0.9rem;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
    }

    .node-normal {
        background: #ecfeff;
        color: #0f766e;
        border: 1px solid #99f6e4;
    }

    .node-warning {
        background: #fef3c7;
        color: #b45309;
        border: 1px solid #fcd34d;
    }

    .node-critical {
        background: #fee2e2;
        color: #b91c1c;
        border: 1px solid #fca5a5;
    }

    .footer-note {
        color: #64748b;
        font-size: 0.88rem;
        margin-top: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Mock Data
# ---------------------------
now = datetime.now()
times = [now - timedelta(minutes=29 - i) for i in range(30)]

pressure_values = []
base = 2.2
for i in range(30):
    if i < 18:
        val = base + random.uniform(-0.04, 0.05)
    elif i < 23:
        val = base - 0.1 + random.uniform(-0.05, 0.05)
    else:
        val = base - 0.42 + random.uniform(-0.04, 0.03)
    pressure_values.append(round(val, 3))

anomaly_scores = []
for i in range(30):
    if i < 18:
        score = random.uniform(0.05, 0.16)
    elif i < 23:
        score = random.uniform(0.25, 0.45)
    else:
        score = random.uniform(0.72, 0.92)
    anomaly_scores.append(round(score, 3))

incident = {
    "incident_id": "INC_001",
    "status": "ACTIVE",
    "severity": "HIGH",
    "affected_asset": "P101",
    "zone": "ZONE_A",
    "anomaly_score": 0.87,
    "failure_risk_score": 0.72,
    "maintenance_horizon_hours": 24,
    "root_cause_summary": "Likely upstream pump degradation causing unstable downstream pressure.",
    "confidence": 0.88,
    "recommended_action": "Inspect Pump P101 immediately and monitor pressure trend for the next 10 minutes.",
    "last_updated": now.strftime("%Y-%m-%d %H:%M:%S"),
}

audit_trace = [
    "Telemetry ingested from SWaT replay stream.",
    "Pressure deviation detected by anomaly agent.",
    "Root cause scored using graph-based dependency reasoning.",
    "Predictive agent estimated elevated failure risk.",
    "Decision agent generated operator recommendation.",
]

recommended_actions = [
    {
        "action": "Inspect Pump P101",
        "priority": "P1",
        "impact": "Low operational disruption",
        "approval_required": "Yes",
    },
    {
        "action": "Monitor pressure trend for 10 minutes",
        "priority": "P2",
        "impact": "No disruption",
        "approval_required": "No",
    },
    {
        "action": "Schedule maintenance within 24 hours",
        "priority": "P2",
        "impact": "Planned intervention",
        "approval_required": "Yes",
    },
]

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.markdown("## ⚙️ Demo Controls")
    st.selectbox("Environment", ["SWaT Replay Demo", "Simulation Demo"], index=0)
    st.selectbox("System Status", ["Critical", "Warning", "Normal"], index=0)
    st.selectbox("Asset Focus", ["P101", "P102", "FIT101", "LIT301"], index=0)
    st.slider("Time Window (minutes)", min_value=10, max_value=60, value=30)
    st.markdown("---")
    st.markdown("### 🧠 Active Modules")
    st.checkbox("Monitoring Agent", value=True)
    st.checkbox("Anomaly Detection Agent", value=True)
    st.checkbox("Root Cause Agent", value=True)
    st.checkbox("Predictive Maintenance Agent", value=True)
    st.checkbox("Decision Support Agent", value=True)
    st.checkbox("Explainability Agent", value=True)
    st.markdown("---")
    st.markdown(
        """
        <div class="small-muted">
        Static checkpoint prototype.<br>
        Backend and models can be connected later.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------
# Header
# ---------------------------
st.markdown('<div class="app-title">💧 Water Infrastructure Monitoring Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Multi-Agent Anomaly Detection & Predictive Maintenance Demo</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="status-banner status-critical">
        🚨 Critical incident detected in <b>{incident["affected_asset"]}</b> ·
        Zone: <b>{incident["zone"]}</b> ·
        Last updated: <b>{incident["last_updated"]}</b>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# KPI Cards
# ---------------------------
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        """
        <div class="card">
            <div class="card-title">Active Incidents</div>
            <div class="card-value">1</div>
            <div class="small-muted">1 critical · 0 resolved</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Affected Asset</div>
            <div class="card-value">{incident["affected_asset"]}</div>
            <div class="small-muted">{incident["zone"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Anomaly Score</div>
            <div class="card-value">{incident["anomaly_score"]:.2f}</div>
            <div class="small-muted">Severity: {incident["severity"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Failure Risk</div>
            <div class="card-value">{incident["failure_risk_score"]:.2f}</div>
            <div class="small-muted">Maintenance horizon: {incident["maintenance_horizon_hours"]} hrs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------
# Charts + Incident Summary
# ---------------------------
left, right = st.columns([1.55, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Sensor Trend View</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=times,
            y=pressure_values,
            mode="lines+markers",
            name="Pressure",
            line=dict(width=3),
        )
    )

    fig.add_vrect(
        x0=times[23],
        x1=times[-1],
        opacity=0.18,
        line_width=0,
        annotation_text="Abnormal region",
        annotation_position="top left",
    )

    fig.update_layout(
        height=360,
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis_title="Time",
        yaxis_title="Pressure",
        template="plotly_white",
        legend=dict(orientation="h", y=1.08, x=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=times,
            y=anomaly_scores,
            mode="lines+markers",
            name="Anomaly Score",
            line=dict(width=3),
        )
    )
    fig2.add_hline(y=0.7, line_dash="dash", annotation_text="Alert threshold", annotation_position="top left")
    fig2.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis_title="Time",
        yaxis_title="Score",
        template="plotly_white",
        legend=dict(orientation="h", y=1.08, x=0),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Incident Summary</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <span class="pill pill-red">HIGH SEVERITY</span>
        <span class="pill pill-yellow">ACTIVE</span>
        <span class="pill pill-green">HUMAN-IN-THE-LOOP</span>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"**Incident ID:** {incident['incident_id']}")
    st.markdown(f"**Affected Asset:** {incident['affected_asset']}")
    st.markdown(f"**Zone:** {incident['zone']}")
    st.markdown(f"**Confidence:** {incident['confidence']:.2f}")

    st.markdown("#### Root Cause Summary")
    st.info(incident["root_cause_summary"])

    st.markdown("#### Plain-English Explanation")
    st.write(
        "The system observed a sustained drop in downstream pressure while anomaly scores rose above the alert threshold. "
        "Based on graph dependencies and recent sensor behavior, the most likely explanation is degradation in the upstream pump."
    )

    st.markdown("#### Model Signals")
    st.progress(int(incident["anomaly_score"] * 100), text=f"Anomaly Score: {incident['anomaly_score']:.2f}")
    st.progress(int(incident["failure_risk_score"] * 100), text=f"Failure Risk: {incident['failure_risk_score']:.2f}")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Recommendation + Workflow
# ---------------------------
bottom_left, bottom_right = st.columns([1.2, 1])

with bottom_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recommended Actions</div>', unsafe_allow_html=True)

    for item in recommended_actions:
        st.markdown(
            f"""
            <div class="action-box">
                <b>{item["priority"]}</b> · <b>{item["action"]}</b><br>
                <span class="small-muted">Impact: {item["impact"]} · Approval required: {item["approval_required"]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("✅ Approve Action", use_container_width=True)
    with c2:
        st.button("👀 Monitor Only", use_container_width=True)
    with c3:
        st.button("📣 Escalate", use_container_width=True)

    st.markdown(
        f"""
        <div class="footer-note">
        Primary recommendation: {incident["recommended_action"]}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with bottom_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Agent Workflow / Audit Trace</div>', unsafe_allow_html=True)

    for i, step in enumerate(audit_trace, start=1):
        st.markdown(
            f"""
            <div class="trace-box">
                <b>Step {i}</b><br>
                <span class="small-muted">{step}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Digital Twin Snapshot")
    st.markdown(
        """
        <div>
            <span class="network-node node-normal">Reservoir</span>
            <span class="network-node node-warning">Valve V12</span>
            <span class="network-node node-critical">Pump P101</span>
            <span class="network-node node-normal">Sensor FIT101</span>
            <span class="network-node node-normal">Pipe Segment A</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="footer-note">
        Critical node highlighted in red. This placeholder view can later be replaced by a live graph visualization.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Footer
# ---------------------------
st.markdown(
    """
    <div class="card">
        <div class="section-title">Checkpoint Demo Scope</div>
        <div class="small-muted">
        Static prototype showing anomaly alerting, incident explanation, risk scoring, recommended actions, and agent workflow.
        This screen can later be connected to FastAPI endpoints and live model outputs.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)