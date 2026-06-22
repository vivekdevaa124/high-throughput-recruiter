import streamlit as st  # pyrefly: ignore [missing-import]
import json
import pandas as pd  # pyrefly: ignore [missing-import]
import plotly.express as px  # pyrefly: ignore [missing-import]
import plotly.graph_objects as go  # pyrefly: ignore [missing-import]
import os

# Import the ranking logic from our optimized backend
from rank import score_candidate

# Configure page to match screenshot vibe
st.set_page_config(page_title="Redrob AI Recruiter", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for UI styling
st.markdown("""
<style>
    .reportview-container {
        background: #0E1117;
    }
    .main-header {
        background: linear-gradient(90deg, #5A32FA 0%, #8D52FA 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        width: 100%;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("Configuration")
jd_option = st.sidebar.selectbox("Job Description", ["Senior AI Engineer"])

st.sidebar.markdown("Upload candidate JSONL (<500 for demo)")
uploaded_file = st.sidebar.file_uploader("Drag and drop file here", type=['jsonl', 'json'])

use_bundled = st.sidebar.checkbox("Use bundled sample dataset", value=False)

top_n = st.sidebar.slider("Top N to display", min_value=10, max_value=100, value=25)

rank_btn = st.sidebar.button("🚀 Rank Candidates")

# --- MAIN CONTENT ---
st.markdown("""
<div class="main-header">
    <h1 style='margin:0; font-size:36px;'>🎯 Redrob AI Recruiter</h1>
    <p style='margin:0; opacity:0.8;'>Hybrid BM25 + TF-IDF + Recruiter-Feature Ranking (CPU, offline)</p>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ Architecture & Pipeline View"):
    st.write("1. JSONL ingested -> 2. Schema normalized -> 3. Evaluated against Honeypot patterns -> 4. Scored via heuristic matrix -> 5. Multipliers applied (Availability/Activity).")

if rank_btn:
    data_source = None
    if use_bundled:
        # Use local file if checkbox is checked
        if os.path.exists("candidates.jsonl"):
            data_source = "candidates.jsonl"
        else:
            st.error("Bundled dataset 'candidates.jsonl' not found in workspace.")
            st.stop()
    elif uploaded_file is not None:
        # User uploaded a file, we process it
        data_source = uploaded_file
    else:
        st.warning("Please upload a JSONL file or select 'Use bundled sample dataset'.")
        st.stop()

    # Processing pipeline
    candidates = []
    with st.spinner("Parsing and scoring candidates..."):
        # Handle file object vs string path securely
        if isinstance(data_source, str):
            with open(data_source, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = data_source.getvalue().decode('utf-8')
            
        candidates_data = []
        try:
            # First, try to parse the entire file as a standard JSON array/object
            parsed = json.loads(content)
            if isinstance(parsed, list):
                candidates_data = parsed
            else:
                candidates_data = [parsed]
        except json.JSONDecodeError:
            # If it fails, fallback to parsing it line-by-line as JSONL
            for line in content.splitlines():
                if not line.strip(): continue
                try:
                    candidates_data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
                    
        for cand in candidates_data:
            score, reasoning, details = score_candidate(cand)
            
            # Extract basic info for the UI
            profile = cand.get("profile", {})
            title = profile.get("current_title", "Unknown Role")
            exp = profile.get("years_of_experience", 0.0)
            
            candidates.append({
                "id": cand.get("candidate_id", "UNKNOWN"),
                "title": title,
                "exp": exp,
                "score": score,
                "reasoning": reasoning,
                "details": details
            })
            
    # Sort and slice
    candidates.sort(key=lambda x: (-x['score'], x['id']))
    
    total_profiles = len(candidates)
    recalled = len([c for c in candidates if c['score'] > 0])
    top_candidates = candidates[:top_n]
    
    top_score = top_candidates[0]['score'] if top_candidates else 0
    avg_top_n = sum([c['score'] for c in top_candidates]) / len(top_candidates) if top_candidates else 0

    # Render Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("PROFILES", total_profiles)
    col2.metric("RECALLED", recalled)
    col3.metric("TOP SCORE", f"{top_score:.2f}")
    col4.metric(f"AVG TOP-{top_n} SCORE", f"{avg_top_n:.2f}")
    
    st.markdown("---")
    
    # Render Score Distribution Chart
    st.subheader(f"Score Distribution (Top {top_n})")
    
    # Plotly bar chart
    scores = [c['score'] for c in top_candidates]
    x_labels = [str(i) for i in range(len(scores))]
    
    fig_dist = px.bar(
        x=x_labels, y=scores, 
        color_discrete_sequence=['#7EC8F9']
    )
    fig_dist.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
        xaxis_title="",
        yaxis_title=""
    )
    st.plotly_chart(fig_dist, use_container_width=True)
    
    st.markdown("---")
    st.subheader(f"Top {top_n} Ranked Candidates")
    
    # Render Expanders
    for i, cand in enumerate(top_candidates):
        rank = i + 1
        exp_header = f"#{rank} | {cand['title']} ({cand['exp']:.1f}y) | Score: {cand['score']:.3f}"
        
        with st.expander(exp_header, expanded=(i == 0)):
            st.markdown(f"**<span style='background:#C47B25; padding: 2px 6px; border-radius:4px; color:white'>Score: {cand['score']:.3f}</span> ID: {cand['id']}**", unsafe_allow_html=True)
            st.markdown(f"**Reasoning:** {cand['reasoning']}")
            
            st.markdown("**Score Components Breakdown**")
            
            # Plotly component chart
            comps = cand['details']['components']
            comp_names = list(comps.keys())
            comp_values = list(comps.values())
            
            fig_comp = px.bar(
                x=comp_names, y=comp_values,
                color_discrete_sequence=['#7EC8F9']
            )
            fig_comp.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=20, b=0),
                height=250,
                xaxis_title="",
                yaxis_title=""
            )
            fig_comp.update_yaxes(range=[0, 1])
            st.plotly_chart(fig_comp, use_container_width=True, key=f"comp_chart_{cand['id']}_{i}")
            
            # Metrics
            m = cand['details']['metrics']
            mc1, mc2, mc3, mc4, mc5 = st.columns(5)
            mc1.metric("Merit (Base)", f"{m.get('Merit (Base)', 0):.3f}")
            mc2.metric("Availability Mult", f"{m.get('Availability Mult', 0):.3f}")
            mc3.metric("Disqualifier Mult", f"{m.get('Disqualifier Mult', 0):.3f}")
            mc4.metric("Authenticity (Honeypot)", f"{m.get('Authenticity (Honeypot)', 0):.3f}")
            mc5.metric("Composite (Final)", f"{m.get('Composite (Final)', 0):.3f}")
else:
    st.info("Upload a JSONL file or check 'Use bundled sample dataset' and click 'Rank Candidates' to begin.")
