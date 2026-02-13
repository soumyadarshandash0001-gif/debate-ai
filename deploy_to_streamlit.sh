#!/bin/bash

# ==============================================
# TriLLM Arena - STREAMLIT CLOUD DEPLOYMENT
# ==============================================
# This script automates deployment to public Streamlit Cloud
# No more localhost! Your app will be public & free forever
# ==============================================

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  TriLLM Arena → Streamlit Cloud Deploy     ║"
echo "║  PUBLIC 🌍 FREE 💰 FOREVER ⏰            ║"
echo "╚════════════════════════════════════════════╝"
echo ""

PROJECT_DIR="/Users/soumyadarshandash/debate ai"
cd "$PROJECT_DIR"

# Step 1: Verify everything is ready
echo "📋 Step 1: Verifying setup..."
echo "✅ Checking files..."

if [ ! -f "streamlit_app.py" ]; then
    echo "❌ streamlit_app.py not found"
    exit 1
fi

if [ ! -f "pyproject.toml" ]; then
    echo "❌ pyproject.toml not found"
    exit 1
fi

if [ ! -f ".streamlit/config.toml" ]; then
    echo "❌ .streamlit/config.toml not found"
    exit 1
fi

echo "✅ All deployment files present!"
echo ""

# Step 2: Verify git repo
echo "📋 Step 2: Verifying Git repository..."
if [ ! -d ".git" ]; then
    echo "❌ Git not initialized"
    exit 1
fi

echo "✅ Git repository found"
echo ""

# Step 3: Commit changes
echo "📋 Step 3: Committing changes to Git..."
git add .
git commit -m "Deploy to Streamlit Cloud: v2.0 with voice & iterative debate" || true
echo "✅ Changes committed"
echo ""

# Step 4: Instructions
echo "╔════════════════════════════════════════════╗"
echo "║        NEXT STEPS (MANUAL)                 ║"
echo "╚════════════════════════════════════════════╝"
echo ""

echo "1️⃣  CREATE GITHUB REPOSITORY"
echo "   ├─ Go to: https://github.com/new"
echo "   ├─ Name: trillm-arena"
echo "   ├─ Description: Multi-LLM Debate Arena with Voice & Iterative Rounds"
echo "   ├─ Public: YES ✓"
echo "   └─ Click: Create repository"
echo ""

echo "2️⃣  PUSH TO GITHUB"
echo "   └─ Copy the GitHub SSH URL and run:"
echo ""
echo "   $ git remote add origin git@github.com:YOUR_USERNAME/trillm-arena.git"
echo "   $ git push -u origin main"
echo ""

echo "3️⃣  DEPLOY TO STREAMLIT CLOUD (1-2 MINUTES)"
echo "   ├─ Go to: https://share.streamlit.io/"
echo "   ├─ Click: New app"
echo "   ├─ Select: GitHub repository you just created"
echo "   ├─ Select: Branch = main"
echo "   ├─ Select: Main file = streamlit_app.py"
echo "   └─ Click: Deploy"
echo ""

echo "4️⃣  SHARE YOUR PUBLIC URL! 🎉"
echo "   └─ Streamlit gives you: https://your-app.streamlit.app"
echo "   └─ Anyone can access it!"
echo ""

echo "╔════════════════════════════════════════════╗"
echo "║        WHAT YOU GET                        ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "✅ Public URL (anyone can access)"
echo "✅ Free hosting (forever)"
echo "✅ Auto-deploy (git push = live)"
echo "✅ Voice debate (macOS/Windows/Linux)"
echo "✅ Iterative rounds (models respond to each other)"
echo "✅ Professional UI (gradient CSS)"
echo "✅ Zero configuration"
echo ""

echo "╔════════════════════════════════════════════╗"
echo "║        CURRENT STATUS                      ║"
echo "╚════════════════════════════════════════════╝"
echo ""

echo "📁 Project: $PROJECT_DIR"
echo "🔧 Main app: trillm_arena/app_v2.py"
echo "🚀 Deploy entry: streamlit_app.py"
echo "📦 Dependencies: pyproject.toml"
echo "⚙️  Config: .streamlit/config.toml"
echo ""

echo "Git remote:"
git remote -v || echo "Not yet configured"
echo ""

echo "Git status:"
git log --oneline -1
echo ""

echo "╔════════════════════════════════════════════╗"
echo "║     🎉 READY FOR PUBLIC DEPLOYMENT! 🎉     ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Questions? Check: STREAMLIT_CLOUD_DEPLOY.md"
echo ""
