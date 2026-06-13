# app.py — MaataRaksha v2 — Medical Dark Theme UI

import streamlit as st
import numpy as np
import joblib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
from huggingface_hub import hf_hub_download

st.set_page_config(
    page_title="MaataRaksha — Maternal Risk AI",
    page_icon="🤱",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

*  { box-sizing:border-box; margin:0; padding:0; }
html, body, [class*="css"] {
    font-family:'Plus Jakarta Sans',sans-serif !important;
}

/* Hide Streamlit branding */
footer,header,#MainMenu { visibility:hidden !important; }
.stDeployButton { display:none !important; }
._container_gzau3_1,._profileContainer_gzau3_53,
._viewerBadge_nim44_23 { display:none !important; }
a[href*="streamlit.io"],
a[href*="share.streamlit.io"] { display:none !important; }
[data-testid="stToolbar"] { display:none !important; }

/* Base */
.stApp { background:#060d1a !important; }

/* Animated ECG line background */
@keyframes ecgMove {
    0%   { transform:translateX(0); }
    100% { transform:translateX(-50%); }
}
.ecg-bg {
    position:fixed; top:0; left:0;
    width:200%; height:100%;
    background-image: repeating-linear-gradient(
        90deg,
        transparent 0px, transparent 80px,
        rgba(0,210,120,0.03) 80px, rgba(0,210,120,0.03) 81px
    );
    animation:ecgMove 20s linear infinite;
    pointer-events:none; z-index:0;
}

/* Glowing orbs */
@keyframes float1 {
    0%,100% { transform:translate(0,0) scale(1); }
    33%     { transform:translate(30px,-40px) scale(1.05); }
    66%     { transform:translate(-20px,20px) scale(0.95); }
}
@keyframes float2 {
    0%,100% { transform:translate(0,0) scale(1); }
    50%     { transform:translate(-40px,30px) scale(1.08); }
}

.orb {
    position:fixed; border-radius:50%;
    filter:blur(100px); pointer-events:none; z-index:0;
}
.orb-1 {
    width:500px; height:500px; opacity:0.07;
    background:radial-gradient(circle,#00d278,#00a86b);
    top:-150px; left:-150px;
    animation:float1 12s ease-in-out infinite;
}
.orb-2 {
    width:400px; height:400px; opacity:0.06;
    background:radial-gradient(circle,#0066ff,#0044cc);
    bottom:-100px; right:-100px;
    animation:float2 15s ease-in-out infinite;
}
.orb-3 {
    width:280px; height:280px; opacity:0.05;
    background:radial-gradient(circle,#ff4d6d,#c9184a);
    top:45%; left:48%;
    animation:float1 9s ease-in-out infinite reverse;
}

/* Heartbeat pulse dot */
@keyframes heartbeat {
    0%,100% { transform:scale(1);   opacity:1; }
    14%     { transform:scale(1.3); opacity:0.8; }
    28%     { transform:scale(1);   opacity:1; }
    42%     { transform:scale(1.2); opacity:0.9; }
    70%     { transform:scale(1);   opacity:1; }
}
.pulse-dot {
    display:inline-block;
    width:10px; height:10px;
    background:#00d278; border-radius:50%;
    margin-right:8px;
    animation:heartbeat 1.5s ease-in-out infinite;
    box-shadow:0 0 12px rgba(0,210,120,0.6);
}

/* Hero */
@keyframes fadeSlideUp {
    from { opacity:0; transform:translateY(32px); }
    to   { opacity:1; transform:translateY(0); }
}
.hero {
    text-align:center; padding:52px 20px 36px;
    position:relative; z-index:1;
    animation:fadeSlideUp 0.9s cubic-bezier(0.16,1,0.3,1) forwards;
}
.hero-eyebrow {
    display:inline-flex; align-items:center;
    background:rgba(0,210,120,0.1);
    border:1px solid rgba(0,210,120,0.25);
    color:#00d278; padding:6px 18px;
    border-radius:50px; font-size:11px;
    font-weight:700; letter-spacing:3px;
    text-transform:uppercase; margin-bottom:22px;
}

@keyframes shimmer {
    0%   { background-position:0% 50%; }
    50%  { background-position:100% 50%; }
    100% { background-position:0% 50%; }
}
.hero-title {
    font-size:76px; font-weight:800; line-height:1;
    background:linear-gradient(
        135deg,
        #ffffff 0%,
        #a8f5d0 30%,
        #00d278 60%,
        #ffffff 100%
    );
    background-size:300% 300%;
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    background-clip:text;
    animation:shimmer 6s ease infinite;
    margin-bottom:6px;
}
.hero-title-hindi {
    font-size:28px; font-weight:600;
    color:rgba(255,255,255,0.25);
    margin-bottom:16px;
    letter-spacing:2px;
}
.hero-sub {
    font-size:16px; color:rgba(255,255,255,0.42);
    max-width:500px; margin:0 auto 28px;
    line-height:1.8; font-weight:400;
}
.hero-pills {
    display:flex; justify-content:center;
    gap:10px; flex-wrap:wrap;
}
.hero-pill {
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.1);
    color:rgba(255,255,255,0.6);
    padding:5px 14px; border-radius:50px;
    font-size:12px; font-weight:500;
}

/* Stat cards */
.stats-grid {
    display:grid; grid-template-columns:repeat(4,1fr);
    gap:14px; margin:0 0 28px;
    position:relative; z-index:1;
}
@keyframes cardIn {
    from { opacity:0; transform:translateY(16px); }
    to   { opacity:1; transform:translateY(0); }
}
.stat-card {
    background:rgba(255,255,255,0.028);
    border:1px solid rgba(255,255,255,0.07);
    border-radius:16px; padding:20px 16px;
    text-align:center; position:relative;
    overflow:hidden; transition:all 0.35s;
    animation:cardIn 0.6s ease forwards;
    backdrop-filter:blur(12px);
}
.stat-card::before {
    content:''; position:absolute;
    top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,#00d278,#0066ff);
    opacity:0; transition:opacity 0.3s;
}
.stat-card:hover {
    background:rgba(0,210,120,0.06);
    border-color:rgba(0,210,120,0.25);
    transform:translateY(-4px);
}
.stat-card:hover::before { opacity:1; }

.stat-icon { font-size:24px; margin-bottom:8px; }
.stat-num {
    font-size:28px; font-weight:800;
    background:linear-gradient(135deg,#00d278,#00a8ff);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    background-clip:text;
}
.stat-lbl {
    font-size:11px; color:rgba(255,255,255,0.28);
    margin-top:4px; font-weight:500;
    letter-spacing:0.5px; line-height:1.4;
}

/* Form card */
.form-card {
    background:rgba(255,255,255,0.025);
    border:1px solid rgba(255,255,255,0.07);
    border-radius:22px; padding:30px;
    position:relative; z-index:1;
    backdrop-filter:blur(20px);
}

/* Section labels */
.sec-label {
    font-size:10px; font-weight:700;
    letter-spacing:3px; text-transform:uppercase;
    color:rgba(0,210,120,0.6); margin-bottom:14px;
    display:flex; align-items:center; gap:10px;
}
.sec-label::after {
    content:''; flex:1; height:1px;
    background:linear-gradient(90deg,
        rgba(0,210,120,0.2),transparent);
}

/* Sliders */
[data-testid="stSlider"] > div > div > div > div {
    background:linear-gradient(90deg,#00d278,#0066ff) !important;
}
[data-testid="stSlider"] label {
    color:rgba(255,255,255,0.65) !important;
    font-size:13px !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background:rgba(255,255,255,0.04) !important;
    border:1px solid rgba(255,255,255,0.1) !important;
    border-radius:10px !important;
    color:rgba(255,255,255,0.8) !important;
}

/* Radio */
.stRadio label { color:rgba(255,255,255,0.65) !important; }

/* Live threshold indicators */
.threshold-row {
    display:flex; gap:8px; flex-wrap:wrap;
    margin:6px 0 14px;
}
.thresh-chip {
    padding:3px 10px; border-radius:6px;
    font-size:11px; font-weight:600;
    font-family:'JetBrains Mono',monospace;
}
.thresh-ok   { background:rgba(0,210,120,0.12); color:#00d278;
               border:1px solid rgba(0,210,120,0.2); }
.thresh-warn { background:rgba(255,152,0,0.12); color:#ffa726;
               border:1px solid rgba(255,152,0,0.2); }
.thresh-crit { background:rgba(244,67,54,0.12); color:#ef5350;
               border:1px solid rgba(244,67,54,0.2); }

/* Analyze button */
@keyframes btnPulse {
    0%,100% { box-shadow:0 0 0 0 rgba(0,210,120,0.4); }
    50%     { box-shadow:0 0 0 16px rgba(0,210,120,0); }
}
.stButton > button {
    background:linear-gradient(135deg,#00d278,#0066ff) !important;
    color:white !important; border:none !important;
    border-radius:14px !important; padding:16px !important;
    font-size:16px !important; font-weight:700 !important;
    width:100% !important; letter-spacing:0.5px !important;
    font-family:'Plus Jakarta Sans',sans-serif !important;
    animation:btnPulse 2.5s ease-in-out infinite !important;
    transition:transform 0.2s, opacity 0.2s !important;
}
.stButton > button:hover {
    transform:translateY(-3px) !important;
    opacity:0.93 !important;
}

/* Result cards */
@keyframes resultPop {
    0%  { opacity:0; transform:scale(0.92) translateY(20px); }
    70% { transform:scale(1.02) translateY(-2px); }
    100%{ opacity:1; transform:scale(1) translateY(0); }
}

.result-card {
    border-radius:22px; padding:30px;
    position:relative; overflow:hidden;
    animation:resultPop 0.6s cubic-bezier(0.16,1,0.3,1) forwards;
}
.result-card::after {
    content:''; position:absolute;
    top:-50%; left:-50%;
    width:200%; height:200%;
    background:radial-gradient(
        circle at 50% 50%,
        rgba(255,255,255,0.04),
        transparent 70%
    );
    pointer-events:none;
}

.card-low {
    background:linear-gradient(
        135deg,
        rgba(0,210,120,0.08),
        rgba(0,168,96,0.04)
    );
    border:1px solid rgba(0,210,120,0.25);
}
.card-low::before {
    content:''; position:absolute;
    top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,#00d278,#8bc34a);
}

.card-mid {
    background:linear-gradient(
        135deg,
        rgba(255,152,0,0.08),
        rgba(255,193,7,0.04)
    );
    border:1px solid rgba(255,152,0,0.3);
}
.card-mid::before {
    content:''; position:absolute;
    top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,#ff9800,#ffc107);
}

@keyframes urgentPulse {
    0%,100% {
        background:linear-gradient(
            135deg,rgba(244,67,54,0.08),rgba(233,30,99,0.04));
        border-color:rgba(244,67,54,0.3);
    }
    50% {
        background:linear-gradient(
            135deg,rgba(244,67,54,0.16),rgba(233,30,99,0.08));
        border-color:rgba(244,67,54,0.55);
    }
}
.card-high {
    animation:resultPop 0.6s cubic-bezier(0.16,1,0.3,1) forwards,
              urgentPulse 2s ease-in-out 0.7s infinite !important;
    border:1px solid rgba(244,67,54,0.3);
}
.card-high::before {
    content:''; position:absolute;
    top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,#f44336,#e91e63);
}

.result-icon { font-size:44px; margin-bottom:12px; }
.result-level-low  {
    font-size:30px; font-weight:800; color:#00d278;
}
.result-level-mid  {
    font-size:30px; font-weight:800; color:#ffa726;
}
.result-level-high {
    font-size:30px; font-weight:800; color:#ef5350;
}
.result-action {
    font-size:14px; color:rgba(255,255,255,0.55);
    line-height:1.8; margin-top:10px;
}
.result-hindi {
    font-size:13px; color:rgba(255,255,255,0.28);
    margin-top:6px; line-height:1.6;
}

/* Probability meters */
.prob-section { margin-top:20px; }
.prob-row {
    display:flex; align-items:center;
    gap:10px; margin-bottom:10px;
}
.prob-label {
    font-size:12px; color:rgba(255,255,255,0.4);
    width:80px; flex-shrink:0;
    font-family:'JetBrains Mono',monospace;
}
.prob-track {
    flex:1; height:8px;
    background:rgba(255,255,255,0.06);
    border-radius:4px; overflow:hidden;
}
.prob-fill-low  {
    height:100%; border-radius:4px;
    background:linear-gradient(90deg,#00d278,#8bc34a);
    transition:width 0.8s cubic-bezier(0.16,1,0.3,1);
}
.prob-fill-mid  {
    height:100%; border-radius:4px;
    background:linear-gradient(90deg,#ff9800,#ffc107);
    transition:width 0.8s cubic-bezier(0.16,1,0.3,1);
}
.prob-fill-high {
    height:100%; border-radius:4px;
    background:linear-gradient(90deg,#f44336,#e91e63);
    transition:width 0.8s cubic-bezier(0.16,1,0.3,1);
}
.prob-pct {
    font-size:12px; color:rgba(255,255,255,0.5);
    width:42px; text-align:right;
    font-family:'JetBrains Mono',monospace;
}

/* Alert box */
.alert-critical {
    background:rgba(244,67,54,0.08);
    border:1px solid rgba(244,67,54,0.25);
    border-radius:12px; padding:14px 18px;
    margin-top:14px;
}
.alert-title {
    font-size:12px; font-weight:700;
    color:#ef5350; letter-spacing:1px;
    text-transform:uppercase; margin-bottom:6px;
}
.alert-item {
    font-size:13px; color:rgba(255,255,255,0.5);
    line-height:1.8;
}

/* Signal chips */
.signals-row {
    display:flex; gap:8px;
    flex-wrap:wrap; margin-top:16px;
}
.sig-chip {
    padding:4px 12px; border-radius:8px;
    font-size:11px; font-weight:600;
    font-family:'JetBrains Mono',monospace;
}
.sig-ok   { background:rgba(0,210,120,0.1); color:#00d278;
             border:1px solid rgba(0,210,120,0.2); }
.sig-warn { background:rgba(255,152,0,0.1); color:#ffa726;
             border:1px solid rgba(255,152,0,0.2); }
.sig-crit { background:rgba(244,67,54,0.1); color:#ef5350;
             border:1px solid rgba(244,67,54,0.2); }

/* Distance urgency */
.dist-alert {
    background:rgba(255,152,0,0.07);
    border:1px solid rgba(255,152,0,0.2);
    border-radius:12px; padding:12px 16px;
    margin-top:12px; font-size:13px;
    color:rgba(255,255,255,0.5); line-height:1.6;
}

/* Empty state */
.empty-state {
    background:rgba(255,255,255,0.018);
    border:1px dashed rgba(255,255,255,0.07);
    border-radius:22px; padding:70px 30px;
    text-align:center; position:relative;
    overflow:hidden;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background:rgba(6,13,26,0.97) !important;
    border-right:1px solid rgba(255,255,255,0.05) !important;
}
[data-testid="stSidebar"] * {
    color:rgba(255,255,255,0.6) !important;
}

.sb-logo {
    font-size:22px; font-weight:800;
    background:linear-gradient(135deg,#00d278,#00a8ff);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    background-clip:text;
}
.sb-div {
    height:1px;
    background:linear-gradient(90deg,
        rgba(0,210,120,0.2),transparent);
    margin:14px 0;
}
.sb-sec {
    font-size:9px; font-weight:700;
    letter-spacing:3px; text-transform:uppercase;
    color:rgba(0,210,120,0.4); margin-bottom:10px;
}
.risk-badge {
    display:flex; align-items:flex-start;
    gap:10px; margin-bottom:12px;
}
.rb-icon { font-size:18px; flex-shrink:0; }
.rb-level {
    font-size:13px; font-weight:600;
    color:rgba(255,255,255,0.7);
}
.rb-action {
    font-size:11px; color:rgba(255,255,255,0.3);
    margin-top:2px; line-height:1.5;
}
.thresh-list {
    font-size:12px; color:rgba(255,255,255,0.3);
    line-height:2.4;
}
</style>

<div class="ecg-bg"></div>
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="orb orb-3"></div>
""", unsafe_allow_html=True)

# ── Load model ────────────────────────────────────────────────
@st.cache_resource
def load_model():
    HF_REPO  = "maitry30/maataraksha-maternal-risk"
    hf_token = st.secrets["HF_TOKEN"]

    model_path  = hf_hub_download(
        repo_id=HF_REPO, filename="maternal_model.pkl",
        token=hf_token
    )
    scaler_path = hf_hub_download(
        repo_id=HF_REPO, filename="maternal_scaler.pkl",
        token=hf_token
    )
    feats_path  = hf_hub_download(
        repo_id=HF_REPO, filename="feature_cols.pkl",
        token=hf_token
    )
    risk_path   = hf_hub_download(
        repo_id=HF_REPO, filename="risk_mapping.json",
        token=hf_token
    )

    model        = joblib.load(model_path)
    scaler       = joblib.load(scaler_path)
    feature_cols = joblib.load(feats_path)
    with open(risk_path) as f:
        risk_map = json.load(f)
    return model, scaler, feature_cols, risk_map

import joblib
model, scaler, feature_cols, risk_map = load_model()

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">
        <span class="pulse-dot"></span>
        AI · Maternal Health · Rural India
    </div>
    <div class="hero-title">🤱 MaataRaksha</div>
    <div class="hero-title-hindi">माता रक्षा</div>
    <div class="hero-sub">
        Instant maternal risk assessment for ASHA workers —
        no doctor, no EHR, no internet required
    </div>
    <div class="hero-pills">
        <span class="hero-pill">ASHA Worker Tool</span>
        <span class="hero-pill">Offline Capable</span>
        <span class="hero-pill">Hindi + English</span>
        <span class="hero-pill">13 Clinical Features</span>
        <span class="hero-pill">XGBoost Ensemble</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────
st.markdown("""
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-icon">💀</div>
        <div class="stat-num">12%</div>
        <div class="stat-lbl">of global maternal deaths from India</div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">👩‍⚕️</div>
        <div class="stat-num">1M+</div>
        <div class="stat-lbl">ASHA workers across India</div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">🧬</div>
        <div class="stat-num">13</div>
        <div class="stat-lbl">clinical features including 7 ASHA-specific</div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-num">87%</div>
        <div class="stat-lbl">accuracy — 3-class medical prediction</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Main layout ───────────────────────────────────────────────
left_col, right_col = st.columns([3, 2], gap="large")

with left_col:
    st.markdown('<div class="form-card">', unsafe_allow_html=True)

    # ── Section 1: Basic Info ─────────────────────────────────
    st.markdown(
        '<div class="sec-label">Patient Basic Information</div>',
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        age = st.slider(
            "Age (years)", 15, 50, 25,
            help="Teen (<19) and older (>35) mothers are high risk"
        )
        # Live age indicator
        if age < 19:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-crit">'
                f'⚠ Teen mother — High Risk</span></div>',
                unsafe_allow_html=True
            )
        elif age > 35:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-warn">'
                f'⚠ Age >35 — Watch</span></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-ok">'
                f'✓ Normal age range</span></div>',
                unsafe_allow_html=True
            )

    with c2:
        parity = st.selectbox(
            "Parity (previous pregnancies)",
            [0, 1, 2, 3],
            format_func=lambda x: (
                "0 — First pregnancy" if x == 0
                else f"{x} previous pregnancies"
            )
        )
        if parity >= 3:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-warn">'
                '⚠ High parity</span></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-ok">'
                '✓ Normal parity</span></div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section 2: Vitals ─────────────────────────────────────
    st.markdown(
        '<div class="sec-label">Vital Signs</div>',
        unsafe_allow_html=True
    )
    c3, c4 = st.columns(2)
    with c3:
        systolic_bp = st.slider(
            "Systolic BP (mmHg)", 70, 180, 110
        )
        if systolic_bp >= 140:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-crit">'
                f'🚨 {systolic_bp} — Pre-eclampsia!</span></div>',
                unsafe_allow_html=True
            )
        elif systolic_bp >= 120:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-warn">'
                f'⚠ {systolic_bp} — Elevated</span></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-ok">'
                f'✓ {systolic_bp} — Normal</span></div>',
                unsafe_allow_html=True
            )

        diastolic_bp = st.slider(
            "Diastolic BP (mmHg)", 50, 120, 70
        )

    with c4:
        heart_rate = st.slider(
            "Heart Rate (bpm)", 50, 120, 75
        )
        body_temp = st.slider(
            "Body Temperature (°F)",
            97.0, 103.0, 98.6, step=0.1
        )
        if body_temp >= 100.4:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-warn">'
                f'⚠ {body_temp}°F — Fever</span></div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section 3: Lab Values ─────────────────────────────────
    st.markdown(
        '<div class="sec-label">Lab and Clinical Values</div>',
        unsafe_allow_html=True
    )
    c5, c6 = st.columns(2)
    with c5:
        haemoglobin = st.slider(
            "Haemoglobin (g/dL)",
            5.0, 15.0, 11.0, step=0.1
        )
        if haemoglobin < 7:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-crit">'
                f'🚨 Hb {haemoglobin} — Severe anaemia!</span></div>',
                unsafe_allow_html=True
            )
        elif haemoglobin < 10:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-warn">'
                f'⚠ Hb {haemoglobin} — Anaemia</span></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-ok">'
                f'✓ Hb {haemoglobin} — Normal</span></div>',
                unsafe_allow_html=True
            )

        blood_sugar = st.slider(
            "Blood Sugar (mmol/L)",
            6.0, 20.0, 8.0, step=0.1
        )

    with c6:
        gestational_age = st.slider(
            "Gestational Age (weeks)", 8, 42, 28
        )
        weight_gain = st.slider(
            "Weight Gain this month (kg)",
            0.0, 8.0, 1.5, step=0.1
        )
        if weight_gain > 3:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-crit">'
                f'🚨 {weight_gain}kg — Excessive!</span></div>',
                unsafe_allow_html=True
            )
        elif weight_gain > 2:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-warn">'
                f'⚠ {weight_gain}kg — Watch</span></div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section 4: Observable Signs ───────────────────────────
    st.markdown(
        '<div class="sec-label">'
        'Observable Signs — No Lab Needed</div>',
        unsafe_allow_html=True
    )
    c7, c8 = st.columns(2)
    with c7:
        oedema = st.radio(
            "Oedema (hands/feet swelling)?",
            ['No', 'Yes'], horizontal=True
        )
        prev_comp = st.radio(
            "Previous complications?",
            ['No', 'Yes'], horizontal=True,
            help="C-section, miscarriage, stillbirth"
        )
    with c8:
        distance = st.slider(
            "Distance to nearest hospital (km)",
            1, 80, 10
        )
        if distance > 30:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-crit">'
                f'🚨 {distance}km — Very remote!</span></div>',
                unsafe_allow_html=True
            )
        elif distance > 15:
            st.markdown(
                '<div class="threshold-row">'
                '<span class="thresh-chip thresh-warn">'
                f'⚠ {distance}km — Remote</span></div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button(
        "⚡ Assess Maternal Risk Now",
        type="primary"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ── Results column ────────────────────────────────────────────
with right_col:
    if predict_btn:
        input_data = np.array([[
            age, systolic_bp, diastolic_bp,
            blood_sugar, body_temp, heart_rate,
            haemoglobin, gestational_age, parity,
            1 if oedema == 'Yes' else 0,
            1 if prev_comp == 'Yes' else 0,
            distance, weight_gain
        ]])

        input_scaled = scaler.transform(input_data)

        with st.spinner("Analyzing clinical signals..."):
            time.sleep(0.5)
            pred       = model.predict(input_scaled)[0]
            pred_proba = model.predict_proba(input_scaled)[0]

        risk_names = ['Low Risk', 'Mid Risk', 'High Risk']

        # ── Result card ───────────────────────────────────────
        if pred == 0:
            css   = "result-card card-low"
            icon  = "✅"
            lvl   = "result-level-low"
            label = "LOW RISK"
            action= "Continue regular check-ins every 4 weeks. No immediate action needed."
            hindi = "हर 4 हफ्ते में नियमित जांच करें।"
        elif pred == 1:
            css   = "result-card card-mid"
            icon  = "⚠️"
            lvl   = "result-level-mid"
            label = "MODERATE RISK"
            action= "Visit ANM within 1 week. Monitor BP and Hb closely."
            hindi = "1 हफ्ते में ANM के पास जाएं। BP और Hb की निगरानी करें।"
        else:
            css   = "result-card card-high"
            icon  = "🚨"
            lvl   = "result-level-high"
            label = "HIGH RISK"
            action= "Refer to PHC TODAY. Possible pre-eclampsia or severe anaemia. Alert supervisor IMMEDIATELY."
            hindi = "आज ही PHC भेजें। तुरंत सुपरवाइज़र को बताएं।"

        st.markdown(f"""
        <div class="{css}">
            <div class="result-icon">{icon}</div>
            <div class="{lvl}">{label}</div>
            <div class="result-action">{action}</div>
            <div class="result-hindi">{hindi}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Critical alerts ───────────────────────────────────
        alerts = []
        if systolic_bp >= 140:
            alerts.append(f"BP {systolic_bp} mmHg — Pre-eclampsia!")
        if haemoglobin < 7:
            alerts.append(f"Hb {haemoglobin} g/dL — Severe anaemia!")
        if weight_gain > 3:
            alerts.append(f"Weight gain {weight_gain} kg — Excessive!")
        if oedema == 'Yes' and systolic_bp >= 130:
            alerts.append("Oedema + High BP — Pre-eclampsia combo!")

        if alerts:
            items = "".join(
                [f'<div class="alert-item">⚠ {a}</div>'
                 for a in alerts]
            )
            st.markdown(f"""
            <div class="alert-critical">
                <div class="alert-title">Critical Values Detected</div>
                {items}
            </div>
            """, unsafe_allow_html=True)

        # ── Probability meters ────────────────────────────────
        st.markdown("""
        <div class="sec-label" style="margin-top:20px">
            Risk Probability
        </div>
        """, unsafe_allow_html=True)

        fills = ['prob-fill-low','prob-fill-mid','prob-fill-high']
        for rname, prob, fill in zip(risk_names, pred_proba, fills):
            st.markdown(f"""
            <div class="prob-row">
                <div class="prob-label">{rname.split()[0]}</div>
                <div class="prob-track">
                    <div class="{fill}"
                         style="width:{prob*100:.0f}%"></div>
                </div>
                <div class="prob-pct">{prob*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Signal chips ──────────────────────────────────────
        st.markdown("""
        <div class="sec-label" style="margin-top:16px">
            Key Clinical Signals
        </div>
        """, unsafe_allow_html=True)

        def chip(label, val, ok_thresh, warn_thresh, lower_bad=False):
            if lower_bad:
                cls = (
                    "sig-crit" if val < ok_thresh
                    else "sig-warn" if val < warn_thresh
                    else "sig-ok"
                )
            else:
                cls = (
                    "sig-crit" if val >= warn_thresh
                    else "sig-warn" if val >= ok_thresh
                    else "sig-ok"
                )
            return (
                f'<span class="sig-chip {cls}">'
                f'{label}: {val}</span>'
            )

        chips = "".join([
            chip("BP", systolic_bp, 120, 140),
            chip("Hb", haemoglobin, 10, 7, lower_bad=True),
            f'<span class="sig-chip '
            f'{"sig-crit" if oedema=="Yes" else "sig-ok"}">'
            f'Oedema: {oedema}</span>',
            f'<span class="sig-chip '
            f'{"sig-warn" if prev_comp=="Yes" else "sig-ok"}">'
            f'Prev Comp: {prev_comp}</span>',
            chip("Wt Gain", weight_gain, 2, 3),
        ])
        st.markdown(
            f'<div class="signals-row">{chips}</div>',
            unsafe_allow_html=True
        )

        # ── Distance urgency ──────────────────────────────────
        if pred == 2 and distance > 20:
            st.markdown(f"""
            <div class="dist-alert">
                🚗 Hospital is <b>{distance} km</b> away.
                Arrange transport IMMEDIATELY —
                do not wait for next visit.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:10px;color:rgba(255,255,255,0.15);
                    margin-top:18px;line-height:1.6">
            AI support tool only. Final decision must
            involve a qualified medical professional.
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="empty-state">
            <div style="font-size:50px;margin-bottom:18px">🤱</div>
            <div style="font-size:15px;
                        color:rgba(255,255,255,0.2);
                        line-height:1.9">
                Fill in the patient details<br>
                and click Assess Maternal Risk
            </div>
            <div style="font-size:12px;
                        color:rgba(0,210,120,0.3);
                        margin-top:14px">
                <span class="pulse-dot"
                      style="width:6px;height:6px"></span>
                AI model ready
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">🤱 MaataRaksha</div>
    <div style="font-size:11px;color:rgba(255,255,255,0.2);
                margin-bottom:2px;font-style:italic">
        माता रक्षा — Maternal Health AI
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-div"></div>',
                unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">Risk Levels</div>',
                unsafe_allow_html=True)

    for icon, level, action in [
        ("✅", "Low Risk",      "Check-in every 4 weeks"),
        ("⚠️", "Moderate Risk", "Visit ANM within 1 week"),
        ("🚨", "High Risk",     "Refer to PHC TODAY"),
    ]:
        st.markdown(f"""
        <div class="risk-badge">
            <div class="rb-icon">{icon}</div>
            <div>
                <div class="rb-level">{level}</div>
                <div class="rb-action">{action}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sb-div"></div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="sb-sec">Critical Thresholds</div>',
        unsafe_allow_html=True
    )
    st.markdown("""
    <div class="thresh-list">
        🔴 BP ≥ 140 → Pre-eclampsia<br>
        🔴 Hb &lt; 7 g/dL → Severe anaemia<br>
        🔴 Weight gain &gt; 3 kg/month<br>
        🔴 Oedema + high BP together<br>
        🟡 Age &lt; 19 or &gt; 35<br>
        🟡 Parity ≥ 3 pregnancies<br>
        🟡 Distance &gt; 30 km
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-div"></div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="sb-sec">Model</div>',
        unsafe_allow_html=True
    )
    st.markdown("""
    <div style="font-size:11px;color:rgba(255,255,255,0.28);
                line-height:2.2">
        XGBoost + RF + GB Ensemble<br>
        Accuracy: ~87%<br>
        Features: 13 (6 original + 7 ASHA)<br>
        Dataset: UCI Maternal Health Risk<br>
        Works offline · No EHR needed
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-div"></div>',
                unsafe_allow_html=True)

    try:
        st.image(
            'shap_high_risk.png',
            caption='SHAP — Top features for High Risk',
            use_column_width=True
        )
    except Exception:
        pass