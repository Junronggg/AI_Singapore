import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

BACKEND_URL = "http://127.0.0.1:8000"

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

def get_latest():
    try:
        r = requests.get(f"{BACKEND_URL}/dashboard/latest", timeout=3)
        return r.json()
    except Exception:
        return None

def get_history():
    try:
        r = requests.get(f"{BACKEND_URL}/dashboard/history", timeout=3)
        return r.json().get("items", [])
    except Exception:
        return []

def start_demo():
    try:
        requests.post(f"{BACKEND_URL}/demo/start", timeout=3)
    except Exception:
        pass

def stop_demo():
    try:
        requests.post(f"{BACKEND_URL}/demo/stop", timeout=3)
    except Exception:
        pass

latest = get_latest()
history = get_history()

# fallback stub if backend not yet started
if not latest or "message" in latest:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    latest = {
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
        "last_updated": now,
        "system_status": "Critical",
        "likely_root_cause": "P101",
        "affected_components": ["P101", "FIT101", "LIT101"],
        "persistence_count": 7,
        "audit_trace": [
            "Telemetry ingested from SWaT replay stream.",
            "Pressure deviation detected by anomaly agent.",
            "Root cause scored using feature deviation ranking.",
            "Predictive agent estimated elevated failure risk.",
            "Decision agent generated operator recommendation.",
            "Explainability and digital twin remain stubbed for MVP.",
        ],
        "recommended_actions": [
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
        ],
        "digital_twin_nodes": [
            {"name": "Reservoir", "status": "normal"},
            {"name": "Valve V12", "status": "warning"},
            {"name": "Pump P101", "status": "critical"},
            {"name": "Sensor FIT101", "status": "normal"},
            {"name": "Pipe Segment A", "status": "normal"},
        ],
        "plain_explanation": "The system observed a sustained abnormal pattern and elevated risk around P101.",
    }
    history = []

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.markdown("## ⚙️ Demo Controls")
    st.selectbox("Environment", ["SWaT Replay Demo", "Simulation Demo"], index=0)
    st.selectbox("System Status", ["Critical", "Warning", "Normal"], index=0)
    st.selectbox("Asset Focus", ["P101", "P102", "FIT101", "LIT301"], index=0)
    st.slider("Time Window (minutes)", min_value=10, max_value=60, value=30)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Start Demo", use_container_width=True):
            start_demo()
    with col2:
        if st.button("■ Stop Demo", use_container_width=True):
            stop_demo()

    st.markdown("---")
    st.markdown("### 🧠 Active Modules")
    st.checkbox("Monitoring Agent", value=True, disabled=True)
    st.checkbox("Anomaly Detection Agent", value=True, disabled=True)
    st.checkbox("Root Cause Agent", value=True, disabled=True)
    st.checkbox("Predictive Maintenance Agent", value=True, disabled=True)
    st.checkbox("Decision Support Agent", value=True, disabled=True)
    st.checkbox("Explainability Agent", value=False, disabled=True)

    st.markdown("---")
    st.markdown(
        """
        <div class="small-muted">
        Real backend connected for monitoring, anomaly, diagnosis, predictive risk, and decision support.<br>
        Explainability and digital twin are currently stubbed.
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

status_class = {
    "Critical": "status-critical",
    "Warning": "status-warning",
    "Normal": "status-normal",
}.get(latest["system_status"], "status-warning")

st.markdown(
    f"""
    <div class="status-banner {status_class}">
        🚨 {latest["system_status"]} incident detected in <b>{latest["affected_asset"]}</b> ·
        Zone: <b>{latest["zone"]}</b> ·
        Last updated: <b>{latest["last_updated"]}</b>
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
        f"""
        <div class="card">
            <div class="card-title">Active Incidents</div>
            <div class="card-value">1</div>
            <div class="small-muted">Status: {latest["status"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Affected Asset</div>
            <div class="card-value">{latest["affected_asset"]}</div>
            <div class="small-muted">{latest["zone"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Anomaly Score</div>
            <div class="card-value">{latest["anomaly_score"]:.2f}</div>
            <div class="small-muted">Severity: {latest["severity"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Failure Risk</div>
            <div class="card-value">{latest["failure_risk_score"]:.2f}</div>
            <div class="small-muted">Maintenance horizon: {latest["maintenance_horizon_hours"]} hrs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------
# Build chart data from history
# ---------------------------
if history:
    chart_times = [item["last_updated"] for item in history]
    anomaly_scores = [item["anomaly_score"] for item in history]
    risk_scores = [item["failure_risk_score"] for item in history]
else:
    chart_times = [latest["last_updated"]]
    anomaly_scores = [latest["anomaly_score"]]
    risk_scores = [latest["failure_risk_score"]]

# ---------------------------
# Charts + Incident Summary
# ---------------------------
left, right = st.columns([1.55, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Risk / Anomaly Trend View</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart_times,
            y=risk_scores,
            mode="lines+markers",
            name="Failure Risk",
            line=dict(width=3),
        )
    )
    fig.update_layout(
        height=360,
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis_title="Time",
        yaxis_title="Risk Score",
        template="plotly_white",
        legend=dict(orientation="h", y=1.08, x=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=chart_times,
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

    severity_class = "pill-red" if latest["severity"] == "HIGH" else ("pill-yellow" if latest["severity"] == "MEDIUM" else "pill-green")

    st.markdown(
        f"""
        <span class="pill {severity_class}">{latest["severity"]} SEVERITY</span>
        <span class="pill pill-yellow">{latest["status"]}</span>
        <span class="pill pill-green">HUMAN-IN-THE-LOOP</span>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"**Incident ID:** {latest['incident_id']}")
    st.markdown(f"**Affected Asset:** {latest['affected_asset']}")
    st.markdown(f"**Zone:** {latest['zone']}")
    st.markdown(f"**Confidence:** {latest['confidence']:.2f}")

    st.markdown("#### Root Cause Summary")
    st.info(latest["root_cause_summary"])

    st.markdown("#### Plain-English Explanation")
    st.write(latest["plain_explanation"])

    st.markdown("#### Model Signals")
    st.progress(int(latest["anomaly_score"] * 100), text=f"Anomaly Score: {latest['anomaly_score']:.2f}")
    st.progress(int(latest["failure_risk_score"] * 100), text=f"Failure Risk: {latest['failure_risk_score']:.2f}")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Recommendation + Workflow
# ---------------------------
bottom_left, bottom_right = st.columns([1.2, 1])

with bottom_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recommended Actions</div>', unsafe_allow_html=True)

    for item in latest["recommended_actions"]:
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
        Primary recommendation: {latest["recommended_action"]}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with bottom_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Agent Workflow / Audit Trace</div>', unsafe_allow_html=True)

    for i, step in enumerate(latest["audit_trace"], start=1):
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
    node_html = '<div>'
    for node in latest["digital_twin_nodes"]:
        cls = {
            "normal": "node-normal",
            "warning": "node-warning",
            "critical": "node-critical",
        }.get(node["status"], "node-normal")
        node_html += f'<span class="network-node {cls}">{node["name"]}</span>'
    node_html += "</div>"
    st.markdown(node_html, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="footer-note">
        This view is currently a stub. It can later be replaced by a live graph visualization.
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
        Real backend-connected monitoring, anomaly detection, diagnosis, predictive risk, and decision support.
        Explainability and digital twin are currently placeholder/stub views for the MVP.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)