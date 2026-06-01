# M4ST Prompt Reuse Cache

Repeated-prompt reuse layer by Mast Anuj.

This module reduces repeated LLM work by storing prompt/response embeddings locally and returning a prior answer when a new prompt is similar enough.

## What It Does

- Stores prompt and response pairs locally.
- Generates embeddings for similarity search.
- Returns cached answers for near-duplicate prompts.
- Reduces repeated API calls.
- Keeps data local by default.
- Integrates with M4ST routing workflows.

## Core Loop

```text
new prompt -> embed -> similarity search -> hit? -> return cached answer
                                      -> miss? -> call model and store result
```

## Install

```bash
# From this repository folder
pip install -r requirements.txt
```

## Example

```python
from semantic_cache import SemanticCache

cache = SemanticCache(
    ttl=3600,
    max_entries=300,
    similarity_threshold=0.92,
)

@cache.wrap
def call_llm(prompt: str) -> str:
    return client.chat(prompt)
```

## M4ST Fit

This module supports:

- M4ST local AI operator
- M4ST model router
- research workflows
- repeated documentation tasks
- low-cost/free-first usage

## Safety Boundary

Do not cache secrets, passwords, API keys, private messages, personal contact data, or sensitive account/session content.

Use a lower-retention or disabled cache mode for private/security-sensitive work.
