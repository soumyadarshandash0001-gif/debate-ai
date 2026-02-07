#!/bin/bash

# TriLLM Arena - Production Launcher with Public Access
# This script starts all services and creates public tunnels

set -e

COLOR_GREEN='\033[0;32m'
COLOR_BLUE='\033[0;34m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${COLOR_BLUE}===============================================${NC}"
echo -e "${COLOR_BLUE}🚀 TriLLM Arena - Production Launcher${NC}"
echo -e "${COLOR_BLUE}===============================================${NC}"
echo ""

# Check if running
if lsof -i :8000 > /dev/null 2>&1; then
    echo -e "${COLOR_YELLOW}⚠️  API server already running on port 8000${NC}"
else
    echo -e "${COLOR_GREEN}✅ Starting API server...${NC}"
    cd "$(dirname "$0")"
    .venv/bin/python -m uvicorn trillm_arena.api:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
    API_PID=$!
    sleep 2
    echo -e "${COLOR_GREEN}✅ API running (PID: $API_PID)${NC}"
fi

if lsof -i :8501 > /dev/null 2>&1; then
    echo -e "${COLOR_YELLOW}⚠️  Streamlit UI already running on port 8501${NC}"
else
    echo -e "${COLOR_GREEN}✅ Starting Streamlit UI...${NC}"
    cd "$(dirname "$0")"
    .venv/bin/streamlit run trillm_arena/app.py --server.port 8501 --server.headless true > /tmp/streamlit.log 2>&1 &
    STREAMLIT_PID=$!
    sleep 2
    echo -e "${COLOR_GREEN}✅ Streamlit running (PID: $STREAMLIT_PID)${NC}"
fi

echo ""
echo -e "${COLOR_BLUE}===============================================${NC}"
echo -e "${COLOR_GREEN}✅ LOCAL ACCESS (Recommended for Development):${NC}"
echo -e "${COLOR_BLUE}===============================================${NC}"
echo ""
echo -e "${COLOR_GREEN}🌐 Web UI:${NC}           http://localhost:8501"
echo -e "${COLOR_GREEN}📡 API Server:${NC}       http://localhost:8000"
echo -e "${COLOR_GREEN}📖 API Docs:${NC}         http://localhost:8000/docs"
echo -e "${COLOR_GREEN}📊 Monitoring:${NC}       http://localhost:8501?page=monitor"
echo ""

# Check if ngrok is installed and try to create tunnels
if command -v ngrok &> /dev/null; then
    echo -e "${COLOR_BLUE}===============================================${NC}"
    echo -e "${COLOR_YELLOW}🌍 PUBLIC ACCESS (via ngrok):${NC}"
    echo -e "${COLOR_BLUE}===============================================${NC}"
    echo ""
    
    # Kill any existing ngrok processes
    pkill -f ngrok 2>/dev/null || true
    sleep 1
    
    echo -e "${COLOR_YELLOW}Starting ngrok tunnels...${NC}"
    
    # Start ngrok tunnels
    ngrok http 8501 --log=stdout > /tmp/ngrok_ui.log 2>&1 &
    sleep 3
    ngrok http 8000 --log=stdout > /tmp/ngrok_api.log 2>&1 &
    sleep 3
    
    # Extract ngrok URLs
    UI_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"https://[^"]*"' | head -1 | tr -d '"')
    API_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"https://[^"]*"' | tail -1 | tr -d '"')
    
    if [ -n "$UI_URL" ]; then
        echo ""
        echo -e "${COLOR_GREEN}✅ PUBLIC LINKS (Share these):${NC}"
        echo ""
        echo -e "${COLOR_GREEN}🌐 Web UI:${NC}           ${COLOR_BLUE}${UI_URL}${NC}"
        echo -e "${COLOR_GREEN}📡 API Server:${NC}       ${COLOR_BLUE}${API_URL}${NC}"
        echo -e "${COLOR_GREEN}📖 API Docs:${NC}         ${COLOR_BLUE}${API_URL}/docs${NC}"
        echo ""
        
        # Save URLs to file
        cat > /tmp/trillm_arena_urls.txt << EOF
TriLLM Arena - Public Access Links
Generated: $(date)

LOCAL ACCESS:
- Web UI: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

PUBLIC ACCESS (ngrok):
- Web UI: ${UI_URL}
- API: ${API_URL}
- API Docs: ${API_URL}/docs

Note: ngrok links expire after 2 hours of inactivity.
For permanent public access, use Docker or cloud deployment.
EOF
        
        echo -e "${COLOR_YELLOW}📝 URLs saved to /tmp/trillm_arena_urls.txt${NC}"
    else
        echo -e "${COLOR_RED}❌ Failed to get ngrok URLs${NC}"
    fi
else
    echo ""
    echo -e "${COLOR_YELLOW}💡 For PUBLIC access, install ngrok:${NC}"
    echo ""
    echo "   macOS:  brew install ngrok"
    echo "   Other:  https://ngrok.com/download"
    echo ""
    echo -e "${COLOR_YELLOW}Then run: ${COLOR_GREEN}npm install -g ngrok${NC}"
    echo ""
fi

echo ""
echo -e "${COLOR_BLUE}===============================================${NC}"
echo -e "${COLOR_GREEN}✅ REQUIREMENTS:${NC}"
echo -e "${COLOR_BLUE}===============================================${NC}"
echo ""
echo -e "1. ${COLOR_YELLOW}Ollama Service${NC}"
echo "   Start in terminal: ${COLOR_GREEN}ollama serve${NC}"
echo ""
echo -e "2. ${COLOR_YELLOW}Models${NC}"
echo "   Download: ${COLOR_GREEN}ollama pull mistral llama2${NC}"
echo ""
echo -e "3. ${COLOR_YELLOW}Check Status${NC}"
echo "   Monitor: ${COLOR_GREEN}http://localhost:8501?page=monitor${NC}"
echo ""

echo -e "${COLOR_BLUE}===============================================${NC}"
echo -e "${COLOR_GREEN}✅ ALL SERVICES RUNNING!${NC}"
echo -e "${COLOR_BLUE}===============================================${NC}"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep running
wait
