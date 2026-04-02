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

# MLOps Tracking
AUTHOR = "Soumyadarshan Dash"
VERSION = "2.0.0"
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
    page_title="TriLLM Arena v2",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== PROFESSIONAL CSS =====
st.markdown("""
    <style>
    /* Color Palette */
    :root {
        --primary: #0066cc;
        --secondary: #ff6b35;
        --success: #00b894;
        --warning: #ffa502;
        --danger: #ee5a6f;
        --dark: #2f3542;
        --light: #f5f6fa;
    }
    
    /* Main Layout */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
    }
    
    /* Header Styling */
    .header-container {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .header-container h1 {
        font-size: 3rem;
        margin: 0;
        font-weight: 900;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .header-container p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.95;
    }
    
    /* Input Section */
    .input-section {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
    }
    
    /* Metric Cards */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        flex: 1;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .metric-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        opacity: 0.95;
    }
    
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    /* Round Container */
    .round-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #667eea;
    }
    
    .round-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .round-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2f3542;
    }
    
    .round-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Model Response Cards */
    .model-response {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    
    .model-a {
        border-left-color: #0066cc;
    }
    
    .model-b {
        border-left-color: #ff6b35;
    }
    
    .model-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .model-label {
        font-size: 1rem;
        font-weight: 700;
        margin-right: 1rem;
    }
    
    .model-label.a {
        color: #0066cc;
    }
    
    .model-label.b {
        color: #ff6b35;
    }
    
    .model-badge {
        background: #e3f2fd;
        color: #0066cc;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .model-badge.b {
        background: #fff3e0;
        color: #ff6b35;
    }
    
    .model-text {
        font-size: 1rem;
        line-height: 1.6;
        color: #2f3542;
    }
    
    /* Verdict Section */
    .verdict-section {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-top: 2rem;
        box-shadow: 0 8px 25px rgba(17, 153, 142, 0.3);
    }
    
    .verdict-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .verdict-content {
        background: rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }
    
    .winner-announce {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .verdict-reasoning {
        font-size: 1rem;
        line-height: 1.7;
        opacity: 0.95;
    }
    
    /* Loading State */
    .loading-spinner {
        text-align: center;
        padding: 2rem;
    }
    
    /* Error State */
    .error-box {
        background: #ffe3e3;
        color: #c92a2a;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #c92a2a;
        margin: 1rem 0;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Sidebar */
    .sidebar .stRadio > label {
        font-weight: 600;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header-container h1 {
            font-size: 2rem;
        }
        
        .metric-row {
            flex-direction: column;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown("""
    <div class="header-container">
        <h1>⚡ TriLLM Arena v2.0</h1>
        <p>Iterative Multi-LLM Debate Engine</p>
    </div>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.title("⚙️ Configuration")
    
    rounds = st.slider(
        "Debate Rounds",
        min_value=1,
        max_value=5,
        value=3,
        help="Number of iterative exchanges between models"
    )
    
    st.divider()
    
    # Metrics Section
    col1 = st.columns(1)
    with col1[0]:
        st.metric("Author", "Soumyadarshan Dash")
    
    st.divider()
    
    # About Project Button
    if st.button("ℹ️ About Project", use_container_width=True):
        with st.expander("📖 Project Information", expanded=True):
            st.markdown("""
            ### TriLLM Arena v2.0
            **Production-Grade Multi-LLM Debate Engine**
            
            **About:**
            A sophisticated debate platform that orchestrates structured arguments 
            between multiple AI models with iterative exchanges, intelligent judging, 
            and professional web interface.
            
            **Features:**
            - 🔄 Iterative debate rounds
            - ⚖️ Expert judge evaluation
            - 🎙️ Voice output for conclusions
            - 📊 Real-time scoring
            - 🎨 Professional UI
            
            **Author:** Soumyadarshan Dash  
            **License:** MIT  
            **Status:** Production Ready ✅
            
            **GitHub:** [TriLLM Arena](https://github.com/soumyadarshandash/trillm-arena)
            """)
    
    st.divider()
    
    # Cloud Status
    st.sidebar.markdown("### ☁️ Cloud Status")
    import os
    if os.getenv("OPENROUTER_API_KEY") and "your_openrouter" not in os.getenv("OPENROUTER_API_KEY"):
        st.sidebar.success("✅ OpenRouter API Active")
    else:
        st.sidebar.warning("⚠️ OpenRouter Key Missing")

    if os.getenv("SUPABASE_URL") and "your_supabase" not in os.getenv("SUPABASE_URL"):
        st.sidebar.success("✅ Supabase Integrated")
    else:
        st.sidebar.warning("⚠️ Supabase Credentials Missing")

    st.divider()
    
    st.markdown("### Active Models")
    st.markdown(f"🔵 **Model A**: {MODEL_A_LABEL}")
    st.markdown(f"🟠 **Model B**: {MODEL_B_LABEL}")
    st.markdown(f"⚖️ **Judge**: {JUDGE_LABEL}")

# ===== MAIN CONTENT =====
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### Enter Your Debate Topic")
    topic = st.text_input(
        "What would you like to debate?",
        placeholder="e.g., Should AI regulation be government-led?",
        label_visibility="collapsed"
    )

with col2:
    start_debate = st.button("🚀 Start Debate", use_container_width=True)

# ===== DEBATE EXECUTION =====
if start_debate:
    if not topic or len(topic.strip()) < 3:
        st.error("❌ Please enter a valid topic (at least 3 characters)")
    else:
        try:
            st.markdown("---")
            
            # Progress container
            progress_placeholder = st.empty()
            rounds_container = st.container()
            
            with progress_placeholder.container():
                st.info("🔄 Starting iterative debate... This may take a minute.")
            
            # Run debate
            logger.info(f"Starting debate: {topic}")
            result = run_iterative_debate(
                topic,
                num_rounds=rounds,
                model_a_id=MODEL_A_ID,
                model_b_id=MODEL_B_ID,
                judge_id=JUDGE_ID,
            )
            
            # Save to Supabase (if configured)
            db.save_debate(result)
            
            progress_placeholder.empty()
            
            # ===== DISPLAY ROUNDS =====
            st.markdown("---")
            st.markdown("## 📊 Debate Progression")
            
            for round_data in result.get("rounds", []):
                round_num = round_data["round"]
                is_opening = round_data["type"] == "opening"
                
                st.markdown(f"""
                    <div class="round-container">
                        <div class="round-header">
                            <div class="round-title">
                                {'🎭 Opening Statements' if is_opening else f'Round {round_num}'}
                            </div>
                            <div class="round-badge">
                                {'OPENING' if is_opening else f'ROUND {round_num}'}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown(f"""
                        <div class="model-response model-a">
                            <div class="model-header">
                                <span class="model-label a">🔵 Model A</span>
                                <span class="model-badge">{MODEL_A_LABEL}</span>
                            </div>
                            <div class="model-text">
                    """, unsafe_allow_html=True)
                    st.write(round_data["model_a"])
                    st.markdown("</div></div>", unsafe_allow_html=True)
                
                with col_b:
                    st.markdown(f"""
                        <div class="model-response model-b">
                            <div class="model-header">
                                <span class="model-label b">🟠 Model B</span>
                                <span class="model-badge b">{MODEL_B_LABEL}</span>
                            </div>
                            <div class="model-text">
                    """, unsafe_allow_html=True)
                    st.write(round_data["model_b"])
                    st.markdown("</div></div>", unsafe_allow_html=True)
            
            # ===== DISPLAY VERDICT =====
            st.markdown("---")
            
            try:
                verdict = json.loads(result.get("verdict", "{}"))
                winner = verdict.get("winner", "TIE")
                reasoning = verdict.get("reasoning", "")
                scores = verdict.get("scores", {})
                
                # ===== WINNER DEBATE CONCLUSION =====
                st.markdown("## 🏆 Winner Debate Conclusion")
                
                rounds_data = result.get("rounds", [])
                winner_key = "model_a" if winner == "Model A" else "model_b"
                
                # Get winner's final response
                if rounds_data:
                    winner_final_response = rounds_data[-1].get(winner_key, "")
                    
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%); 
                                    padding: 2rem; border-radius: 12px; margin-bottom: 2rem;
                                    box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);">
                            <h3 style="color: #333; margin-top: 0;">🎯 {winner}'s Conclusion</h3>
                            <div style="background: white; padding: 1.5rem; border-radius: 8px;
                                       line-height: 1.8; color: #2f3542;">
                                {winner_final_response}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # ===== JUDGE VERDICT SECTION =====
                st.markdown("## ⚖️ Final Judgment")
                
                st.markdown(f"""
                    <div class="verdict-section">
                        <div class="verdict-title">⚖️ Judge's Decision</div>
                        <div class="verdict-content">
                            <div class="winner-announce">
                                🏆 Winner: <strong>{winner}</strong>
                            </div>
                            <div class="verdict-reasoning">
                                {reasoning}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Scores
                st.markdown("### 📈 Debate Scores")
                score_col_a, score_col_b = st.columns(2)
                
                with score_col_a:
                    score_a = scores.get("Model A", 5.0)
                    st.metric("🔵 Model A Score", f"{score_a}/10", delta=None)
                
                with score_col_b:
                    score_b = scores.get("Model B", 5.0)
                    st.metric("🟠 Model B Score", f"{score_b}/10", delta=None)
                
                # ===== VOICE DEBATE PLAYBACK ⭐ NEW =====
                st.markdown("---")
                st.markdown("## 🎙️ Voice Debate Playback")
                
                voice_col1, voice_col2, voice_col3 = st.columns([2, 1, 1])
                
                with voice_col1:
                    st.write("**🔊 Hear the debate with voices! (macOS/Linux/Windows)**")
                    if sys.platform == "darwin":
                        st.info("ℹ️ Using macOS built-in voice (say command)")
                    elif sys.platform == "win32":
                        st.info("ℹ️ Using Windows voice synthesis")
                    else:
                        st.info("ℹ️ Using Linux voice synthesis (espeak)")
                
                with voice_col2:
                    if st.button("🔊 Play Debate", use_container_width=True):
                        st.write("🔄 Playing debate with voices...")
                        
                        # Play opening round
                        if rounds_data and len(rounds_data) > 0:
                            opening = rounds_data[0]
                            
                            # Model A opening
                            with st.spinner("🔵 Model A speaking..."):
                                st.write(opening.get("model_a", "")[:100] + "...")
                                speak_text(opening.get("model_a", "")[:500], "A")
                                import time
                                time.sleep(2)
                            
                            # Model B opening
                            with st.spinner("🟠 Model B speaking..."):
                                st.write(opening.get("model_b", "")[:100] + "...")
                                speak_text(opening.get("model_b", "")[:500], "B")
                                time.sleep(2)
                        
                        # Play remaining rounds
                        for i in range(1, len(rounds_data)):
                            round_data = rounds_data[i]
                            
                            # Model A response
                            with st.spinner(f"🔵 Model A Round {i}..."):
                                st.write(round_data.get("model_a", "")[:100] + "...")
                                speak_text(round_data.get("model_a", "")[:500], "A")
                                time.sleep(2)
                            
                            # Model B response
                            with st.spinner(f"🟠 Model B Round {i}..."):
                                st.write(round_data.get("model_b", "")[:100] + "...")
                                speak_text(round_data.get("model_b", "")[:500], "B")
                                time.sleep(2)
                        
                        # Final verdict with voice
                        with st.spinner("⚖️ Judge speaking..."):
                            verdict_text = f"The winner is {winner}. {reasoning}"
                            st.write(verdict_text)
                            speak_text(verdict_text, "A")
                        
                        st.success("✅ Debate playback complete!")
                
                with voice_col3:
                    st.info("▶️ Click to play")
                
                # Note about voice
                st.caption("💡 Voices play in background. Turn up system volume!")
                
                # ===== DEBATE SUMMARY =====
                st.markdown("---")
                st.markdown("## 📋 Complete Debate Summary")
                
                summary_text = f"""
                **Topic:** {result['topic']}
                
                **Debate Format:** Iterative ({result['num_rounds']} rounds) with Voice Synthesis
                
                **Models:**
                - Model A (🔵): {MODEL_A_LABEL} (Voice: System Default 1)
                - Model B (🟠): {MODEL_B_LABEL} (Voice: System Default 2)
                - Judge (⚖️): {JUDGE_LABEL}
                
                **Results:**
                - **Winner:** {winner}
                - **Model A Score:** {scores.get("Model A", 5.0)}/10
                - **Model B Score:** {scores.get("Model B", 5.0)}/10
                - **Judge's Reasoning:** {reasoning}
                
                **Conclusion:**
                {winner} won the debate based on logical consistency, factual accuracy, 
                depth of reasoning, clarity of arguments, and minimal risk of hallucination.
                
                **Voice Technology:** pyttsx3 (Open-source Text-to-Speech)
                """
                
                with st.expander("📖 View Full Summary", expanded=False):
                    st.markdown(summary_text)
                    
                    # Download summary
                    st.download_button(
                        label="📥 Download Summary",
                        data=summary_text,
                        file_name=f"debate_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            except json.JSONDecodeError:
                st.markdown(f"""
                    <div class="verdict-section">
                        <div class="verdict-title">⚖️ Judge's Review</div>
                        <div class="verdict-reasoning">
                            {result.get("verdict", "Judgment unavailable")}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # ===== METADATA =====
            st.markdown("---")
            st.markdown("### 📋 Debate Metadata")
            
            meta_col1, meta_col2, meta_col3 = st.columns(3)
            
            with meta_col1:
                st.markdown(f"**Topic**: {result['topic']}")
            
            with meta_col2:
                st.markdown(f"**Rounds**: {result['num_rounds']}")
            
            with meta_col3:
                st.markdown(f"**Mode**: {result['meta']['mode'].title()}")
            
            logger.info(f"Debate completed successfully. Session: {SESSION_ID}")
        
        except DebateError as e:
            st.markdown(f"""
                <div class="error-box">
                    <strong>❌ Debate Error</strong><br>
                    {str(e)}
                </div>
            """, unsafe_allow_html=True)
            logger.error(f"Debate error: {str(e)}")
        
        except Exception as e:
            st.markdown(f"""
                <div class="error-box">
                    <strong>❌ Unexpected Error</strong><br>
                    {str(e)}
                </div>
            """, unsafe_allow_html=True)
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)

# ===== FOOTER =====
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>TriLLM Arena v{VERSION} | Built by {AUTHOR} | 
        <a href="https://github.com/soumyadarshandash/trillm-arena" style="color: #667eea; text-decoration: none;">GitHub</a> | 
        Session: {SESSION_ID}</p>
    </div>
""", unsafe_allow_html=True)
