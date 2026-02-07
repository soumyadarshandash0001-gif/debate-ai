import streamlit as st
import json
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MLOps Tracking
AUTHOR = "Soumyadarshan Dash"
VERSION = "1.0.0"
SESSION_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from trillm_arena.debate_engine import run_debate_fast, DebateError
except ImportError:
    from debate_engine import run_debate_fast, DebateError

# ===== Page Configuration =====
st.set_page_config(
    page_title="TriLLM Arena",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for production UI
st.markdown("""
    <style>
        .main {
            padding-top: 2rem;
        }
        .stTitle {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        .debate-card {
            border-left: 4px solid #1f77b4;
            padding: 1.5rem;
            background-color: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        .verdict-card {
            border: 2px solid #2ecc71;
            padding: 1.5rem;
            background-color: #f0fdf4;
            border-radius: 8px;
            margin-top: 1.5rem;
        }
        .model-label {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #1f77b4;
        }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ TriLLM Arena")
st.markdown("Production-grade Multi-LLM Debate Engine")

# Display version and author info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Version", VERSION)
with col2:
    st.metric("Status", "🟢 Active")
with col3:
    st.caption(f"By {AUTHOR}")

# ===== Sidebar Configuration =====
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Author and Project Info
    st.divider()
    st.markdown("### 👤 Project Info")
    st.markdown(f"""
    **Created by**: {AUTHOR}  
    **Version**: {VERSION}  
    **Status**: Production Ready ✅  
    **License**: MIT  
    
    [GitHub](https://github.com/soumyadarshandash/trillm-arena) • 
    [Docs](https://github.com/soumyadarshandash/trillm-arena/blob/main/README.md)
    """)
    st.divider()
    
    deep_review = st.checkbox(
        "Deep Review (Enable Heavy Judge)",
        value=False,
        help="Trigger advanced judgment for close debates"
    )
    st.divider()
    st.markdown("### About")
    st.markdown("""
    TriLLM Arena runs structured AI debates between:
    - **Model A**: Mistral
    - **Model B**: LLaMA-3
    
    Each debate includes:
    1. Opening arguments
    2. Rebuttals
    3. Defenses
    4. Verdict from judges
    """)

# ===== Main UI =====
topic = st.text_input(
    "Enter Debate Topic",
    placeholder="e.g., Should AI regulation be government-led or industry-led?",
    help="A topic for the AI models to debate"
)

col1, col2 = st.columns([3, 1])
with col2:
    start_button = st.button(
        "🚀 Start Debate",
        use_container_width=True,
        type="primary"
    )

if start_button and topic:
    if len(topic.strip()) < 5:
        st.error("❌ Please enter a topic with at least 5 characters.")
    else:
        try:
            with st.spinner("🔄 Running optimized debate..."):
                logger.info(f"[MLOps] Debate started | Topic: {topic} | Author: {AUTHOR} | Session: {SESSION_ID}")
                result = run_debate_fast(topic, deep_review=deep_review)
                
                # MLOps tracking - log debate metrics
                if result:
                    logger.info(f"[MLOps] Debate completed | Topic: {topic[:50]}... | Duration: {result.get('meta', {}).get('duration_seconds', 'N/A')}s | Author: {AUTHOR}")
                    st.success("✅ Debate completed successfully!")
                else:
                    logger.warning(f"[MLOps] Debate returned empty result | Topic: {topic}")


            # ===== Debate Results =====
            st.subheader("📋 Debate Transcripts")
            
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown(
                    '<div class="debate-card"><div class="model-label">Model A — Mistral</div>',
                    unsafe_allow_html=True
                )
                st.markdown("**📝 Opening Argument**")
                st.markdown(result["model_a"]["opening"])
                st.markdown("**⚔️ Rebuttal**")
                st.markdown(result["model_a"]["rebuttal"])
                st.markdown("**🛡️ Defense**")
                st.markdown(result["model_a"]["defense"])
                st.markdown("</div>", unsafe_allow_html=True)

            with col_b:
                st.markdown(
                    '<div class="debate-card"><div class="model-label">Model B — LLaMA-3</div>',
                    unsafe_allow_html=True
                )
                st.markdown("**📝 Opening Argument**")
                st.markdown(result["model_b"]["opening"])
                st.markdown("**⚔️ Rebuttal**")
                st.markdown(result["model_b"]["rebuttal"])
                st.markdown("**🛡️ Defense**")
                st.markdown(result["model_b"]["defense"])
                st.markdown("</div>", unsafe_allow_html=True)

            # ===== Verdicts =====
            st.subheader("⚖️ Judge Verdicts")
            
            col_fast, col_heavy = st.columns(2)
            
            with col_fast:
                st.markdown("### Fast Judge")
                try:
                    fast_json = json.loads(result["fast_verdict"])
                    st.json(fast_json)
                except json.JSONDecodeError as e:
                    st.warning(f"Could not parse fast verdict: {str(e)}")
                    st.text(result["fast_verdict"])
            
            if result["heavy_verdict"]:
                with col_heavy:
                    st.markdown("### Heavy Judge")
                    try:
                        heavy_json = json.loads(result["heavy_verdict"])
                        st.json(heavy_json)
                    except json.JSONDecodeError as e:
                        st.warning(f"Could not parse heavy verdict: {str(e)}")
                        st.text(result["heavy_verdict"])
            
            # Metadata
            if result.get("meta"):
                with st.expander("📊 Metadata"):
                    st.json(result["meta"])
            
            st.success("✅ Debate completed successfully!")
            logger.info(f"Debate completed for topic: {topic}")
            
        except DebateError as e:
            logger.error(f"Debate error: {str(e)}")
            st.error(f"❌ Debate error: {str(e)}")
            st.info("Please ensure Ollama is running with Mistral and LLaMA-3 models.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            st.error(f"❌ Unexpected error: {str(e)}")
elif start_button:
    st.warning("⚠️ Please enter a debate topic first.")

# ===== Footer =====
st.divider()
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption(f"🔬 **TriLLM Arena v{VERSION}**")
with footer_col2:
    st.caption(f"👤 **By {AUTHOR}**")
with footer_col3:
    st.caption("📄 **MIT License**")

st.caption(
    "Built with ⚡ FastAPI & Streamlit | "
    "[GitHub](https://github.com/soumyadarshandash/trillm-arena) | "
    "[Documentation](https://github.com/soumyadarshandash/trillm-arena/blob/main/README.md)"
)
