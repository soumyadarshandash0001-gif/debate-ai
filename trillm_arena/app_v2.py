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

# Simple cross-platform TTS
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Startup Metadata
BRAND_NAME = "RATIO"
TAGLINE = "The Ratiocination Arena"
VERSION = "3.0.0"
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

# ===== SIMPLE VOICE SYNTHESIS =====
def speak_text(text: str, model: str = "A") -> bool:
    """Simple cross-platform text-to-speech."""
    if not text or len(text.strip()) < 3:
        return False
    
    try:
        # Limit text to 500 chars for TTS
        text = text[:500]
        
        if sys.platform == "darwin":  # macOS
            # Use built-in say command
            os.system(f'say "{text}" 2>/dev/null &')
            return True
        elif sys.platform == "win32":  # Windows
            if HAS_PYTTSX3:
                try:
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
                    return True
                except:
                    return False
            return False
        else:  # Linux
            # Try espeak
            os.system(f'espeak "{text}" 2>/dev/null &')
            return True
    except Exception as e:
        logger.warning(f"TTS failed: {str(e)}")
        return False

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
    
    # Cloud Health
    st.markdown("### ☁️ Ecosystem Status")
    import os
    if os.getenv("OPENROUTER_API_KEY") and "your_openrouter" not in os.getenv("OPENROUTER_API_KEY"):
        st.success("API: ACTIVE")
    else:
        st.error("API: MISSING KEY")

    if os.getenv("SUPABASE_URL") and "your_supabase" not in os.getenv("SUPABASE_URL"):
        st.success("DB: SYNCHRONIZED")
    else:
        st.warning("DB: LOCAL ONLY")

    st.divider()
    
    # Model Specs
    with st.expander("🤖 Active Model Registry"):
        st.caption(f"A: {MODEL_A_LABEL}")
        st.caption(f"B: {MODEL_B_LABEL}")
        st.caption(f"Judge: {JUDGE_LABEL}")

# ===== NAVIGATION TABS =====
tab_arena, tab_gallery, tab_stats = st.tabs(["⚔️ Battle Arena", "🎬 Live Gallery", "📊 Model Leaderboards"])

# -----------------------------
# TAB 1: BATTLE ARENA
# -----------------------------
with tab_arena:
    col1, col2 = st.columns([4, 1.2])
    
    with col1:
        st.markdown("### 📢 Initiative Prompt")
        topic = st.text_input(
            "What is the focus of this ratiocination?",
            placeholder="e.g., The viability of Universal Basic Income in AI economies...",
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
                placeholder = st.empty()
                with placeholder.container():
                    st.info("🔬 **Orchestrating Model Agents...**")
                    progress = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress.progress(i + 1)
                
                # Execute Debate
                start_time = time.time()
                result = run_iterative_debate(
                    topic,
                    num_rounds=rounds,
                    model_a_id=MODEL_A_ID,
                    model_b_id=MODEL_B_ID,
                    judge_id=JUDGE_ID,
                )
                latency = time.time() - start_time
                
                # Persistence
                db.save_debate(result)
                placeholder.empty()
                
                # Display Results
                verdict_raw = result.get('verdict', '{}')
                try:
                    verdict_json = json.loads(verdict_raw)
                    winner_val = verdict_json.get('winner', 'TIE')
                except:
                    winner_val = "EVALUATED"

                st.markdown(f"### 🏆 Final Verdict: {winner_val}")
                
                # Display Metrics
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.metric("Latency", f"{latency:.2f}s")
                m_col2.metric("Rounds", f"{len(result['rounds'])}")
                m_col3.metric("Tokens", f"~{len(str(result)):,}")
                
                # Rounds View
                for rd in result['rounds']:
                    with st.expander(f"Round {rd['round']}: {rd['type'].title()}", expanded=(rd['round'] == 0)):
                        ca, cb = st.columns(2)
                        with ca:
                            st.markdown(f"**🔵 {MODEL_A_LABEL}**")
                            st.write(rd['model_a'])
                        with cb:
                            st.markdown(f"**🟠 {MODEL_B_LABEL}**")
                            st.write(rd['model_b'])

                # Conclusion
                verdict = json.loads(result['verdict'])
                st.markdown(f"""
                    <div class="glass-card">
                        <h4 style="color:#667eea">⚖️ Judicial Reasoning</h4>
                        <p style="color:#888">{verdict.get('reasoning')}</p>
                    </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

# -----------------------------
# TAB 2: LIVE GALLERY
# -----------------------------
with tab_gallery:
    st.markdown("### 🎬 Archive of Intelligence")
    st.caption("Real-time stream of debates from the ecosystem.")
    
    recent_debates = db.get_recent_debates(limit=10)
    
    if not recent_debates:
        st.info("No recorded debates found in the ecosystem. Start the first one!")
    else:
        for d in recent_debates:
            with st.container():
                # Safe extraction of fields
                t_topic = d.get('topic', 'Untitled Debate')
                t_winner = d.get('winner', 'TIE')
                t_reasoning = d.get('reasoning', 'No reasoning provided.')
                t_created = d.get('created_at', 'Long ago')[:19].replace('T', ' ')
                t_ma = d.get('model_a', 'AI-A')
                t_mb = d.get('model_b', 'AI-B')

                st.markdown(f"""
                    <div class="glass-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0;">{t_topic}</h4>
                            <span class="badge badge-primary">WINNER: {t_winner}</span>
                        </div>
                        <p style="color:#666; font-size:0.9rem; margin-top:8px;">
                            {t_reasoning[:200]}...
                        </p>
                        <small style="color:#444;">{t_created} | vs {t_ma} and {t_mb}</small>
                    </div>
                """, unsafe_allow_html=True)

# -----------------------------
# TAB 3: MODEL STATS
# -----------------------------
with tab_stats:
    st.markdown("### 📊 Ecosystem Intelligence")
    
    all_debates = db.get_recent_debates(limit=100)
    if all_debates:
        # Calculate Leaderboard
        wins = {"Model A": 0, "Model B": 0, "TIE": 0}
        for d in all_debates:
            w = d.get('winner', 'TIE')
            if w in wins: wins[w] += 1
            elif "Model A" in str(w): wins["Model A"] += 1
            elif "Model B" in str(w): wins["Model B"] += 1
            else: wins["TIE"] += 1
            
        c1, c2, c3 = st.columns(3)
        c1.metric(f"🔵 {MODEL_A_LABEL} Wins", wins["Model A"])
        c2.metric(f"🟠 {MODEL_B_LABEL} Wins", wins["Model B"])
        c3.metric("🤝 Ties", wins["TIE"])

    else:
        st.info("Stats will populate after the first 5 ecosystem battles.")

# ===== FOOTER =====
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: #444; padding: 2rem;">
        <p>© 2026 {BRAND_NAME} Intelligence | Version {VERSION} | Engineering by Soumyadarshan Dash</p>
        <p style="font-size:0.8rem">Zero-Cloud / Local-First / Startup-Grade</p>
    </div>
""", unsafe_allow_html=True)
