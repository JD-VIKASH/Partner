<div align="center">

<img src="https://img.shields.io/badge/Frieren-Cognitive_AI_Partner-7C3AED?style=for-the-badge&logo=openai&logoColor=white" alt="Frieren" />

# 🦋 Frieren — Cognitive AI Partner

**One Brain, Many Devices. A calm, wise, and persistent AI companion for your studies and projects.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-Agentic-1C3C3C?style=flat-square&logo=chainlink&logoColor=white)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-F55036?style=flat-square&logo=meta&logoColor=white)](https://groq.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Memory-E86428?style=flat-square)](https://trychroma.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## ✨ Overview

**Frieren** is a multi-device, agentic AI partner built around a centralized cognitive backend. She is not a simple chatbot — she is a fully-stateful reasoning system with persistent long-term memory, goal tracking, skill progression, and real-time voice interaction.

> *"I am Frieren, a calm and serene study partner, with a deep love for learning and sharing knowledge."*

Frieren operates on a **Client–Brain architecture**: a FastAPI backend handles all cognitive processing (reasoning, memory, reflection), while a lightweight Windows voice client acts as the human interface. This allows Frieren to remain consistent, context-aware, and personalized across multiple devices and sessions.

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Windows Voice Client                  │
│  (Frieren.py) — Microphone → STT → HTTP → TTS → Speaker│
└──────────────────────┬──────────────────────────────────┘
                       │  REST API (localhost:8000)
┌──────────────────────▼──────────────────────────────────┐
│              Frieren Cognitive Backend (FastAPI)         │
│                                                         │
│  ┌─────────────────┐   ┌───────────────────────────┐   │
│  │  Reasoning Engine│   │   State Management        │   │
│  │  (LangChain +   │   │  - User Profile           │   │
│  │   Groq LLaMA)   │   │  - Goal Management        │   │
│  └────────┬────────┘   │  - Project Engine         │   │
│           │            │  - Skill Engine            │   │
│  ┌────────▼────────┐   └───────────────────────────┘   │
│  │  Memory System  │                                    │
│  │ - Working Memory│   ┌───────────────────────────┐   │
│  │ - Long-Term     │   │   Tools / Spells          │   │
│  │   (ChromaDB)    │   │  - Web Search (DuckDuckGo)│   │
│  │ - Consolidation │   │  - File Save              │   │
│  │ - Reflection    │   │  - Goal & Skill Tools     │   │
│  └─────────────────┘   └───────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │           PWA Frontend (Browser Client)          │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🧠 Core Modules

### 🔮 Cognitive Backend (`backend/`)
A **FastAPI** server exposing the full cognitive API. It orchestrates all reasoning, memory retrieval, and state management.

| Route | Description |
|---|---|
| `POST /api/v1/chat` | Main conversational endpoint |
| `GET /api/v1/health` | Backend health check |
| `GET/POST /api/v1/memory` | Memory read/write operations |
| `GET/POST /api/v1/state` | User state (goals, projects, skills) |
| `GET /api/v1/conversations` | Conversation history |
| `GET /api/v1/system` | System diagnostics |

### 🧩 Reasoning Engine (`core/reasoning.py`)
The central intelligence. For every user message, it:
1. **Assembles a Context Package** — pulls from long-term memory, user profile, active goals, projects, and skills
2. **Runs an Agentic Tool Loop** — up to 5 iterations with LangChain + Groq (LLaMA 3.1 8B Instant)
3. **Updates Working Memory** — keeps the session coherent
4. **Triggers Background Reflection** — asynchronously stores insights via `ReflectionSystem`

### 💾 Memory System (`memory/`)
A multi-tiered memory architecture backed by **ChromaDB** (ONNX MiniLM-L6 vector embeddings):

| Component | Role |
|---|---|
| `WorkingMemory` | Short-term in-session conversation buffer |
| `LongTermMemory` | **Episodic** (events/experiences) + **Semantic** (facts/identity) ChromaDB stores |
| `RetrievalEvaluator` | Distance-based scoring to filter relevant memories before they reach the LLM |
| `MemoryFilter` | Pre-filters noise before vector insertion |
| `MemoryConsolidation` | Periodic deduplication and compression of stored memories |

### 🗂️ State Management (`state/`)
Persistent SQLite-backed engines that give Frieren awareness of your life and learning:

- **`UserProfileEngine`** — Name, preferences, communication style
- **`GoalManagementSystem`** — Create, track, and complete long-term goals
- **`ProjectEngine`** — Active project descriptions and status
- **`SkillEngine`** — Skill tracking with category, level, and progress percentage
- **`PersonalizationLayer`** — Dynamically modifies the system prompt based on user profile

### 🛠️ Tools / Spells (`tools/`)
Agentic tools that Frieren can autonomously invoke:

| Tool | Spell Name | Description |
|---|---|---|
| `base_tools.py` | Search, Save, Spidy_Web | Web search (DuckDuckGo), file save, HTML generator |
| `goal_tools.py` | Goal Management | Add, complete, and list user goals |
| `skill_tools.py` | Skill Tracker | Log and update skill progression |

### 🖥️ Windows Voice Client (`Frieren.py` + `core/`)
A voice-first Windows interface:
- **Perception** (`core/perception.py`): Google Speech Recognition via microphone
- **Output** (`core/output.py`): Neural TTS using Edge-TTS (`en-US-AvaNeural`)
- **Proactive Assistant** (`core/proactive_assistant.py`): Contextual suggestions without being asked

### 🌐 Progressive Web App (`frontend/`)
A browser-based PWA client (`index.html` + `manifest.json` + `service-worker.js`) for accessing Frieren from any device on the local network.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- A **Groq API Key** (free tier available at [console.groq.com](https://console.groq.com))
- A working **microphone and speakers** (for the voice client)

### 1. Clone the Repository

```bash
git clone https://github.com/JD-VIKASH/Partner.git
cd Partner
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn langchain-groq langchain-core langchain \
            chromadb SpeechRecognition edge-tts playsound3 \
            python-dotenv duckduckgo-search requests
```

### 3. Configure Environment

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
FRIEREN_API_KEY=your_optional_api_key_for_auth
```

### 4. Start the Cognitive Backend

```bash
python backend/app.py
```

The API will be live at `http://localhost:8000`. You can explore the interactive docs at `http://localhost:8000/docs`.

### 5. Launch the Windows Voice Client

In a **second terminal**:

```bash
python Frieren.py
```

Wait for:
```
✨ MAGE FRIEREN: WINDOWS CLIENT ONLINE ✨
[Backend Connected]
🦋 Frieren: It is good to see you again...
```

Then start speaking! 🎙️

---

## 🗣️ Voice Commands

### Natural Conversation
Just speak naturally — Frieren will listen, reason, use tools if needed, and respond via voice.

### Shutdown Phrases
Say any of the following to end the session gracefully:

| Phrase |
|---|
| "exit" / "quit" |
| "stop studying" |
| "goodbye" |
| "go to sleep" / "sleep frieren" |
| "turn off" / "shut down" |

---

## 📁 Project Structure

```
Partner/
│
├── Frieren.py                  # Windows voice client entry point
├── backend/
│   ├── app.py                  # FastAPI server
│   ├── routes/                 # API route handlers (chat, memory, state, etc.)
│   ├── services/               # Session manager, user identity
│   ├── auth/                   # API key authentication middleware
│   └── schemas/                # Pydantic request/response models
│
├── core/
│   ├── reasoning.py            # 🧠 Main ReasoningEngine (LangChain agentic loop)
│   ├── perception.py           # 🎙️ Voice input (speech-to-text)
│   ├── output.py               # 🔊 Voice output (Edge-TTS)
│   ├── reflection.py           # 💡 Background memory reflection
│   └── proactive_assistant.py  # 🌟 Proactive contextual suggestions
│
├── memory/
│   ├── long_term_memory.py     # ChromaDB episodic + semantic stores
│   ├── working_memory.py       # In-session conversation buffer
│   ├── retrieval_evaluator.py  # Memory relevance scoring
│   ├── memory_filter.py        # Pre-insertion noise filtering
│   └── consolidation.py        # Memory deduplication & compression
│
├── state/
│   ├── user_profile.py         # User identity & preferences
│   ├── goal_management.py      # Long-term goal tracking
│   ├── project_engine.py       # Active project management
│   ├── skill_engine.py         # Skill levels & progress
│   └── personalization.py      # Dynamic prompt personalization
│
├── tools/
│   ├── base_tools.py           # Search, Save, Spidy_Web spells
│   ├── goal_tools.py           # Goal management tools
│   └── skill_tools.py          # Skill tracking tools
│
├── frontend/                   # PWA browser client
│   ├── index.html
│   ├── manifest.json
│   └── service-worker.js
│
├── db/                         # ChromaDB persistent vector store
├── tests/                      # API and unit tests
└── .env                        # API keys (not committed)
```

---

## 🔬 Running Tests

```bash
python -m pytest tests/
```

Or run the standalone agent test:

```bash
python test_agent.py
```

---

## 🛣️ Roadmap

- [ ] Android/iOS mobile voice client
- [ ] Redis-backed session management for multi-user production
- [ ] Scheduled proactive check-ins (daily summaries, goal reminders)
- [ ] Deeper RAG pipeline with PDF/document ingestion
- [ ] Web dashboard for memory, goal, and skill visualization

---

## 🤝 Contributing

Contributions are welcome! Please open an issue to discuss proposed changes before submitting a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

*Built with 🦋 and a love for calm, persistent intelligence.*

**Frieren — One Brain, Many Devices.**

</div>
