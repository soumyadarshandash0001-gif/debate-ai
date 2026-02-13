# 🚀 TriLLM Arena v2.0

> **Multi-LLM Debate Engine with Voice Synthesis & Iterative Reasoning**

[![Streamlit Cloud Deploy](https://img.shields.io/badge/Streamlit-Cloud%20Ready-FF6B6B?logo=streamlit)](https://share.streamlit.io/)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()

## ⚡ What is TriLLM Arena?

**TriLLM Arena** is an AI-powered debate platform where multiple Large Language Models (LLMs) debate topics in real-time, with voice synthesis for immersive experience.

- **🤖 Multi-LLM Debates**: LLaMA 3.2 vs LLaMA 3.1 (running on Ollama locally)
- **🗣️ Voice Synthesis**: Hear models debate with different voices
- **🔄 Iterative Rounds**: Models respond to each other round-by-round
- **⚖️ AI Judge**: LLaMA renders final verdict with scores
- **💫 Professional UI**: Gradient CSS, real-time feedback, download debates
- **🌍 Public Hosting**: Deploy to Streamlit Cloud for free, forever

## 🎯 Features

### Debate System
- ✅ Configurable debate topics
- ✅ Multi-round iterative debates (models respond to each other)
- ✅ Separate models for arguments and judging
- ✅ Real-time response streaming
- ✅ Complete debate transcript capture

### Voice & Audio
- ✅ macOS: Native `say` command (no external deps)
- ✅ Windows: pyttsx3 engine
- ✅ Linux: espeak TTS
- ✅ Different voice profiles for Model A vs Model B
- ✅ Synchronized playback with spinners

### UI/UX
- ✅ Professional gradient design
- ✅ Color-coded model responses
- ✅ Real-time debate progression
- ✅ Metrics & scoring display
- ✅ One-click debate download as .txt
- ✅ Mobile responsive

### Deployment
- ✅ Ready for Streamlit Cloud (FREE hosting)
- ✅ Docker support included
- ✅ Production-grade error handling
- ✅ Comprehensive logging

## 🚀 Quick Start (3 minutes)

### Local Development

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/trillm-arena.git
cd trillm-arena
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Ensure Ollama is running
# Models needed: llama3.2, llama3.1:8b

# Run the app
streamlit run trillm_arena/app_v2.py --server.port 8503
```

Visit: **http://localhost:8503**

### Deploy to Streamlit Cloud (FREE, FOREVER)

1. **Create GitHub Repo**
   - Go: https://github.com/new
   - Name: `trillm-arena`
   - Make it PUBLIC

2. **Push Code**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/trillm-arena.git
   git push -u origin main
   ```

3. **Deploy**
   - Go: https://share.streamlit.io/
   - New app → Select your repo
   - Main file: `streamlit_app.py`
   - Deploy!

4. **Share**
   - Streamlit gives you a public URL
   - Anyone can access it anytime

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│        Streamlit Frontend (v2)          │
│   (Voice UI + Gradient CSS)             │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴──────────┐
       ▼                  ▼
┌──────────────┐  ┌──────────────┐
│   FastAPI    │  │  Iterative   │
│   Backend    │  │   Debate     │
│  (8000)      │  │   Engine     │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                ▼
        ┌───────────────┐
        │ Ollama Server │
        │ Local Models  │
        │   (11434)     │
        └───────────────┘
```

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | Streamlit | 1.28.1 |
| **Backend** | FastAPI | 0.104.1 |
| **LLM Inference** | Ollama | Local |
| **Models** | LLaMA 3.2, LLaMA 3.1 8B | Latest |
| **Voice** | pyttsx3 + System TTS | Cross-platform |
| **Language** | Python | 3.9+ |
| **Hosting** | Streamlit Cloud | FREE |

## 📁 Project Structure

```
trillm-arena/
├── streamlit_app.py              # Streamlit Cloud entry point
├── pyproject.toml                # Python dependencies (Poetry)
├── requirements.txt              # Legacy dependencies
├── .streamlit/
│   └── config.toml               # Streamlit configuration
├── trillm_arena/
│   ├── app_v2.py                 # Main Streamlit app (with voice)
│   ├── app.py                    # Legacy version
│   ├── debate_engine_iterative.py # Core debate orchestration
│   ├── llm.py                    # Ollama interface
│   ├── prompts.py                # Debate prompts
│   ├── voice.py                  # Voice synthesis
│   ├── fact_bot.py               # Fact checking
│   └── monitor.py                # System monitoring
├── docker-compose.yml            # Docker setup
├── Dockerfile                    # Container image
├── QUICK_DEPLOY.md               # Deployment guide
├── STREAMLIT_CLOUD_DEPLOY.md     # Cloud setup guide
└── README.md                     # This file
```

## 🎓 How It Works

### Debate Flow

1. **User Input**: Enter debate topic
2. **Opening Round**: Both models present initial arguments
3. **Iterative Rounds** (3+ configurable):
   - Model A responds to Model B
   - Model B responds to Model A
   - Alternating turns
4. **Judge Evaluation**: Third model evaluates arguments
5. **Verdict**: Winner declared with scores
6. **Voice Playback** (Optional): Hear the entire debate

### Model Configuration

```python
# Models used
MODEL_A = "llama3.2"           # Main debater
MODEL_B = "llama3.1:8b"        # Opponent
JUDGE_MODEL = "llama3.1:8b"    # Verdict

# Debate settings
DEBATE_ROUNDS = 3              # Round count (1-5)
RESPONSE_TIMEOUT = 60          # Seconds per response
MAX_RETRIES = 3                # Retry attempts
```

## 🔊 Voice Features

### Cross-Platform Support

| OS | Method | Requires Setup |
|----|--------|---|
| **macOS** | Native `say` command | ✅ Built-in |
| **Windows** | pyttsx3 engine | ✅ Via pip |
| **Linux** | espeak TTS | ✅ apt-get install espeak |

### Usage

```python
from trillm_arena.voice import VoiceDebater

debater = VoiceDebater()
debater.play_debate_with_voices(debate_result)
```

## 📦 Installation

### Requirements
- Python 3.9+
- Ollama (local LLM server)
- 2GB RAM minimum
- macOS / Windows / Linux

### Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/trillm-arena.git
cd trillm-arena

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Alternative: Poetry
poetry install
```

### Start Ollama

```bash
# macOS (if using Homebrew)
brew services start ollama

# Or run directly
ollama serve

# Pull required models
ollama pull llama3.2
ollama pull llama3.1:8b
```

## 🚀 Running

### Local Development
```bash
streamlit run trillm_arena/app_v2.py --server.port 8503
```

### Docker
```bash
docker-compose up
```

### Production (Streamlit Cloud)
- Automatically deployed when you push to GitHub
- Public URL provided: `https://your-app.streamlit.app`
- Zero-configuration hosting

## 🧪 Testing

```bash
# Test voice synthesis
python3 -c "from trillm_arena.voice import speak_text; speak_text('Testing voice')"

# Test Ollama connection
curl http://localhost:11434/api/tags

# Test debate engine
python3 -c "from trillm_arena.debate_engine_iterative import run_iterative_debate; print(run_iterative_debate('AI should be regulated'))"
```

## 📝 Configuration

### Streamlit Settings (.streamlit/config.toml)
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#F0F2F6"
secondaryBackgroundColor = "#E8EAED"
textColor = "#262730"

[server]
port = 8503
maxUploadSize = 200
```

### Environment Variables
```bash
OLLAMA_HOST=http://localhost:11434
DEBUG=false
LOG_LEVEL=INFO
```

## 🌐 Deployment

### Streamlit Cloud (Recommended)
✅ **FREE** | ✅ **24/7** | ✅ **Public URL** | ✅ **Auto-Deploy**

See: [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

### Docker
See: [docker-compose.yml](docker-compose.yml)

### Self-Hosted
- Deploy anywhere with Python 3.9+
- Expose port 8503 (or configure)
- Backend needs Ollama access

## 📚 Documentation

- [QUICK_DEPLOY.md](QUICK_DEPLOY.md) - 5-minute deployment guide
- [STREAMLIT_CLOUD_DEPLOY.md](STREAMLIT_CLOUD_DEPLOY.md) - Detailed cloud setup
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed local setup

## 🐛 Troubleshooting

### Voice Not Working
```bash
# macOS: Test say command
say "Hello"

# Windows: Install pyttsx3
pip install pyttsx3

# Linux: Install espeak
sudo apt-get install espeak
```

### Models Not Responding
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
brew services restart ollama  # macOS

# Pull models if missing
ollama pull llama3.2
ollama pull llama3.1:8b
```

### Streamlit Cloud Deploy Issues
- Check `streamlit_app.py` exists in root
- Verify `pyproject.toml` has all dependencies
- Check `.streamlit/config.toml` is valid TOML
- View logs in Streamlit Cloud dashboard

## 💡 Tips & Tricks

### Customize Debate Topics
Edit `trillm_arena/prompts.py` for custom debate formats

### Change Models
```python
# In trillm_arena/debate_engine_iterative.py
MODEL_A = "your-model:tag"
MODEL_B = "another-model:tag"
```

### Adjust Debate Rounds
```python
DEBATE_ROUNDS = 5  # More rounds = longer debate
```

### Voice Configuration
```python
# In trillm_arena/app_v2.py
speak_text(text, rate=150)  # Adjust speaking speed
```

## 🔐 Security

### Local Development
- No authentication required
- Ollama server is local-only
- No data sent externally

### Streamlit Cloud
- Your code is private (GitHub repo)
- Frontend-only deployed (no backend secrets)
- Use `.streamlit/secrets.toml` for sensitive data (not pushed)

### Production
- Restrict Ollama to localhost or private network
- Use environment variables for configuration
- Implement rate limiting if public
- Monitor resource usage

## 📈 Performance

### Debate Generation Time
- **Fast** (~20s): Lower-end model, fewer rounds
- **Moderate** (~60s): Balanced configuration
- **Thorough** (~120s): Powerful models, many rounds

### System Requirements
- **Minimum**: 2GB RAM, 1GB free disk
- **Recommended**: 8GB RAM, 10GB free disk (for model caching)
- **Optimal**: 16GB RAM, 50GB disk (multiple models)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] More LLM models support
- [ ] Advanced debate strategies
- [ ] Real-time visualization
- [ ] Multi-language support
- [ ] API endpoints
- [ ] Mobile app

## 📄 License

MIT License - See [LICENSE](LICENSE)

## 🎯 Roadmap

- [ ] **v2.1**: More voice profiles
- [ ] **v2.2**: Custom debate formats
- [ ] **v2.3**: Browser-based TTS
- [ ] **v3.0**: Multi-participant debates (4+ models)
- [ ] **v3.1**: Debate tournaments
- [ ] **v4.0**: API for external integrations

## 📞 Support

**Questions?**
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [QUICK_DEPLOY.md](QUICK_DEPLOY.md)
- Open GitHub issue

**Want to Deploy?**
- Run: `bash deploy_to_streamlit.sh`
- Or follow: [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

## 🙏 Acknowledgments

- **Ollama**: Local LLM inference
- **Streamlit**: Interactive UI framework
- **LLaMA**: Meta's powerful language models
- **pyttsx3**: Cross-platform text-to-speech

---

**Status**: ✅ Production Ready | 🌍 Deploy to Public | 🎉 Free Forever

**Next Step**: [Deploy Now!](QUICK_DEPLOY.md)
