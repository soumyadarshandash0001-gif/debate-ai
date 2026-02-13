#!/bin/bash

# ==============================================
# TriLLM Arena - PRE-DEPLOYMENT CHECKLIST
# ==============================================

echo ""
echo "╔═════════════════════════════════════════════════════════╗"
echo "║     TriLLM Arena - Pre-Deployment Verification         ║"
echo "║                                                         ║"
echo "║  Checking: Code ✓ Voice ✓ Models ✓ Git ✓ Deploy Files ║"
echo "╚═════════════════════════════════════════════════════════╝"
echo ""

PROJECT_DIR="/Users/soumyadarshandash/debate ai"
cd "$PROJECT_DIR"

PASS=0
FAIL=0

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅${NC} $1"
        ((PASS++))
    else
        echo -e "${RED}❌${NC} $1"
        ((FAIL++))
    fi
}

echo "📁 PROJECT STRUCTURE"
echo "─────────────────────────────────────────────────────────"

test -f "streamlit_app.py" && check "streamlit_app.py exists" || (echo -e "${RED}❌${NC} streamlit_app.py missing" && ((FAIL++)))
test -f "pyproject.toml" && check "pyproject.toml exists" || (echo -e "${RED}❌${NC} pyproject.toml missing" && ((FAIL++)))
test -f ".streamlit/config.toml" && check ".streamlit/config.toml exists" || (echo -e "${RED}❌${NC} .streamlit/config.toml missing" && ((FAIL++)))
test -d "trillm_arena" && check "trillm_arena/ directory exists" || (echo -e "${RED}❌${NC} trillm_arena/ missing" && ((FAIL++)))
test -f "trillm_arena/app_v2.py" && check "app_v2.py exists" || (echo -e "${RED}❌${NC} app_v2.py missing" && ((FAIL++)))

echo ""
echo "🔊 VOICE SYNTHESIS"
echo "─────────────────────────────────────────────────────────"

# Test voice
python3 -c "import sys; print('darwin' in sys.platform or 'linux' in sys.platform or 'win32' in sys.platform)" > /dev/null 2>&1 && check "Python platform detected" || ((FAIL++))

# Test macOS voice
if [[ "$OSTYPE" == "darwin"* ]]; then
    which say > /dev/null 2>&1 && check "macOS 'say' command available" || (echo -e "${RED}❌${NC} macOS 'say' not available" && ((FAIL++)))
fi

echo ""
echo "🤖 LLM MODELS"
echo "─────────────────────────────────────────────────────────"

# Check Ollama
curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && check "Ollama service running (port 11434)" || (echo -e "${RED}❌${NC} Ollama not responding" && ((FAIL++)))

# Check models
if curl -s http://localhost:11434/api/tags | grep -q "llama3.2"; then
    echo -e "${GREEN}✅${NC} llama3.2 model available"
    ((PASS++))
else
    echo -e "${RED}❌${NC} llama3.2 model not found"
    ((FAIL++))
fi

if curl -s http://localhost:11434/api/tags | grep -q "llama3.1.*8b"; then
    echo -e "${GREEN}✅${NC} llama3.1:8b model available"
    ((PASS++))
else
    echo -e "${RED}❌${NC} llama3.1:8b model not found"
    ((FAIL++))
fi

echo ""
echo "📦 DEPENDENCIES"
echo "─────────────────────────────────────────────────────────"

# Check Python packages
python3 -c "import streamlit" > /dev/null 2>&1 && check "streamlit installed" || (echo -e "${RED}❌${NC} streamlit not installed" && ((FAIL++)))
python3 -c "import fastapi" > /dev/null 2>&1 && check "fastapi installed" || (echo -e "${RED}❌${NC} fastapi not installed" && ((FAIL++)))
python3 -c "import pyttsx3" > /dev/null 2>&1 && check "pyttsx3 installed (optional)" || echo -e "${YELLOW}⚠️${NC} pyttsx3 not installed (Linux/Windows need this)"

echo ""
echo "🔧 GIT REPOSITORY"
echo "─────────────────────────────────────────────────────────"

test -d ".git" && check "Git repository initialized" || (echo -e "${RED}❌${NC} Git not initialized" && ((FAIL++)))

if [ -d ".git" ]; then
    git remote | grep -q origin && check "Git remote 'origin' configured" || echo -e "${YELLOW}⚠️${NC} Git remote not yet set (you'll configure this on GitHub)"
    git status > /dev/null 2>&1 && check "Git working directory clean or committable" || (echo -e "${RED}❌${NC} Git status error" && ((FAIL++)))
fi

echo ""
echo "📊 DEPLOYMENT FILES"
echo "─────────────────────────────────────────────────────────"

# Check content of key deployment files
grep -q "run_iterative_debate" "streamlit_app.py" > /dev/null 2>&1 && check "streamlit_app.py has correct content" || (echo -e "${RED}❌${NC} streamlit_app.py content issue" && ((FAIL++)))
grep -q "dependencies" "pyproject.toml" > /dev/null 2>&1 && check "pyproject.toml has dependencies" || (echo -e "${RED}❌${NC} pyproject.toml content issue" && ((FAIL++)))
grep -q "streamlit" ".streamlit/config.toml" > /dev/null 2>&1 && check ".streamlit/config.toml configured" || (echo -e "${RED}❌${NC} .streamlit/config.toml content issue" && ((FAIL++)))

echo ""
echo "📋 MISC CHECKS"
echo "─────────────────────────────────────────────────────────"

test -f ".gitignore" && check ".gitignore exists" || (echo -e "${RED}❌${NC} .gitignore missing" && ((FAIL++)))
test -f "QUICK_DEPLOY.md" && check "QUICK_DEPLOY.md exists (deployment guide)" || (echo -e "${RED}❌${NC} deployment guide missing" && ((FAIL++)))

echo ""
echo "╔═════════════════════════════════════════════════════════╗"
echo "║                    SUMMARY                              ║"
echo "╚═════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✅ Passed: $PASS${NC}"
echo -e "${RED}❌ Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED! Ready for deployment!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Create GitHub repo: https://github.com/new"
    echo "2. Add remote: git remote add origin <your-url>"
    echo "3. Push code: git push -u origin main"
    echo "4. Deploy: https://share.streamlit.io/ → New app"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  Some checks failed. Fix issues above before deploying.${NC}"
    echo ""
    exit 1
fi
