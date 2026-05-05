<p align="center">
  <img src="https://img.shields.io/badge/Chrono--Topic--RAG-Conversation%20Intelligence-blueviolet?style=for-the-badge&logo=openai&logoColor=white" alt="Chrono-Topic-RAG" />
</p>

<h1 align="center">🔍 Chrono-Topic-RAG</h1>

<p align="center">
  <strong>A conversation intelligence system that performs dynamic topic segmentation, persona extraction, and retrieval-augmented QA.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Tailwind%20CSS-4.0-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" />
  <img src="https://img.shields.io/badge/sentence--transformers-4.1-FF6F00?style=flat-square" />
  <img src="https://img.shields.io/badge/T5--Small-Summarization-4285F4?style=flat-square&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" />
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-features">Features</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-api-reference">API Reference</a> •
  <a href="#-deployment">Deployment</a>
</p>

---

## 🎬 Demo

### Video Walkthrough

> 📹 **[Watch the full demo on Loom](https://www.loom.com/share/YOUR_LOOM_LINK_HERE)**
>
> *Covers: CSV upload → topic detection → persona extraction → chatbot Q&A*

<!-- Replace the link above with your actual Loom recording URL -->

### Screenshots

<details>
<summary><strong>💬 Chat Interface — Ask questions about the conversation</strong></summary>
<br>

<!-- Replace with actual screenshot -->
<!-- ![Chat Interface](./screenshots/chat.png) -->
> *Screenshot: Upload your screenshot to `screenshots/chat.png` and uncomment the line above*

</details>

<details>
<summary><strong>👤 Persona Panel — Extracted user profile</strong></summary>
<br>

<!-- Replace with actual screenshot -->
<!-- ![Persona Panel](./screenshots/persona.png) -->
> *Screenshot: Upload your screenshot to `screenshots/persona.png` and uncomment the line above*

</details>

<details>
<summary><strong>📑 Topics Panel — Detected conversation topics</strong></summary>
<br>

<!-- Replace with actual screenshot -->
<!-- ![Topics Panel](./screenshots/topics.png) -->
> *Screenshot: Upload your screenshot to `screenshots/topics.png` and uncomment the line above*

</details>

---

## 🎯 What is Chrono-Topic-RAG?

Chrono-Topic-RAG ingests raw conversation data (CSV), processes it through a multi-stage AI pipeline, and provides an intelligent chatbot interface to query insights about the conversations — all without calling OpenAI or any external LLM API.

**Ask questions like:**
- *"What kind of person is this user?"*
- *"What are their daily habits?"*
- *"How do they communicate?"*
- *"What topics were discussed?"*

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Semantic Topic Detection** | Dynamically detects topic shifts using cosine similarity between sentence embeddings — no fixed chunking |
| 📝 **Abstractive Summarization** | Generates topic and checkpoint summaries using Google's T5-Small model |
| 🔍 **Dual-Layer RAG Retrieval** | Retrieves relevant context at both topic-level and message-level for accurate answers |
| 👤 **Persona Extraction** | Extracts habits, personality traits, personal facts, and communication style from evidence in messages |
| 💬 **ChatGPT-Style Interface** | Modern dark-themed chat UI with real-time responses, typing indicators, and a sidebar for persona/topic exploration |
| 📊 **100-Message Checkpoints** | Independent rolling summaries every N messages for temporal context |
| 🚀 **Zero External APIs** | Runs 100% locally using `sentence-transformers` and `transformers` — no API keys, no cost |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    REACT FRONTEND (Vite)                     │
│  ┌────────────┐  ┌────────────────────────────────────────┐ │
│  │  Sidebar    │  │         Chat Interface                 │ │
│  │  ┌────────┐ │  │  ┌──────────────────────────────────┐ │ │
│  │  │Persona │ │  │  │  User & AI message bubbles       │ │ │
│  │  │Panel   │ │  │  │  Typing indicator                │ │ │
│  │  ├────────┤ │  │  │  Quick-action buttons            │ │ │
│  │  │Topics  │ │  │  └──────────────────────────────────┘ │ │
│  │  │Panel   │ │  │  ┌──────────────────────────────────┐ │ │
│  │  ├────────┤ │  │  │  Input box + Send                │ │ │
│  │  │Upload  │ │  │  └──────────────────────────────────┘ │ │
│  │  └────────┘ │  └────────────────────────────────────────┘ │
│  └────────────┘                                              │
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────┐
│                    FASTAPI BACKEND                           │
│                                                              │
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐            │
│  │  Data     │  │  Topic       │  │ Summarizer │            │
│  │  Loader   │──▶ Segmentation │──▶ (T5-Small) │            │
│  │  (CSV)    │  │  (MiniLM)    │  │            │            │
│  └──────────┘  └──────────────┘  └─────┬──────┘            │
│                                         │                    │
│  ┌──────────────────────────────────────▼──────────────┐    │
│  │              RAG System (Dual-Layer)                  │    │
│  │  ┌─────────────────┐  ┌───────────────────────────┐  │    │
│  │  │ Topic Retrieval  │  │  Message Retrieval        │  │    │
│  │  │ (summary embeds) │  │  (all message embeds)     │  │    │
│  │  └─────────────────┘  └───────────────────────────┘  │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Persona Extractor (Rule-Based: Regex + Statistics)    │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
kastack-assignment/
│
├── backend/
│   ├── main.py                  # FastAPI app + processing pipeline
│   ├── data_loader.py           # CSV ingestion + message flattening
│   ├── topic_segmentation.py    # Semantic topic boundary detection
│   ├── summarizer.py            # T5-Small abstractive summarization
│   ├── rag.py                   # Dual-layer retrieval + answer generation
│   ├── persona.py               # Evidence-based persona extraction
│   ├── app.py                   # Streamlit alternative UI
│   ├── Dockerfile               # Production container (pre-downloads models)
│   ├── requirements.txt         # Python dependencies
│   └── data/
│       └── conversations.csv    # Sample conversation data
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx   # Main chat area with messages
│   │   │   ├── MessageBubble.jsx# User/AI message bubbles
│   │   │   ├── Sidebar.jsx      # Collapsible sidebar container
│   │   │   ├── PersonaPanel.jsx # Persona visualization
│   │   │   └── TopicsPanel.jsx  # Topic list with summaries
│   │   ├── App.jsx              # Root component + state management
│   │   ├── api.js               # Backend API client
│   │   ├── main.jsx             # React entry point
│   │   └── index.css            # Design system + animations
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── .github/workflows/
│   └── keep-alive.yml           # Cron job to prevent Render spin-down
│
└── README.md
```

---

## 🧠 How It Works

### 1. Topic Change Detection

> **Core idea:** Topic boundaries are detected dynamically using semantic similarity — not fixed-size chunking.

**Algorithm:**

1. Every message is embedded into a 384-dimensional vector using `all-MiniLM-L6-v2`
2. Cosine similarity is computed between each consecutive pair of message embeddings
3. When similarity drops below a threshold (default: `0.35`), a topic boundary is marked
4. A minimum segment size (default: `5`) prevents micro-topics

```
Msg 1 ─0.82─ Msg 2 ─0.75─ Msg 3 ─0.21─ Msg 4 ─0.68─ Msg 5
                            ▲
                      TOPIC BOUNDARY
                    (0.21 < 0.35 threshold)
```

**Scalability:** For datasets >10K messages, the system uniformly samples 10K messages for topic detection, then embeds all messages for RAG retrieval with batch progress logging.

### 2. Dual-Layer Retrieval (RAG)

When a user asks a question, the system retrieves context from **two independent layers**:

| Layer | What's Indexed | What's Retrieved | Purpose |
|-------|---------------|-----------------|---------|
| **Topic-Level** | Topic summary embeddings | Top-3 most relevant topic summaries | Broad context about conversation themes |
| **Message-Level** | All individual message embeddings | Top-5 most relevant messages | Precise, granular evidence |

Both retrieved contexts are combined and used to generate a grounded answer — the system never hallucinates or invents information.

### 3. Persona Extraction

Persona is extracted using **evidence-based pattern matching** — no guessing, no LLM inference.

| Category | Method | Minimum Evidence |
|----------|--------|-----------------|
| **Habits** | Regex detection for sleep, food, exercise, study, work, screen time patterns | ≥2 matching messages |
| **Personal Facts** | Pattern matching for relationships (`"my mom"`), events (`"my exam"`), preferences (`"I love"`) | Any match with context |
| **Personality Traits** | Tone classification — humor, seriousness, emotional, supportive, analytical | ≥3 matching messages |
| **Communication Style** | Statistical analysis — avg message length, emoji frequency, formality ratio, question frequency | Computed over all messages |

### 4. Answer Generation

- Answers are synthesized from **retrieved context only**
- For persona queries → structured persona data is formatted and returned
- For general queries → relevant topic summaries + messages are presented
- **No external LLM API is used** — synthesis is rule-based and deterministic

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10+ |
| Node.js | 18+ |
| uv | Latest (Python package manager) |

### Backend

```bash
cd backend

# Create virtual environment
uv venv
# Activate:
#   Linux/Mac: source .venv/bin/activate
#   Windows:   .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Start FastAPI server
python main.py
# → http://localhost:8000
# ⚠ First run downloads models (~300MB) — takes 5-10 min
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (auto-proxies to backend)
npm run dev
# → http://localhost:5173
```

### Alternative: Streamlit UI

```bash
cd backend
pip install streamlit
streamlit run app.py
# → http://localhost:8501
```

---

## 📡 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check + processing status |
| `POST` | `/upload` | Upload and process a CSV file |
| `POST` | `/chat` | Query the RAG system |
| `GET` | `/persona` | Retrieve extracted persona JSON |
| `GET` | `/topics` | Retrieve detected topic segments |
| `GET` | `/checkpoints` | Retrieve checkpoint summaries |

### `POST /chat`

```json
// Request
{ "query": "What kind of person is this user?" }

// Response
{
  "response": "Based on conversation analysis, here's the user profile...",
  "retrieved_topics": [
    { "topic_id": 3, "start_index": 20, "end_index": 35, "summary": "...", "relevance_score": 0.72 }
  ],
  "retrieved_messages": [
    { "index": 24, "speaker": "User", "content": "...", "relevance_score": 0.81 }
  ]
}
```

### `GET /persona`

```json
{
  "habits": ["Mentions sleep-related topics frequently", "Regularly discusses food, meals, or drinks"],
  "personal_facts": ["[relationship] \"my mom told me to study harder\""],
  "personality_traits": ["Highly humor — detected in 15 messages (30%)"],
  "communication_style": ["Short, concise messages (avg ~45 chars)", "Heavy emoji user (32% of messages)"]
}
```

### CSV Format

| Column | Description |
|--------|-------------|
| `day` | Day number or date |
| `conversation` | Full day's conversation, newline-separated, format: `Speaker: message` |

```csv
day,conversation
1,"User: Hey how are you
Friend: I'm good, studying for the exam
User: Same, chapter 5 is so hard"
```

---

## ☁️ Deployment

### Backend → Render (Docker)

1. Push repo to GitHub
2. [render.com](https://render.com) → New → **Web Service**
3. Connect repo, set **Root Directory** = `backend`, **Runtime** = `Docker`
4. Deploy (the Dockerfile pre-downloads models at build time)
5. Copy URL: `https://your-app.onrender.com`

### Frontend → Vercel

1. [vercel.com](https://vercel.com) → Import repo
2. Set **Root Directory** = `frontend`
3. Add env var: `VITE_API_URL` = `https://your-app.onrender.com`
4. Deploy

### Keep-Alive (Free Tier)

A GitHub Actions workflow (`.github/workflows/keep-alive.yml`) pings the health endpoint every 14 minutes to prevent Render free tier spin-down.

---

## 🔧 Tech Stack

| Component | Technology | Role |
|-----------|-----------|------|
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | 384-dim sentence vectors for similarity + retrieval |
| **Summarization** | `google/t5-small` | Abstractive text summarization |
| **Similarity** | `sklearn` cosine similarity | Topic boundary detection + RAG ranking |
| **Backend** | FastAPI + Uvicorn | REST API server |
| **Frontend** | React 19 (Vite) + Tailwind CSS 4 | ChatGPT-style interface |
| **Alt. Frontend** | Streamlit | Simpler chat + sidebar UI |
| **Containerization** | Docker | Production deployment |

---

## ⚠️ Design Constraints

| Constraint | How It's Handled |
|-----------|-----------------|
| No OpenAI/GPT APIs | All inference via local `sentence-transformers` + `t5-small` |
| No random chunking | Topic boundaries via semantic similarity, not fixed windows |
| Chronological integrity | Messages processed in strict CSV row → line order |
| No fake personas | Every trait requires ≥2 or ≥3 evidence messages |
| No hallucination | Answers grounded exclusively in retrieved data |

---

## 📄 License

MIT — use it however you want.
