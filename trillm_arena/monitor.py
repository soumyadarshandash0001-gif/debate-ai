import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Page config
st.set_page_config(
    page_title="TriLLM Arena Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
        }
        .status-healthy {
            color: #10b981;
            font-weight: bold;
        }
        .status-degraded {
            color: #f59e0b;
            font-weight: bold;
        }
        .status-error {
            color: #ef4444;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# API Base URL
API_URL = "http://localhost:8000"

def fetch_health():
    try:
        resp = requests.get(f"{API_URL}/monitor/health", timeout=5)
        return resp.json()
    except:
        return None

def fetch_models():
    try:
        resp = requests.get(f"{API_URL}/monitor/models", timeout=5)
        return resp.json()
    except:
        return None

def fetch_system():
    try:
        resp = requests.get(f"{API_URL}/monitor/system", timeout=5)
        return resp.json()
    except:
        return None

def fetch_debates():
    try:
        resp = requests.get(f"{API_URL}/monitor/debates", timeout=5)
        return resp.json()
    except:
        return None

# Title
st.title("🔬 TriLLM Arena - System Monitor")
st.markdown("**Real-time monitoring dashboard for the debate engine**")
st.divider()

# Refresh button
if st.button("🔄 Refresh Now", use_container_width=True):
    st.rerun()

# Auto-refresh every 30 seconds
st.write("""
<script>
setTimeout(function(){
    window.location.reload();
}, 30000);
</script>
""", unsafe_allow_html=True)

# Fetch all data
health = fetch_health()
models = fetch_models()
system = fetch_system()
debates = fetch_debates()

# Health Status
if health:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_class = "status-healthy" if health["status"] == "healthy" else "status-degraded"
        st.metric("System Status", health["status"].upper(), delta=None)
    
    with col2:
        st.metric("Ollama Running", "✅ Yes" if health["ollama"]["running"] else "❌ No")
    
    with col3:
        st.metric("Models Loaded", health["ollama"]["models_loaded"])
    
    st.divider()

# Main monitoring tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🤖 Models", "💻 System", "📈 Debates"])

# === TAB 1: Dashboard ===
with tab1:
    if health:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "API Status",
                "✅ Active",
                f"v{health['api']['version']}"
            )
        
        with col2:
            st.metric(
                "Total Debates",
                health.get("debates_total", 0)
            )
        
        with col3:
            cpu = system["cpu_percent"] if system else 0
            st.metric(
                "CPU Usage",
                f"{cpu:.1f}%",
                delta=f"{'⚠️ High' if cpu > 80 else '✅ Good'}"
            )
        
        with col4:
            mem = system["memory_percent"] if system else 0
            st.metric(
                "Memory Usage",
                f"{mem:.1f}%",
                delta=f"{'⚠️ High' if mem > 80 else '✅ Good'}"
            )
        
        st.divider()
        
        # Status Summary
        st.subheader("System Health Summary")
        
        health_cols = st.columns(3)
        with health_cols[0]:
            st.write("**Ollama Service**")
            if health["ollama"]["running"]:
                st.success("Running")
                st.write(f"Models: {', '.join(health['ollama']['models'])}")
            else:
                st.error("Not Running")
        
        with health_cols[1]:
            st.write("**CPU & Memory**")
            if system:
                if system["cpu_percent"] < 80 and system["memory_percent"] < 80:
                    st.success("Healthy")
                else:
                    st.warning("High Usage")
                st.write(f"CPU: {system['cpu_percent']:.1f}%")
                st.write(f"Memory: {system['memory_percent']:.1f}%")
        
        with health_cols[2]:
            st.write("**Last Updated**")
            st.info(datetime.now().strftime("%H:%M:%S"))
    else:
        st.error("❌ Cannot connect to API server. Ensure it's running on port 8000.")

# === TAB 2: Models ===
with tab2:
    if models:
        st.subheader("Ollama Models")
        
        if models["ollama_running"]:
            st.success(f"✅ Ollama Running - {models['models_count']} models loaded")
            
            if models["models"]:
                df_models = pd.DataFrame(models["models"])
                st.dataframe(df_models, use_container_width=True)
            else:
                st.warning("⚠️ No models loaded. Pull models with: `ollama pull llama3.2`")
        else:
            st.error("❌ Ollama is not running. Start with: `ollama serve`")
            
            # Instructions
            with st.expander("📖 How to start Ollama", expanded=True):
                st.code("""
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Pull models
ollama pull llama3.2
ollama pull qwen3-vl:4b
ollama pull llama3.1:8b
""")
    else:
        st.error("Cannot fetch model information")

# === TAB 3: System ===
with tab3:
    if system:
        st.subheader("System Resources")
        
        metrics_cols = st.columns(3)
        
        with metrics_cols[0]:
            st.metric(
                "CPU Usage",
                f"{system['cpu_percent']:.1f}%",
                delta="Active"
            )
        
        with metrics_cols[1]:
            st.metric(
                "Memory Usage",
                f"{system['memory_percent']:.1f}%",
                delta=f"{system['memory_gb']:.1f}GB / {system['memory_total_gb']:.1f}GB"
            )
        
        with metrics_cols[2]:
            st.metric(
                "Disk Usage",
                f"{system['disk_percent']:.1f}%",
                delta="Available"
            )
        
        st.divider()
        
        # Resource gauge
        st.subheader("Resource Utilization")
        
        fig = go.Figure(data=[
            go.Bar(
                name='Usage %',
                x=['CPU', 'Memory', 'Disk'],
                y=[system['cpu_percent'], system['memory_percent'], system['disk_percent']],
                marker=dict(
                    color=['#10b981' if x < 70 else '#f59e0b' if x < 85 else '#ef4444' 
                           for x in [system['cpu_percent'], system['memory_percent'], system['disk_percent']]],
                    line=dict(color='rgba(0,0,0,0.1)', width=2)
                )
            )
        ])
        
        fig.update_layout(
            yaxis_range=[0, 100],
            hovermode='x unified',
            height=400,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Cannot fetch system metrics")

# === TAB 4: Debates ===
with tab4:
    if debates:
        st.subheader("Debate Statistics")
        
        stats_cols = st.columns(4)
        
        with stats_cols[0]:
            st.metric("Total Debates", debates["total"])
        
        with stats_cols[1]:
            st.metric("Last 7 Days", debates["last_7_days"])
        
        with stats_cols[2]:
            st.metric("Last 24 Hours", debates["last_24_hours"])
        
        with stats_cols[3]:
            st.metric("Today", debates["today"])
        
        st.divider()
        
        # Activity chart
        if debates["total"] > 0:
            st.subheader("Activity Timeline")
            st.info(f"📊 {debates['total']} debates recorded")
            
            try:
                resp = requests.get(f"{API_URL}/debates")
                all_debates = resp.json().get("debates", [])
                
                if all_debates:
                    # Create timeline
                    debate_dates = []
                    for debate in all_debates:
                        try:
                            ts = datetime.fromisoformat(debate["timestamp"])
                            debate_dates.append(ts.date())
                        except:
                            pass
                    
                    if debate_dates:
                        date_counts = pd.Series(debate_dates).value_counts().sort_index()
                        
                        fig_timeline = go.Figure(data=[
                            go.Scatter(
                                x=date_counts.index,
                                y=date_counts.values,
                                mode='lines+markers',
                                name='Debates',
                                line=dict(color='#667eea', width=3),
                                marker=dict(size=8)
                            )
                        ])
                        
                        fig_timeline.update_layout(
                            title="Debates Over Time",
                            xaxis_title="Date",
                            yaxis_title="Number of Debates",
                            hovermode='x unified',
                            height=400,
                        )
                        st.plotly_chart(fig_timeline, use_container_width=True)
            except:
                pass
        else:
            st.info("No debates recorded yet. Start a debate to see activity!")
    else:
        st.error("Cannot fetch debate statistics")

# Footer
st.divider()
st.markdown("""
---
**TriLLM Arena v1.0.0** | Created by Soumyadarshan Dash | [GitHub](https://github.com/soumyadarshandash/trillm-arena) | [API Docs](http://localhost:8000/docs)

**Quick Links:**
- 🌐 [Web UI](http://localhost:8501) - Start debates
- 📡 [API Server](http://localhost:8000) - REST endpoints
- 📖 [API Documentation](http://localhost:8000/docs) - Interactive API docs
- 📊 [Monitoring](http://localhost:8501/?page=monitor) - This page
""")
