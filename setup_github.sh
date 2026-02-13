#!/bin/bash

# TriLLM Arena - GitHub Setup Script
# This script prepares your project for GitHub deployment

echo "🚀 TriLLM Arena GitHub Setup"
echo "============================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first:"
    echo "   brew install git"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Get current directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Check if git repo already exists
if [ -d ".git" ]; then
    echo "✅ Git repository already initialized"
    echo ""
    echo "📊 Current Git Status:"
    git status
    echo ""
    echo "Current Remote:"
    git remote -v
    echo ""
else
    echo "📝 Initializing new Git repository..."
    git init
    git add .
    git commit -m "Initial commit: TriLLM Arena v2.0 with voice and iterative debate"
    git branch -M main
    echo "✅ Git repository initialized!"
    echo ""
fi

echo ""
echo "============================"
echo "📋 NEXT STEPS:"
echo "============================"
echo ""
echo "1. Go to: https://github.com/new"
echo "2. Create repository: 'trillm-arena'"
echo "3. Copy the SSH or HTTPS URL"
echo ""
echo "4. Run this command (replace YOUR_URL):"
echo "   git remote add origin YOUR_URL"
echo "   git push -u origin main"
echo ""
echo "5. Go to: https://share.streamlit.io/"
echo "6. Click 'New app'"
echo "7. Select your repository and deploy!"
echo ""
echo "✅ Your app will be live in 1-2 minutes!"
echo ""
