# 🔧 Ollama Setup & Troubleshooting Guide

## Understanding the Issue

The debate fails because the application cannot reach **Ollama** (the LLM backend) at `http://localhost:11434`.

### ✅ What's NOT Broken
- ✅ Code is working correctly
- ✅ API server is responding
- ✅ UI is loading
- ✅ Error handling is graceful

### ⚠️ What's Needed
- ⏳ Ollama service running
- ⏳ Required models downloaded
- ⏳ Correct network configuration

---

## Quick Fix (3 Steps)

### Step 1: Install Ollama
Download from: https://ollama.ai

### Step 2: Start Ollama Service
```bash
ollama serve
```

### Step 3: Pull Required Models
```bash
# In another terminal
ollama pull mistral
ollama pull llama3
ollama pull mixtral
```

**Then retry your debate!** ✅

---

## Setup Instructions by Deployment Type

### **Type 1: Local Development (Simplest)**

#### Install Ollama
```bash
# macOS: Download from https://ollama.ai and install

# Verify installation
ollama --version
```

#### Start Ollama
```bash
ollama serve
```
**Output**: `Listening on 127.0.0.1:11434`

#### Pull Models
```bash
ollama pull mistral      # Model A
ollama pull llama3       # Model B
ollama pull mixtral      # Heavy Judge (optional)
```

#### Verify Models
```bash
curl http://localhost:11434/api/tags
```

#### Run Your Debate App
```bash
cd "debate ai"
streamlit run trillm_arena/app.py
```

**Configuration**: No changes needed! ✅

---

### **Type 2: Docker - Ollama on Host**

#### Start Ollama on Host
```bash
ollama serve
```

#### Run Your App in Docker
```bash
cd "debate ai"
docker-compose up -d
```

#### Configure Network Access
**Problem**: Docker container can't reach `localhost:11434`

**Solution 1**: Use host network
```bash
docker run --network host myapp
```

**Solution 2**: Use special hostname
```bash
# In your .env or environment variable:
OLLAMA_URL=http://host.docker.internal:11434
```

**Solution 3**: Update docker-compose.yml
```yaml
services:
  api:
    environment:
      OLLAMA_URL: http://host.docker.internal:11434
```

---

### **Type 3: Docker - Ollama in Docker**

#### Run Ollama in Docker
```bash
docker run -d -p 11434:11434 ollama/ollama:latest
```

#### Pull Models in Container
```bash
docker exec <container_id> ollama pull mistral
docker exec <container_id> ollama pull llama3
```

#### Run Your App
```bash
cd "debate ai"
docker-compose up -d
```

#### Configure Networking
```yaml
# docker-compose.yml
version: '3.8'
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

  api:
    environment:
      OLLAMA_URL: http://ollama:11434  # Service name!
    depends_on:
      - ollama

volumes:
  ollama_data:
```

---

### **Type 4: Kubernetes/Production**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  OLLAMA_URL: http://ollama-service:11434

---
apiVersion: v1
kind: Service
metadata:
  name: ollama-service
spec:
  selector:
    app: ollama
  ports:
    - port: 11434
      targetPort: 11434
```

---

## Verification Checklist

### ✅ Is Ollama Running?
```bash
curl http://localhost:11434/api/tags
```
**Expected**: JSON with list of models

### ✅ Are Models Downloaded?
```bash
ollama list
```
**Expected**: Shows mistral, llama3, mixtral

### ✅ Can Your App Reach Ollama?
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Hello",
  "stream": false
}'
```
**Expected**: Model responds with text

### ✅ Full Debate Test
```bash
python test_api.py "Your debate topic"
```
**Expected**: Debate completes successfully

---

## Common Issues & Solutions

### ❌ Issue 1: "Connection refused" on localhost:11434

**Cause**: Ollama not running

**Solution**:
```bash
ollama serve
```

---

### ❌ Issue 2: Models not found

**Cause**: Models not downloaded

**Solution**:
```bash
ollama pull mistral
ollama pull llama3
```

---

### ❌ Issue 3: Docker can't reach Ollama on host

**Cause**: localhost resolves to container, not host

**Solutions**:
1. Use `http://host.docker.internal:11434` (macOS/Windows)
2. Use `http://172.17.0.1:11434` (Linux)
3. Use `--network host` flag
4. Run Ollama in Docker too

---

### ❌ Issue 4: Slow/Timeout errors

**Cause**: Ollama response too slow or timeout too short

**Solution 1**: Increase timeout
```bash
# In .env
LLM_TIMEOUT=300  # 5 minutes instead of default 120
```

**Solution 2**: Use faster model
```bash
# In config or code
DEBATE_MODELS = ["neural-chat", "orca-mini"]  # Faster than mistral
```

**Solution 3**: Check system resources
```bash
# Ensure GPU is available if using it
nvidia-smi

# Check CPU usage
top
```

---

## Configuration Options

### Environment Variables
```bash
# .env file
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL_A=mistral
OLLAMA_MODEL_B=llama3
OLLAMA_MODEL_JUDGE=mixtral
LLM_TIMEOUT=120
LLM_RETRY_ATTEMPTS=3
```

### Python Configuration
```python
# In trillm_arena/llm.py or config
OLLAMA_ENDPOINT = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODELS = {
    "model_a": os.getenv("OLLAMA_MODEL_A", "mistral"),
    "model_b": os.getenv("OLLAMA_MODEL_B", "llama3"),
    "judge": os.getenv("OLLAMA_MODEL_JUDGE", "mixtral"),
}
TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))
```

---

## Model Selection & Performance

### Fast Models (2-5 min debate)
```bash
ollama pull neural-chat    # Small, fast
ollama pull orca-mini      # Lightweight
ollama pull tinyllama      # Minimal resources
```

### Balanced Models (5-10 min debate)
```bash
ollama pull mistral        # Current setup (recommended)
ollama pull llama3         # Current setup (recommended)
```

### Advanced Models (10-20 min debate)
```bash
ollama pull mixtral        # Heavy judge, powerful
ollama pull neural-chat-v2 # More capable
```

---

## Complete Setup Script

```bash
#!/bin/bash

echo "🚀 Setting up TriLLM Arena with Ollama..."

# 1. Install Ollama (if not present)
if ! command -v ollama &> /dev/null; then
    echo "📥 Installing Ollama..."
    curl https://ollama.ai/install.sh | sh
fi

# 2. Start Ollama
echo "🔧 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!
sleep 3

# 3. Pull models
echo "📦 Pulling models (this takes time)..."
ollama pull mistral
ollama pull llama3
ollama pull mixtral

# 4. Verify
echo "✅ Verifying Ollama..."
curl -s http://localhost:11434/api/tags | grep -q "mistral"
if [ $? -eq 0 ]; then
    echo "✅ Ollama is ready with models!"
else
    echo "❌ Failed to set up models"
    exit 1
fi

# 5. Run app
echo "🚀 Starting TriLLM Arena..."
cd "debate ai"
streamlit run trillm_arena/app.py

# Cleanup
trap "kill $OLLAMA_PID" EXIT
```

---

## Docker Compose with Ollama

```yaml
version: '3.8'

services:
  # Ollama LLM Backend
  ollama:
    image: ollama/ollama:latest
    container_name: trillm-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_MODELS=/root/.ollama/models
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Server
  api:
    build:
      context: .
      target: api
    container_name: trillm-api
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_URL=http://ollama:11434
      - LOG_LEVEL=info
    depends_on:
      ollama:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Streamlit UI
  ui:
    build:
      context: .
      target: ui
    container_name: trillm-ui
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  ollama_data:

networks:
  default:
    name: trillm-network
```

---

## Monitoring & Debugging

### View Ollama Status
```bash
ps aux | grep ollama
```

### Check Ollama Logs
```bash
# Ollama logs (varies by OS)
# macOS: ~/Library/Logs/Ollama/Ollama.log
# Linux: ~/.ollama/logs
tail -f ~/.ollama/logs/ollama.log
```

### Test Model Response
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral",
    "prompt": "What is the capital of France?",
    "stream": false
  }'
```

### Monitor Docker Services
```bash
docker-compose ps
docker-compose logs -f
docker stats
```

---

## Summary

| Setup Type | Complexity | Latency | Best For |
|-----------|-----------|---------|----------|
| **Local** | Simple | Low | Development |
| **Docker (Host Ollama)** | Medium | Medium | Testing |
| **Docker (Both)** | Medium | Medium | Production |
| **Kubernetes** | Complex | Low | Enterprise |

---

## Next Steps

1. **Start Ollama**:
   ```bash
   ollama serve
   ```

2. **Pull Models** (in another terminal):
   ```bash
   ollama pull mistral && ollama pull llama3
   ```

3. **Verify Setup**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

4. **Run Your App**:
   ```bash
   streamlit run trillm_arena/app.py
   # OR
   docker-compose up -d
   ```

5. **Test Debate**:
   ```bash
   python test_api.py "Your debate topic"
   ```

---

**Status**: Complete Ollama setup guide
**Created**: February 8, 2026
**Updated**: Production ready

🚀 Follow this guide and your debate engine will work perfectly!
