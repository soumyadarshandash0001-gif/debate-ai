# Safari & Data Storage Fixes ✅

## Problems Fixed

### 1. **Safari Connection Issue** ✅
**Problem**: Safari couldn't connect to API (CORS error)
**Solution**: Added CORS middleware to FastAPI
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
**Status**: CORS headers now present - `Access-Control-Allow-Origin: *`

### 2. **Data Persistence Issue** ✅
**Problem**: Debate results weren't being stored
**Solution**: Added JSON file storage with persistent database
- Debates stored in: `~/.trillm_arena/debates.json`
- Each debate saved with timestamp
- New endpoints to retrieve/clear debates

**Code Added**:
```python
DATA_DIR = Path.home() / ".trillm_arena"
DEBATES_FILE = DATA_DIR / "debates.json"

def load_debates():
    if DEBATES_FILE.exists():
        return json.loads(DEBATES_FILE.read_text())
    return []

def save_debate(debate_result: dict):
    debates = load_debates()
    debates.append({
        "timestamp": datetime.now().isoformat(),
        **debate_result
    })
    DEBATES_FILE.write_text(json.dumps(debates, indent=2))
```

### 3. **Docker File Issue** ✅
**Problem**: Dockerfile referenced `app_updated.py` (doesn't exist)
**Solution**: Fixed to reference correct file `app.py`

## New API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/debate` | POST | Run debate (now saves results) |
| `/debates` | GET | Get all stored debates |
| `/debates` | DELETE | Clear all debates |

## Test Results

✅ API running: `http://localhost:8000`
✅ CORS headers present: `Access-Control-Allow-Origin: *`
✅ Data persistence working: `~/.trillm_arena/debates.json`
✅ New endpoints accessible

## Required Setup

To use the application with Safari:

1. **Start Ollama** (in separate terminal):
   ```bash
   ollama serve
   ```

2. **Pull Models**:
   ```bash
   ollama pull mistral
   ollama pull llama2
   ```

3. **Access from Safari**:
   - **Web UI**: `http://localhost:8501`
   - **API Docs**: `http://localhost:8000/docs`
   - **API Direct**: POST to `http://localhost:8000/debate`

## How to Test

### From Safari Web UI:
1. Go to `http://localhost:8501`
2. Enter debate topic
3. Click "Start Debate"
4. Results are automatically saved

### From API (curl or Safari fetch):
```bash
curl -X POST http://localhost:8000/debate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Your topic here", "deep_review": false}'
```

### Check Stored Debates:
```bash
curl http://localhost:8000/debates
```

Output:
```json
{
  "debates": [
    {
      "timestamp": "2026-02-08T12:34:56.789123",
      "topic": "...",
      "model_a": {...},
      "model_b": {...},
      "fast_verdict": "..."
    }
  ],
  "count": 1
}
```

## Files Modified

- ✅ `trillm_arena/api.py` - Added CORS + data persistence
- ✅ `Dockerfile` - Fixed app.py reference

## Next Steps

1. Start Ollama service: `ollama serve`
2. Pull models: `ollama pull mistral llama2`
3. Open Safari: `http://localhost:8501`
4. Run debates - they will now be stored!
5. View all debates: `curl http://localhost:8000/debates`
