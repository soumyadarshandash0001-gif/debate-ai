# 🚀 TriLLM Arena - Production Deployment Guide

**Version**: 1.0.0  
**Author**: Soumyadarshan Dash  
**License**: MIT  

## Quick Start (2 minutes)

### Prerequisites
- Python 3.9+ with venv
- Ollama installed (https://ollama.ai)
- Terminal access

### 1. Setup Environment
```bash
# Clone/navigate to project
cd "debate ai"

# Create virtual environment (if not exists)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Ollama Service (Terminal 1)
```bash
ollama serve

# In another terminal, pull models:
ollama pull mistral
ollama pull llama2
```

### 3. Launch Application
```bash
# Option A: Development (local only)
# Terminal 2: Start API
cd "debate ai"
.venv/bin/python -m uvicorn trillm_arena.api:app --host 0.0.0.0 --port 8000

# Terminal 3: Start UI
.venv/bin/streamlit run trillm_arena/app.py --server.port 8501

# Option B: Production (with public access)
./start_production.sh  # Requires ngrok for public URLs
```

### 4. Access Application

**Local (Recommended):**
- 🌐 **Web UI**: http://localhost:8501
- 📡 **API**: http://localhost:8000
- 📖 **API Docs**: http://localhost:8000/docs
- 📊 **Monitor**: http://localhost:8501?page=monitor

**Public (via ngrok):**
- Links shown in terminal after running `./start_production.sh`

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│         TriLLM Arena System                     │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ Streamlit Web UI (Port 8501)            │  │
│  │ - Debate interface                      │  │
│  │ - Results display                       │  │
│  │ - Real-time monitoring                  │  │
│  └────────────┬─────────────────────────────┘  │
│               │                                 │
│               ▼                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ FastAPI Server (Port 8000)               │  │
│  │ - /debate (POST) - Run debate            │  │
│  │ - /debates (GET) - List debates          │  │
│  │ - /monitor/* - System monitoring         │  │
│  │ - /docs - API documentation             │  │
│  └────────────┬─────────────────────────────┘  │
│               │                                 │
│      ┌────────┴────────┐                       │
│      ▼                 ▼                       │
│  ┌─────────────┐  ┌──────────────────────┐   │
│  │ Debate      │  │ Ollama Service       │   │
│  │ Engine      │  │ (Port 11434)         │   │
│  │ - Orchestr  │  │ - Mistral model      │   │
│  │ - Judging   │  │ - LLaMA2/3 models    │   │
│  │ - Retry     │  │ - Model inference    │   │
│  └─────────────┘  └──────────────────────┘   │
│      │                                         │
│      ▼                                         │
│  ┌─────────────────────────────────────────┐  │
│  │ Data Storage (~/.trillm_arena/)        │  │
│  │ - debates.json - All debate results    │  │
│  └─────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## API Endpoints

### Health & Status
- `GET /health` - Simple health check
- `GET /monitor/health` - Detailed health with metrics
- `GET /monitor/models` - List loaded models
- `GET /monitor/system` - System resource metrics
- `GET /monitor/debates` - Debate statistics

### Debate Operations
- `POST /debate` - Start new debate
  ```json
  {
    "topic": "Is Python better than JavaScript?",
    "deep_review": false
  }
  ```
- `GET /debates` - Get all debates
- `DELETE /debates` - Clear all debates

### Documentation
- `GET /docs` - Swagger UI (interactive)
- `GET /redoc` - ReDoc (alternative UI)
- `GET /openapi.json` - OpenAPI schema

---

## Configuration

### Environment Variables
Create `.env` file in project root:
```bash
# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_TIMEOUT=120

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Streamlit Configuration
STREAMLIT_PORT=8501

# Debate Configuration
DEBATE_TIMEOUT=300
RETRY_ATTEMPTS=3
RETRY_DELAY=5
```

### Streamlit Configuration
`~/.streamlit/config.toml`:
```toml
[server]
port = 8501
headless = true
runOnSave = true

[logger]
level = "info"

[client]
showErrorDetails = true
```

---

## System Monitoring

### Real-time Dashboard
Access at: **http://localhost:8501?page=monitor**

Displays:
- ✅ System status
- 🤖 Ollama service status
- 💻 CPU, Memory, Disk usage
- 📊 Debate activity timeline
- 📈 Statistics (last 7 days, 24 hours, today)

### API Monitoring Endpoints
```bash
# Overall health
curl http://localhost:8000/monitor/health | jq

# Models status
curl http://localhost:8000/monitor/models | jq

# System metrics
curl http://localhost:8000/monitor/system | jq

# Debate stats
curl http://localhost:8000/monitor/debates | jq
```

---

## Troubleshooting

### Issue: API returns "Ollama not running"
**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama
ollama serve

# Pull models
ollama pull mistral
ollama pull llama2
```

### Issue: Safari/cross-origin errors
**Solution:** CORS is enabled in API. Clear browser cache and try again.

### Issue: Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Issue: Out of memory
```bash
# Check system memory
free -h

# Stop other services
pkill streamlit
pkill ollama

# Reduce debate complexity (disable deep_review)
```

---

## Deployment Options

### Option 1: Local Development (Recommended for testing)
```bash
# Terminal 1
ollama serve

# Terminal 2
cd "debate ai" && source .venv/bin/activate
python -m uvicorn trillm_arena.api:app --host 0.0.0.0 --port 8000

# Terminal 3
streamlit run trillm_arena/app.py --server.port 8501
```

### Option 2: Production with ngrok (Public access)
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Run production launcher
./start_production.sh

# Public links displayed in terminal
```

### Option 3: Docker (Isolated environment)
```bash
# Build image
docker-compose build

# Run with GPU support
docker-compose -f docker-compose.gpu.yml up

# Or standard
docker-compose up
```

### Option 4: Cloud Deployment

#### AWS EC2
```bash
# Launch Ubuntu 22.04 instance
# SSH into instance
ssh -i key.pem ubuntu@<instance-ip>

# Install dependencies
sudo apt update
sudo apt install -y python3.11 python3-pip curl

# Clone repo, install, run start_production.sh
```

#### Heroku
```bash
heroku create trillm-arena
git push heroku main
heroku config:set OLLAMA_URL=<external-ollama-url>
```

#### Google Cloud Run
```bash
gcloud run deploy trillm-arena --source .
```

---

## Performance Tuning

### Optimize Ollama
```bash
# Use quantized models (faster, less memory)
ollama pull mistral:7b-q4  # Instead of full model

# Set context size
export OLLAMA_NUM_CTX=2048  # Default: 4096

# Set concurrency
export OLLAMA_NUM_PARALLEL=2
```

### Streamlit Optimization
```toml
# In ~/.streamlit/config.toml
[client]
toolbarMode = "minimal"

[logger]
level = "warning"  # Reduce logging

[server]
runOnSave = false  # Disable auto-reload in production
```

### API Performance
- Enable caching for repeated debates
- Use connection pooling
- Implement rate limiting
- Monitor endpoint response times

---

## Security Best Practices

1. **Authentication** (if exposing publicly)
   ```bash
   pip install python-jose python-multipart
   # Add API key validation to endpoints
   ```

2. **Rate Limiting**
   ```bash
   pip install slowapi
   # Add rate limit decorator to endpoints
   ```

3. **HTTPS** (for public deployment)
   ```bash
   # Use ngrok (auto HTTPS)
   # Or deploy behind reverse proxy with SSL
   ```

4. **Environment Variables**
   - Use `.env` file (never commit)
   - Rotate secrets regularly
   - Use AWS Secrets Manager for production

5. **Input Validation**
   - Sanitize debate topics
   - Validate request payloads (already using Pydantic)
   - Implement CSRF protection

---

## Data Persistence

### Storage Location
- **Local**: `~/.trillm_arena/debates.json`
- **Docker**: `/app/data/debates.json`

### Backup
```bash
# Backup debates
cp ~/.trillm_arena/debates.json ~/.trillm_arena/debates.backup.json

# Restore
cp ~/.trillm_arena/debates.backup.json ~/.trillm_arena/debates.json
```

### Database Migration (Future)
For production, consider:
- PostgreSQL with SQLAlchemy ORM
- MongoDB for flexible schema
- AWS DynamoDB for serverless

---

## Monitoring & Logging

### View Logs
```bash
# API logs
tail -f /tmp/api.log

# Streamlit logs
tail -f /tmp/streamlit.log

# System logs
ps aux | grep -E "uvicorn|streamlit"
```

### Metrics Collection
```bash
# Check disk usage
du -sh ~/.trillm_arena/

# Monitor active processes
top -p $(pgrep -f "uvicorn|streamlit" | tr '\n' ',')
```

---

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/xyz`
3. Make changes
4. Test locally
5. Commit: `git commit -m "Add feature xyz"`
6. Push: `git push origin feature/xyz`
7. Create Pull Request

---

## Support & Resources

- **GitHub Issues**: https://github.com/soumyadarshandash/trillm-arena/issues
- **Documentation**: [README.md](README.md)
- **Ollama Docs**: https://ollama.ai
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Streamlit Docs**: https://docs.streamlit.io

---

## License

MIT License - See [LICENSE](LICENSE) file

---

**Last Updated**: 8 February 2026  
**Created by**: Soumyadarshan Dash  
**Status**: Production Ready ✅
