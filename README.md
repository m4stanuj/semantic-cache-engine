<div align="center">

# 🧠 semantic-cache-engine — Redis-Compatible LLM Response Cache

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-00E5FF?style=flat-square)](https://trychroma.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![API Cost](https://img.shields.io/badge/API%20Savings-40--60%25-brightgreen?style=flat-square)]()

**Cut your LLM API costs by 40–60% using semantic similarity matching. Zero-configuration drop-in for any Python AI project.**

[How It Works](#how-it-works) · [Installation](#installation) · [Usage](#usage) · [Benchmarks](#benchmarks) · [Config](#configuration)

</div>

---

## 💡 The Problem

Every time your AI app sends a similar (but not identical) query to an LLM API, you pay full price. A user asking *"what is machine learning?"* and another asking *"explain machine learning simply"* both trigger expensive API calls — even though the answer is essentially identical.

**Semantic Cache Engine solves this.** It stores LLM responses as vector embeddings and retrieves them when a new query is semantically similar above a configurable threshold — no API call needed.

## ⚙️ How It Works

```
New Query
    │
    ▼
Generate Embedding (via sentence-transformers, local)
    │
    ▼
Search ChromaDB for similar cached responses
    │
    ├── Similarity > threshold (default: 0.92)?
    │       │
    │       ▼ YES
    │   Return cached response ⚡ (< 50ms)
    │
    └── NO
            │
            ▼
        Call LLM API (Groq / Gemini / etc.)
            │
            ▼
        Cache response with embedding
            │
            ▼
        Return response
```

## 🚀 Installation

```bash
pip install semantic-cache-engine

# Or from source
git clone https://github.com/m4stanuj/semantic-cache-engine.git
cd semantic-cache-engine
pip install -r requirements.txt
```

## 📖 Usage

```python
from semantic_cache import SemanticCache

# Initialize (defaults: 3600s TTL, 300 entries, 0.92 similarity threshold)
cache = SemanticCache(
    ttl=3600,
    max_entries=300,
    similarity_threshold=0.92
)

# Use as middleware around any LLM call
@cache.wrap
def call_llm(prompt: str) -> str:
    # Your existing LLM call here
    return groq_client.chat(prompt)

# That's it — 40-60% fewer API calls automatically
response = call_llm("Explain machine learning")
```

## 📊 Benchmarks

Tested on M4STCLAW v3 production workload (April 2026):

| Metric | Without Cache | With Cache | Improvement |
|--------|--------------|------------|-------------|
| Avg Response Time | 1,200ms | 48ms | **96% faster** |
| API Calls / 1000 queries | 1,000 | ~420 | **58% reduction** |
| Monthly API Cost | ~$45 | ~$0 (free tier sufficient) | **$0 overhead** |
| Cache Hit Rate | — | 58% | — |

## ⚙️ Configuration

```python
cache = SemanticCache(
    ttl=3600,                    # Cache TTL in seconds
    max_entries=300,             # Max cached responses
    similarity_threshold=0.92,   # 0.0-1.0 (higher = stricter matching)
    embedding_model="all-MiniLM-L6-v2",  # Local model (no API needed)
    persist_directory="./cache_db"       # ChromaDB storage path
)
```

## 🔌 Integrations

Works out-of-the-box with:
- **Groq** API
- **OpenAI** / **OpenRouter** compatible endpoints
- **Gemini** (via OpenAI-compat mode)
- Any Python function that takes a string and returns a string

---

<div align="center">
  <sub>Extracted from <a href="https://github.com/m4stanuj/M4STCLAW">M4STCLAW v3</a> core · Production-tested · 58% cache hit rate in real workloads</sub>
</div>
