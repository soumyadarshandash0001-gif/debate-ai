# 🚀 Zero-Cost Cloudless Deployment Guide

This guide ensures your **RATIO (TriLLM Arena)** is accessible globally for **$0/month** by combining free cloud services with your local hardware.

## 🏗️ The Hybrid Architecture
1. **Frontend**: [Streamlit Community Cloud](https://share.streamlit.io/) (Free Hosting)
2. **Task Queue**: [Supabase](https://supabase.com/) (Free Database)
3. **Inference Engine**: Your Local GPU (Ollama)
4. **Browser Inference**: [WebLLM](https://webllm.mlc-ai.org/) (Runs in user's browser via WebGPU)

---

## 🛠️ Step 1: Initialize Supabase (One-Time Setup)
1. Create a free account at [Supabase](https://supabase.com/).
2. Create a new project.
3. In the **SQL Editor**, run the following to create the required tables:

```sql
-- 1. Debates Table (Archive)
create table debates (
  id uuid primary key default uuid_generate_v4(),
  created_at timestamp with time zone default now(),
  topic text not null,
  model_a text,
  model_b text,
  rounds int,
  verdict text,
  winner text,
  reasoning text,
  scores jsonb,
  num_rounds int
);

-- 2. Debate Requests Table (Task Queue)
create table debate_requests (
  id uuid primary key default uuid_generate_v4(),
  created_at timestamp with time zone default now(),
  topic text not null,
  rounds int default 3,
  models text[],
  status text default 'pending', -- pending, processing, completed, failed
  result_id uuid references debates(id)
);

-- Enable public read if you want a public leaderboard
alter table debates enable row level security;
create policy "Public Read" on debates for select using (true);
create policy "Public Insert" on debates for insert with check (true);

alter table debate_requests enable row level security;
create policy "Anyone can create requests" on debate_requests for insert with check (true);
create policy "Anyone can check status" on debate_requests for select using (true);
create policy "Worker can update" on debate_requests for update using (true);
```

---

## 🛠️ Step 2: Deploy Frontend (Streamlit Cloud)
1. Push your code to GitHub:
   ```bash
   git push origin main
   ```
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub repository:
   - **Repository**: `soumyadarshandash0001-gif/debate-ai`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
4. Click **Advanced Settings** and add your **Secrets**:
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   IS_PRODUCTION = "true"
   # Optional: Add OPENROUTER_API_KEY if you want paid cloud fallback
   ```

---

## 🛠️ Step 3: Run the Local Worker (Your GPU)
This script connects your local machine to the cloud. When a user requests a debate on your website, this worker will run it locally and push the result back.

1. Ensure **Ollama** is running and models are pulled:
   ```bash
   ollama pull llama3.2  # Model A
   ollama pull llama3.1  # Judge
   ```
2. Set environment variables in your terminal:
   ```bash
   export SUPABASE_URL="your-supabase-url"
   export SUPABASE_KEY="your-supabase-key"
   ```
3. Start the worker:
   ```bash
   python trillm_arena/local_worker.py
   ```

---

## 🌐 How People Access It
- Give them your URL: `https://ratiotrillm.streamlit.app/`
- **Option A (Lightning Fast)**: They use the **⚡ Edge Node** tab. It runs models directly in their browser (No servers needed!).
- **Option B (High Quality)**: They use the **⚔️ Battle Arena**. Your local machine will process the request in the background.

## ✅ Verification Checklist
- [ ] Supabase Tables Created
- [ ] Streamlit Cloud Secrets configured
- [ ] `local_worker.py` running on your laptop/PC
- [ ] GitHub repository in sync
