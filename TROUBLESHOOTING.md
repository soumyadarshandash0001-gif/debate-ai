# 🆘 Troubleshooting Guide

## The Core Issue Explained

When you try to run a debate and it fails with:
```
❌ Debate failed: Failed to call mistral after 3 attempts
```

This means your **application code is working perfectly**, but it cannot reach the **Ollama service**.

### Why This Happens

| Reason | Symptom | Fix |
|--------|---------|-----|
| Ollama not running | Connection refused | `ollama serve` |
| Models not downloaded | Model not found | `ollama pull mistral` |
| Wrong network config | Localhost resolution fails | Use `host.docker.internal` |
| Timeout too short | Request times out | Increase `LLM_TIMEOUT` |

---

## Diagnosis Flow

### Step 1: Check if Ollama is Running
```bash
curl http://localhost:11434/api/tags
```

**Expected**: JSON response with models list
**If fails**: Start Ollama with `ollama serve`

---

### Step 2: Check Models Downloaded
```bash
ollama list
```

**Expected**: Should show `mistral`, `llama3`, etc.
**If missing**: Run:
```bash
ollama pull mistral
ollama pull llama3
```

---

### Step 3: Test Model Response
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral",
    "prompt": "Hello!",
    "stream": false
  }'
```

**Expected**: Model responds with text
**If fails**: Check Ollama logs or system resources

---

### Step 4: Test Your App
```bash
python test_api.py "Test topic"
```

**Expected**: Debate runs and completes
**If fails**: Check specific error message below

---

## Error Messages & Fixes

### Error: "Connection refused"
```
HTTPConnectionPool(host='localhost', port=11434): 
Failed to establish a new connection: [Errno 61] Connection refused
```

**Cause**: Ollama service not running

**Fix**:
```bash
ollama serve
```

---

### Error: "Model not found"
```
Error: model 'mistral' not found
```

**Cause**: Models not downloaded

**Fix**:
```bash
ollama pull mistral
ollama pull llama3
ollama pull mixtral
```

---

### Error: "Timeout" or "Operation timed out"
```
HTTPException(status_code=504, detail="Request timeout")
```

**Cause 1**: Model taking too long to respond

**Fix 1**: Use faster model
```bash
ollama pull orca-mini  # Faster than mistral
```

**Fix 2**: Increase timeout
```bash
# In .env file
LLM_TIMEOUT=300  # 5 minutes
```

**Cause 2**: System resources exhausted

**Fix**: Close other apps, check:
```bash
top        # CPU usage
df -h      # Disk space
free -h    # Memory
```

---

### Error: "Docker can't reach localhost:11434"

**Cause**: `localhost` inside Docker container points to the container, not your host

**Fix Option 1** (macOS/Windows):
```bash
# In .env file or docker-compose
OLLAMA_URL=http://host.docker.internal:11434
```

**Fix Option 2** (Linux):
```bash
# In .env file
OLLAMA_URL=http://172.17.0.1:11434
```

**Fix Option 3** (All platforms):
Run Ollama in Docker too (see `OLLAMA_SETUP.md`)

---

### Error: "API server not running"
```
Cannot connect to http://localhost:8000
```

**Cause**: API server crashed or not started

**Fix**:
```bash
# Terminal 1: Start API
cd "debate ai"
python -m uvicorn trillm_arena.api:app --port 8000

# OR with Docker
docker-compose up -d
```

---

### Error: "UI not loading"
```
Cannot connect to http://localhost:8501
```

**Cause**: Streamlit not running

**Fix**:
```bash
streamlit run trillm_arena/app.py
```

---

## Complete Health Check Script

```bash
#!/bin/bash

echo "🔍 TriLLM Arena Health Check"
echo "================================"

# 1. Ollama Service
echo ""
echo "1️⃣  Checking Ollama Service..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "   ✅ Ollama is running"
else
    echo "   ❌ Ollama not running"
    echo "   Fix: ollama serve"
fi

# 2. Ollama Models
echo ""
echo "2️⃣  Checking Models..."
if curl -s http://localhost:11434/api/tags | grep -q "mistral"; then
    echo "   ✅ Models are available"
else
    echo "   ❌ Models not found"
    echo "   Fix: ollama pull mistral && ollama pull llama3"
fi

# 3. API Server
echo ""
echo "3️⃣  Checking API Server..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "   ✅ API server is running"
else
    echo "   ❌ API server not running"
    echo "   Fix: python -m uvicorn trillm_arena.api:app --port 8000"
fi

# 4. Streamlit UI
echo ""
echo "4️⃣  Checking Streamlit UI..."
if curl -s http://localhost:8501 > /dev/null; then
    echo "   ✅ Streamlit UI is running"
else
    echo "   ❌ Streamlit UI not running"
    echo "   Fix: streamlit run trillm_arena/app.py"
fi

# 5. System Resources
echo ""
echo "5️⃣  System Resources..."
echo "   CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')"
echo "   Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "   Disk: $(df -h / | awk '/\// {print $3 "/" $2}')"

echo ""
echo "================================"
echo "✅ Health check complete!"
```

Save as `health_check.sh` and run:
```bash
chmod +x health_check.sh
./health_check.sh
```

---

## Performance Tuning

### Slow Debates?

**Check 1**: Model size vs hardware
```bash
# Fast models (CPU friendly)
ollama pull orca-mini
ollama pull neural-chat

# Heavy models (need good hardware)
ollama pull mixtral
ollama pull mistral-large
```

**Check 2**: Increase resources
```bash
# For Docker
docker-compose down
# Edit docker-compose.yml: increase memory/cpu limits
docker-compose up -d
```

**Check 3**: Use GPU
```bash
docker-compose -f docker-compose.gpu.yml up -d
```

---

## Common Workflows

### Scenario 1: Fresh Installation
```bash
# 1. Install Ollama from https://ollama.ai

# 2. Start Ollama
ollama serve

# 3. Pull models (in new terminal)
ollama pull mistral
ollama pull llama3

# 4. Run app
cd "debate ai"
streamlit run trillm_arena/app.py

# 5. Visit http://localhost:8501
```

---

### Scenario 2: Using Docker
```bash
# 1. Make sure Ollama is running
ollama serve

# 2. Create .env file
cat > .env << EOF
OLLAMA_URL=http://host.docker.internal:11434
EOF

# 3. Start Docker
docker-compose up -d

# 4. Wait for health checks to pass
docker-compose ps

# 5. Visit http://localhost:8501
```

---

### Scenario 3: Restarting Everything
```bash
# 1. Stop services
docker-compose down

# 2. Restart Ollama
pkill ollama
sleep 2
ollama serve

# 3. Start app again
docker-compose up -d

# 4. Check health
curl http://localhost:8000/health
```

---

## Getting Help

### Gather Diagnostic Info
```bash
# Ollama status
ollama list
curl -s http://localhost:11434/api/tags | jq

# API logs
curl -v http://localhost:8000/health
docker-compose logs api

# System info
uname -a
docker --version
python --version
```

### Resources
- **Ollama Docs**: https://github.com/ollama/ollama
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Streamlit Docs**: https://docs.streamlit.io
- **Project Docs**: 
  - [OLLAMA_SETUP.md](OLLAMA_SETUP.md) - Detailed Ollama guide
  - [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment
  - [README.md](README.md) - Main documentation

---

## Summary

**Most Common Fix** (99% of cases):
```bash
# Terminal 1
ollama serve

# Terminal 2
ollama pull mistral && ollama pull llama3

# Terminal 3
cd "debate ai"
streamlit run trillm_arena/app.py

# Browser
http://localhost:8501
```

That's it! Debates will work. 🎉

---

**Created**: February 8, 2026
**Status**: Complete troubleshooting guide
