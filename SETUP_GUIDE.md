# 🎯 TriLLM Arena - Complete Setup Guide

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Author**: Soumyadarshan Dash

---

## 📋 Complete Checklist

- [ ] Install Python 3.9+
- [ ] Install Ollama
- [ ] Clone/navigate to project
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Start Ollama service
- [ ] Pull LLM models
- [ ] Start API server
- [ ] Start Streamlit UI
- [ ] Access in browser
- [ ] Test a debate
- [ ] View monitoring dashboard
- [ ] (Optional) Set up public access with ngrok

---

## 🔧 Step-by-Step Installation

### Step 1: Prerequisites

#### Install Python (if needed)
```bash
# Check if installed
python3 --version

# If Python 3.9+ not installed:
# macOS (via Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt-get install python3.11 python3.11-venv

# Windows
# Download from https://www.python.org/downloads/
```

#### Install Ollama
Download from: https://ollama.ai

```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Windows
# Download installer from https://ollama.ai

# Verify installation
ollama --version
```

### Step 2: Project Setup

```bash
# Navigate to project directory
cd "debate ai"

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate

# Windows:
# .venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
# Check Python
python --version

# Check installed packages
pip list

# Should see:
# - fastapi
# - streamlit
# - pydantic
# - uvicorn
# - requests
# - psutil
# - plotly
```

---

## 🚀 Starting Services

### Option A: Manual Start (Recommended for Development)

**Terminal 1 - Start Ollama:**
```bash
ollama serve

# Keep this running. In another terminal:
# ollama pull mistral
# ollama pull llama2
```

**Terminal 2 - Start API Server:**
```bash
cd "debate ai"
source .venv/bin/activate
python -m uvicorn trillm_arena.api:app --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 3 - Start Streamlit UI:**
```bash
cd "debate ai"
source .venv/bin/activate
streamlit run trillm_arena/app.py --server.port 8501

# You should see:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

### Option B: One-Command Start (With Public Access)

```bash
cd "debate ai"
./start_production.sh

# This will:
# 1. Check/start API server
# 2. Check/start Streamlit UI
# 3. (Optional) Create ngrok tunnels for public access
```

---

## 🌐 Accessing the Application

### Local Access (Development)

Open your browser to these URLs:

1. **Web Interface** - http://localhost:8501
   - Debate input form
   - Real-time results
   - Debate history

2. **API Documentation** - http://localhost:8000/docs
   - Interactive Swagger UI
   - Test endpoints directly
   - View request/response schemas

3. **Alternative API Docs** - http://localhost:8000/redoc
   - ReDoc format (cleaner layout)

4. **Monitoring Dashboard** - http://localhost:8501?page=monitor
   - System health
   - Model status
   - Performance metrics
   - Debate statistics

### Public Access (with ngrok)

After running `./start_production.sh`:

```
🌍 PUBLIC LINKS (Share these):

🌐 Web UI: https://xxxx-xx-xxx-xxx-xx.ngrok.io
📡 API Server: https://xxxx-xx-xxx-xxx-xx.ngrok.io
📖 API Docs: https://xxxx-xx-xxx-xxx-xx.ngrok.io/docs
```

---

## 🧪 First-Time Testing

### Test 1: Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

### Test 2: Monitor System
```bash
curl http://localhost:8000/monitor/health | python3 -m json.tool
# Shows system metrics, Ollama status, etc.
```

### Test 3: Via Web UI (Easiest)
1. Go to http://localhost:8501
2. Enter debate topic: "Is Python better than JavaScript?"
3. Click "Start Debate"
4. Wait for results (usually 30-60 seconds)
5. View results and verdict

### Test 4: Via API
```bash
curl -X POST http://localhost:8000/debate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Is AI beneficial for society?",
    "deep_review": false
  }' | python3 -m json.tool
```

### Test 5: View Stored Debates
```bash
curl http://localhost:8000/debates | python3 -m json.tool
```

---

## 🔍 Troubleshooting

### Problem: "Connection refused on port 8000"

**Solution:**
```bash
# Check if API is running
lsof -i :8000

# If not, start it
cd "debate ai"
source .venv/bin/activate
python -m uvicorn trillm_arena.api:app --host 0.0.0.0 --port 8000
```

### Problem: "Ollama not running" error

**Solution:**
```bash
# Start Ollama
ollama serve

# In another terminal, check status
curl http://localhost:11434/api/tags

# Pull models if needed
ollama pull mistral
ollama pull llama2
```

### Problem: "No models available"

**Solution:**
```bash
# List current models
ollama list

# Pull required models
ollama pull mistral    # Recommended: 4.1GB
ollama pull llama2     # Optional: 3.8GB
ollama pull neural-chat # Optional: lightweight

# Takes 2-5 minutes per model
```

### Problem: "Port already in use"

**Solution:**
```bash
# Find what's using port
lsof -i :8501

# Kill the process
kill -9 <PID>

# Or use different port
streamlit run trillm_arena/app.py --server.port 8502
```

### Problem: High memory/CPU usage

**Solution:**
1. Stop other applications
2. Use smaller models:
   ```bash
   ollama pull mistral:7b-q4  # Quantized version
   ```
3. Reduce model context size:
   ```bash
   export OLLAMA_NUM_CTX=2048
   ```
4. Limit concurrent requests (in API)

### Problem: "ModuleNotFoundError"

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

---

## 📊 Monitoring Guide

### Real-Time Dashboard
- Access: http://localhost:8501?page=monitor
- Shows:
  - ✅ System status (CPU, Memory, Disk)
  - 🤖 Ollama models loaded
  - 📈 Debate activity (7-day chart)
  - 💾 Debate statistics

### Command-Line Monitoring

```bash
# System Health
watch -n 5 'curl -s http://localhost:8000/monitor/health | python3 -m json.tool'

# Models Status
curl http://localhost:8000/monitor/models | python3 -m json.tool

# System Metrics
curl http://localhost:8000/monitor/system | python3 -m json.tool

# Debate Stats
curl http://localhost:8000/monitor/debates | python3 -m json.tool
```

### Process Monitoring
```bash
# Check running services
ps aux | grep -E "uvicorn|streamlit|ollama"

# View API logs
tail -f /tmp/api.log

# View Streamlit logs
tail -f /tmp/streamlit.log
```

---

## 🌍 Public Deployment (Optional)

### Option 1: ngrok (Easiest - 10 minutes)
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Run production launcher
./start_production.sh

# ngrok links displayed in terminal
# Share these URLs with anyone
```

### Option 2: Docker (Isolated - 15 minutes)
```bash
# Start with Docker Compose
docker-compose up

# With GPU support
docker-compose -f docker-compose.gpu.yml up
```

### Option 3: Cloud (AWS/GCP/Heroku - 30+ minutes)
See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for detailed guides.

---

## 📖 Key Endpoints Reference

### Health & Status
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Quick health check |
| `/monitor/health` | GET | Complete health report |
| `/monitor/models` | GET | Model list & status |
| `/monitor/system` | GET | CPU, memory, disk |
| `/monitor/debates` | GET | Debate statistics |

### Debate Operations
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/debate` | POST | Start new debate |
| `/debates` | GET | List all debates |
| `/debates` | DELETE | Clear all debates |

### Documentation
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc format |
| `/openapi.json` | GET | OpenAPI schema |

---

## 📁 Project Structure

```
debate ai/
├── trillm_arena/
│   ├── app.py              # Streamlit web UI
│   ├── monitor.py          # Monitoring dashboard
│   ├── api.py              # FastAPI server
│   ├── debate_engine.py    # Debate orchestration
│   ├── llm.py              # LLM integration
│   └── prompts.py          # Debate prompts
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container image
├── docker-compose.yml      # Docker orchestration
├── start_production.sh     # Production launcher
├── README.md               # Main documentation
├── PRODUCTION_DEPLOYMENT.md # Deployment guide
└── LICENSE                 # MIT License
```

---

## 🚀 Quick Commands Reference

```bash
# Activate environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start API (port 8000)
python -m uvicorn trillm_arena.api:app --host 0.0.0.0 --port 8000

# Start UI (port 8501)
streamlit run trillm_arena/app.py --server.port 8501

# Start monitoring
curl http://localhost:8000/monitor/health

# Start Ollama
ollama serve

# Pull models
ollama pull mistral llama2

# Test debate endpoint
curl -X POST http://localhost:8000/debate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test topic"}'
```

---

## ✅ Verification Checklist

After setup, verify everything works:

```bash
# ✅ Python environment
python --version          # Should be 3.9+
python -c "import streamlit; print('Streamlit OK')"
python -c "import fastapi; print('FastAPI OK')"

# ✅ Services running
curl http://localhost:8000/health
curl http://localhost:8501 2>/dev/null | head -1

# ✅ Ollama
curl http://localhost:11434/api/tags

# ✅ Models
ollama list

# ✅ API endpoints
curl http://localhost:8000/docs 2>/dev/null | grep -c "swagger"

# ✅ UI accessible
open http://localhost:8501
```

---

## 📞 Support

- **Issues**: https://github.com/soumyadarshandash/trillm-arena/issues
- **Documentation**: See README.md and PRODUCTION_DEPLOYMENT.md
- **Ollama Help**: https://ollama.ai
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Streamlit Docs**: https://docs.streamlit.io

---

## 🎓 Next Steps

1. **Customize Prompts** - Edit `trillm_arena/prompts.py`
2. **Add More Models** - `ollama pull <model-name>`
3. **Customize UI** - Modify `trillm_arena/app.py`
4. **Deploy Publicly** - Use ngrok or Docker
5. **Contribute** - GitHub: soumyadarshandash/trillm-arena

---

**Happy Debating! 🚀**

*Last Updated: 8 February 2026*  
*TriLLM Arena v1.0.0*
