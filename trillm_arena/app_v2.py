import streamlit as st
import json
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import subprocess
import os
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Startup Metadata
BRAND_NAME = "RATIO"
TAGLINE = "The Ratiocination Arena"
VERSION = "3.1.0"
SESSION_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from trillm_arena.debate_engine_iterative import run_iterative_debate, DebateError
    from trillm_arena.model_config import get_model_config
    from trillm_arena.database import db
except ImportError:
    from debate_engine_iterative import run_iterative_debate, DebateError
    from model_config import get_model_config
    from database import db

MODEL_CONFIG = get_model_config()
MODEL_A_ID = MODEL_CONFIG.model_a_id
MODEL_B_ID = MODEL_CONFIG.model_b_id
JUDGE_ID = MODEL_CONFIG.judge_id
MODEL_A_LABEL = MODEL_CONFIG.model_a_label
MODEL_B_LABEL = MODEL_CONFIG.model_b_label
JUDGE_LABEL = MODEL_CONFIG.judge_label

# ===== Page Configuration =====
st.set_page_config(
    page_title=f"{BRAND_NAME} | {TAGLINE}",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== STARTUP GRADE CSS (Glassmorphism & Professional Dark Mode) =====
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Modern Dark Theme */
    .stApp {
        background-color: #0b0e14;
        background-image: 
            radial-gradient(at 0% 0%, rgba(102, 126, 234, 0.1) 0, transparent 50%),
            radial-gradient(at 100% 100%, rgba(118, 75, 162, 0.1) 0, transparent 50%);
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }

    /* Header Styling */
    .startup-header {
        text-align: center;
        padding: 3rem 0;
        margin-bottom: 2rem;
    }
    
    .startup-header h1 {
        font-size: 5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -2px;
        margin-bottom: 0;
    }
    
    .startup-header p {
        font-size: 1.4rem;
        color: #888;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Round Badges */
    .badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .badge-primary { background: rgba(102, 126, 234, 0.2); color: #667eea; border: 1px solid #667eea; }
    .badge-secondary { background: rgba(255, 107, 53, 0.2); color: #ff6b35; border: 1px solid #ff6b35; }
    .badge-success { background: rgba(0, 184, 148, 0.2); color: #00b894; border: 1px solid #00b894; }

    /* Custom Input */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 1rem !important;
    }

    /* Custom Button */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        padding: 0.8rem !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }

    /* Metric Overrides */
    [data-testid="stMetricValue"] {
        font-weight: 900 !important;
        color: #667eea !important;
    }

    /* Sidebar Fixes */
    section[data-testid="stSidebar"] {
        background-color: #0b0e14 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown(f"""
    <div class="startup-header">
        <h1>{BRAND_NAME}</h1>
        <p>{TAGLINE}</p>
    </div>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.image("https://api.iconify.design/heroicons:bolt-20-solid.svg?color=%23667eea", width=50)
    st.markdown(f"## {BRAND_NAME}")
    st.caption(TAGLINE)
    st.divider()
    
    st.markdown("### 🛠️ Configuration")
    rounds = st.slider("Debate Depth (Rounds)", 1, 5, 3)
    
    st.divider()
    
    # Ecosystem Status (Cloud Health)
    st.markdown("### ☁️ Ecosystem Status")
    is_cloud_prod = os.getenv("IS_PRODUCTION", "true").lower() == "true"
    has_router_key = os.getenv("OPENROUTER_API_KEY") is not None
    
    if has_router_key:
        st.success("API: CLOUD ACTIVE")
    else:
        st.warning("API: LOCAL MODE")

    if os.getenv("SUPABASE_URL") and "your_supabase" not in os.getenv("SUPABASE_URL"):
        st.success("DB: SYNCHRONIZED")
    else:
        st.error("DB: LOCAL ONLY")

    st.divider()
    
    # Model Specs
    with st.expander("🤖 Active Model Registry"):
        st.caption(f"A: {MODEL_A_LABEL}")
        st.caption(f"B: {MODEL_B_LABEL}")
        st.caption(f"Judge: {JUDGE_LABEL}")

# ===== NAVIGATION TABS =====
tab_arena, tab_gallery, tab_stats, tab_edge = st.tabs([
    "⚔️ Battle Arena", 
    "🎬 Live Gallery", 
    "📊 Model Leaderboards", 
    "⚡ Edge Node (P2P)"
])

# -----------------------------
# TAB 1: BATTLE ARENA (Cloud/Local API)
# -----------------------------
with tab_arena:
    st.caption("Standard mode using OpenRouter or Local Worker.")
    col1, col2 = st.columns([4, 1.2])
    
    with col1:
        st.markdown("### 📢 Initiative Prompt")
        topic = st.text_input(
            "What is the focus of this ratiocination?",
            placeholder="e.g., The viability of Universal Basic Income in AI economies...",
            key="cloud_topic",
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("### &nbsp;", unsafe_allow_html=True)
        start_debate = st.button("EXECUTE PROTOCOL")

    if start_debate:
        if not topic or len(topic.strip()) < 3:
            st.warning("⚠️ Topic requires at least 3 characters.")
        else:
            try:
                # HYBRID LOGIC: If Cloud and no API key, use Task Queue
                is_prod = os.getenv("IS_PRODUCTION", "true").lower() == "true"
                has_api = os.getenv("OPENROUTER_API_KEY") is not None
                
                if is_prod and not has_api:
                    st.info("📡 **No API Key detected. Routing to Private Local Node...**")
                    req_id = db.create_debate_request(topic, rounds, [MODEL_A_ID, MODEL_B_ID])
                    
                    if req_id:
                        placeholder = st.empty()
                        with placeholder.container():
                            st.warning(f"⏳ **Request Queued (ID: {req_id})**")
                            status_label = st.empty()
                            progress = st.progress(0)
                            
                            for i in range(120):
                                status = db.check_request_status(req_id)
                                current_s = status.get('status') if status else 'pending'
                                
                                if current_s == 'processing':
                                    status_label.info("⚔️ **Model Node Active: Running Llama 3.1 & 3.2...**")
                                    progress.progress(50)
                                elif current_s == 'completed':
                                    status_label.success("✅ **Debate Complete! Loading...**")
                                    progress.progress(100)
                                    time.sleep(2)
                                    st.rerun()
                                    break
                                elif current_s == 'failed':
                                    status_label.error("❌ **Local Node Error.**")
                                    break
                                else:
                                    status_label.caption(f"Waiting for your local node... ({i+1}/120)")
                                    progress.progress(min((i+1)/120, 0.45))
                                time.sleep(5)
                    else:
                        st.error("Could not register request.")
                
                else:
                    # DIRECT EXECUTION
                    placeholder = st.empty()
                    with placeholder.container():
                        st.info("🔬 **Orchestrating Model Agents...**")
                        res = run_iterative_debate(topic, rounds, MODEL_A_ID, MODEL_B_ID, JUDGE_ID)
                        db.save_debate(res)
                        st.success("✅ Protocol Completed.")
                        time.sleep(1)
                        st.rerun()

            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

# -----------------------------
# TAB 2: LIVE GALLERY
# -----------------------------
with tab_gallery:
    st.markdown("### 🎬 Archive of Intelligence")
    debates = db.get_recent_debates(limit=10)
    
    if not debates:
        st.info("No recorded debates yet.")
    else:
        for d in debates:
            with st.container():
                t_topic = d.get('topic', 'Untitled')
                t_winner = d.get('winner', 'TIE')
                t_reasoning = d.get('reasoning', '')
                t_created = d.get('created_at', '')[:19].replace('T', ' ')
                
                st.markdown(f"""
                    <div class="glass-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0;">{t_topic}</h4>
                            <span class="badge badge-primary">WINNER: {t_winner}</span>
                        </div>
                        <p style="color:#888; font-size:0.9rem; margin-top:10px;">{t_reasoning[:250]}...</p>
                        <small style="color:#555;">{t_created} | vs {d.get('model_a')} & {d.get('model_b')}</small>
                    </div>
                """, unsafe_allow_html=True)

# -----------------------------
# TAB 3: LEADERBOARDS
# -----------------------------
with tab_stats:
    st.markdown("### 📊 Ecosystem Intelligence")
    all_d = db.get_recent_debates(limit=100)
    if all_d:
        wins = {"Model A": 0, "Model B": 0, "TIE": 0}
        for d in all_d:
            w = d.get('winner', 'TIE')
            if "Model A" in str(w): wins["Model A"] += 1
            elif "Model B" in str(w): wins["Model B"] += 1
            else: wins["TIE"] += 1
        
        c1, c2, c3 = st.columns(3)
        c1.metric(f"🔵 {MODEL_A_LABEL} Wins", wins["Model A"])
        c2.metric(f"🟠 {MODEL_B_LABEL} Wins", wins["Model B"])
        c3.metric("🤝 Ties", wins["TIE"])
    else:
        st.info("Stats will populate soon.")

# -----------------------------
# TAB 4: EDGE NODE (P2P Interface)
# -----------------------------
with tab_edge:
    st.markdown("### ⚡ RATIO Edge Protocol")
    st.markdown("""
        **Zero-Infrastructure Mode:** Downloads **Llama 3.2** directly to your browser. 
        Runs on your **GPU (WebGPU)**. *100% Private & Distributed.*
    """)
    
    e_topic = st.text_input("Browser Debate Topic:", "Is decentralized AI more robust than cloud AI?")
    e_rounds = st.slider("Browser Rounds", 1, 3, 2, key="edge_rounds_slider")
    
    import streamlit.components.v1 as components
    
    webllm_component = f"""
    <div id="status" style="color: #667eea; font-family: sans-serif; padding:15px; border-radius:12px; background: rgba(102,126,234,0.1); border: 1px solid #667eea;">
        Ready for Edge Activation...
    </div>
    <button id="run-btn" style="width: 100%; margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #667eea, #764ba2); color:white; border:none; border-radius:12px; font-weight:bold; cursor:pointer; font-family: sans-serif;">
        ACTIVATE EDGE NODE (Requires WebGPU)
    </button>
    <div id="log" style="height: 350px; overflow-y: auto; color: #00ff00; font-family: monospace; font-size: 0.85rem; padding: 15px; border-radius: 12px; background: #000; border: 1px solid #333;">
        [SYSTEM] Waiting for handshake...
    </div>

    <script type="module">
        import * as webllm from "https://cdn.jsdelivr.net/npm/@mlc-ai/web-llm/+esm";
        const logDiv = document.getElementById("log");
        const statusDiv = document.getElementById("status");
        const btn = document.getElementById("run-btn");

        function log(msg) {{
            const p = document.createElement("p");
            p.style.margin = "2px 0";
            p.textContent = `[NODE] ${{msg}}`;
            logDiv.appendChild(p);
            logDiv.scrollTop = logDiv.scrollHeight;
        }}

        btn.onclick = async () => {{
            btn.disabled = true;
            btn.textContent = "⚙️ INITIALIZING ENGINE...";
            log("Handshaking with WebGPU...");
            
            try {{
                const engine = await webllm.CreateMLCEngine(
                    "Llama-3.2-1B-Instruct-q4f16_1-MLC",
                    {{ initProgressCallback: (p) => {{
                        statusDiv.textContent = `📦 ${{p.text}} (${{Math.round(p.progress * 100)}}%)`;
                    }} }}
                );

                statusDiv.textContent = "⚔️ EDGE NODE ACTIVE";
                btn.textContent = "⚔️ RUNNING BATTLE...";
                
                let hist = [];
                for (let r = 0; r <= {e_rounds}; r++) {{
                    log(`STARTING ROUND ${{r}}...`);
                    const pA = r === 0 ? `Topic: {e_topic}. Short opening.` : `Respond: ${{hist[hist.length-1]}}`;
                    const rA = await engine.chat.completions.create({{ messages: [{{ role:"user", content:pA }}], max_tokens: 150 }});
                    const mA = rA.choices[0].message.content;
                    log(`🔵 [A]: ${{mA}}`);
                    hist.push(mA);

                    if (r === {e_rounds}) break;

                    const pB = `Counter: ${{mA}}`;
                    const rB = await engine.chat.completions.create({{ messages: [{{ role:"user", content:pB }}], max_tokens: 150 }});
                    const mB = rB.choices[0].message.content;
                    log(`🟠 [B]: ${{mB}}`);
                    hist.push(mB);
                }}
                log("### BATTLE SUCCESSFUL ###");
                btn.textContent = "✅ COMPLETED";
            }} catch (e) {{
                log(`!! ERROR: ${{e.message}}`);
                btn.disabled = false;
                btn.textContent = "RETRY ACTIVATION";
            }}
        }};
    </script>
    """
    components.html(webllm_component, height=600)

# ===== FOOTER =====
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: #444; padding: 2rem;">
        <p>© 2026 {BRAND_NAME} Intelligence | Version {VERSION} | Engineering by Soumyadarshan Dash</p>
        <p style="font-size:0.8rem">P2P Distribution / Edge Computing / Zero-Inference Cost</p>
    </div>
""", unsafe_allow_html=True)
