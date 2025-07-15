# Documentation Assistant **for LangChain**

> A self‑contained chatbot that indexes the entire LangChain Python documentation, stores it in Pinecone, and lets you query it conversationally with source citations.

![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.46-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.3.x-9cf?logo=langchain)
[![LangSmith](https://img.shields.io/badge/LangSmith-enabled-brightgreen)](https://smith.langchain.com/o/856312b1-7816-4389-80cb-b01e398655be/projects/p/29eae9f5-17ef-4946-a14b-58a9570b274e?timeModel=%7B%22duration%22%3A%227d%22%7D)
[![Pinecone](https://img.shields.io/badge/Pinecone-VectorDB-blueviolet)](https://app.pinecone.io/organizations/-OQOYTa7PD5A_F9pFlNC/projects/0fed2f10-ab48-4302-a34b-583868c23c78/indexes/documentation-assistant-project/browser)
[![Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Spaces-langchain__documentation__assistant-yellow?logo=huggingface)](https://huggingface.co/spaces/ndk211/langchain_documentation_assistant)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
---

## What I built 🔍

* **Full‑text crawler & indexer** – loads the LangChain Read‑the‑Docs site, chunks each page to ±600 chars, cleans the URLs and writes the embeddings to **Pinecone** using *`text‑embedding‑3‑small`* ([raw.githubusercontent.com](https://raw.githubusercontent.com/ndkhoa211/documentation_assistant_project/main/ingestion.py))
* **History‑aware retrieval chain** – wraps a GPT‑4.1 chat model with LangChain’s *history‑aware retriever* + *retrieval‑qa‑chat* prompts for grounded answers. ([raw.githubusercontent.com](https://raw.githubusercontent.com/ndkhoa211/documentation_assistant_project/main/backend/core.py))
* **Streamlit front‑end** – a one‑file UI (`main.py`) with a profile sidebar, chat bubbles, and clickable source links. ([raw.githubusercontent.com](https://raw.githubusercontent.com/ndkhoa211/documentation_assistant_project/main/main.py))
* **Re‑usable project template** – dependency‑pinned **pyproject.toml** (uv‑style), theming via `.streamlit/config.toml`, and a deploy‑ready HF Spaces repo. ([raw.githubusercontent.com](https://raw.githubusercontent.com/ndkhoa211/documentation_assistant_project/main/pyproject.toml), [raw.githubusercontent.com](https://raw.githubusercontent.com/ndkhoa211/documentation_assistant_project/main/.streamlit/config.toml))

---

## Quick demo

```bash
# 1 Clone & enter
$ git clone https://github.com/ndkhoa211/documentation_assistant_project
$ cd documentation_assistant_project

# 2 Create isolated env (uv recommended)
$ uv venv            # → .venv/
$ source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3 Install runtime deps + dev extras
$ uv pip install -e .

# 4 Set your secrets (OpenAI + Pinecone)
$ cat > .env <<'EOF'
OPENAI_API_KEY=sk‑...
PINECONE_API_KEY=...
PINECONE_ENV=us‑east‑1‑aws
EOF

# 5 One‑off ingestion (≈ 2–3 min)
$ python ingestion.py

# 6 Launch the chat app
$ streamlit run main.py
```

> **Tip** – Skip steps 2‑6 entirely by hitting the 🤗 **Spaces** badge above. (CURRENTLY MADE PRIVATE)

---

## How it works

### 1. Ingestion pipeline

1. **ReadTheDocsLoader** pulls every `.html` page from the local mirror `langchain-docs/`.
2. `RecursiveCharacterTextSplitter` cuts pages into 600‑character overlaps to fit the 8 k context window.
3. Each chunk is embedded with **OpenAI `text‑embedding‑3‑small`**, then upserted in batches of 100 to **Pinecone** (`documentation-assistant-project` index).
4. Canonical HTTPS URLs are patched into `Document.metadata['source']` so users can click through.

### 2. Retrieval‑augmented generation

* On each user prompt:

  * **History‑aware retriever** rewrites the question given the last turns.
  * Top‑k documents (k=4 default) are fetched from Pinecone.
  * GPT‑4.1 is run with the `retrieval-qa-chat` prompt and stuffed context.
* The response is streamed back with numbered source links.

### 3. Streamlit UI

The chat front‑end lives entirely in `main.py` and offers:

* Persistent *`st.session_state`* chat history.
* (Made with Cursor) A sidebar showing user initials, contact info, and project branding.
* (Made with Cursor) Pytorch-alike color palette configured in `.streamlit/config.toml`.

---

## Repository structure

```text
documentation_assistant_project/
├── backend/
│   ├── core.py        # retrieval chain logic
│   └── __init__.py
├── langchain-docs/    # offline copy of docs (git‑ignored in remote)
├── ingestion.py       # crawl ➜ chunk ➜ embed ➜ upsert
├── main.py            # Streamlit app
├── .streamlit/
│   └── config.toml    # theme + static serving
├── pyproject.toml     # deps pinned for uv
└── uv.lock            # exact versions
```

---

## Environment variables

| Variable            | Purpose                       |
|---------------------|-------------------------------|
| `OPENAI_API_KEY`    | LLM + embeddings              |
| `PINECONE_API_KEY`  | Vector database access        |
| `PINECONE_ENV`      | Region (e.g. `us-east-1-aws`) |
| `INDEX_NAME`        | Vector database index         |
| `LANGSMITH_API_KEY` | LLM calls tracing             |
| `LANGCHAIN_PROJECT` | Documen t Assistant Project   |
| `LANGSMITH_TRACING` | true                          |

Store them in a local `.env` – they are loaded by `python‑dotenv` at runtime.

