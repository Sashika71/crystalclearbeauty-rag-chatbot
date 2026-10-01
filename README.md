# Crystal Clear Beauty — RAG Chatbot Service 💬

A Python microservice that powers an AI customer-support chatbot for the **Crystal Clear Beauty** e-commerce store, using **Retrieval-Augmented Generation (RAG)**. It answers customer questions about products (prices, descriptions, usage) by retrieving relevant information from a product catalog (PDF) and generating natural-language answers using a large language model.

This service is consumed by a separate backend repo (Express API) which is in turn called by a separate frontend repo (React chat widget).

---

## 🏗️ How it fits into the system

```
React Chat Widget  →  Express Backend  →  this RAG Service  →  Hugging Face LLM
   (frontend repo)      (backend repo)      (/ask endpoint)       (remote API)
```

1. A customer asks a question in the chat widget.
2. The Express backend receives it and forwards it here, to `POST /ask`.
3. This service:
   - Embeds the question using a local embedding model.
   - Retrieves the most relevant chunks from the product PDF (stored in a Chroma vector database).
   - Sends the question + retrieved context to a Hugging Face LLM.
   - Returns the generated answer as JSON.

---

## ⚙️ Tech Stack

| Component | Technology |
|---|---|
| API framework | FastAPI |
| RAG orchestration | LangChain |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (runs locally) |
| LLM | `meta-llama/Llama-3.1-8B-Instruct` (via Hugging Face Inference Providers) |
| Vector database | ChromaDB |
| PDF parsing | pypdf |

---


## 🚀 Getting Started

### Prerequisites

- Python 3.12 (recommended for best compatibility with `torch` / `chromadb` on Windows)
- A free [Hugging Face](https://huggingface.co/settings/tokens) account and API token with **"Make calls to Inference Providers"** permission

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/crystal-clear-beauty-rag.git
cd rag-service
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### 3. Add your environment variables

Create a `.env` file in the project root:

```
HUGGINGFACEHUB_API_TOKEN=your_hf_token_here
HF_TOKEN=your_hf_token_here
```

### 4. Add your product catalog

Place your product catalog PDF in the project root and name it `products.pdf`.

### 5. Run the service

```bash
uvicorn main:app --port 8000
```

On first run, the embedding model (~90 MB) downloads automatically — this may take a minute.

Test it interactively at **http://localhost:8000/docs**.

---

## 🔌 API Reference

### `POST /ask`

Ask a question and get an answer grounded in the product catalog.

**Request**
```json
{ "question": "What is the price of Vitamin C Glow Serum?" }
```

**Response**
```json
{ "answer": "The price of Vitamin C Glow Serum is Rs. 3,500." }
```

### `GET /health`

Simple health check.

**Response**
```json
{ "status": "ok" }
```

---

## 🔐 Environment Variables

| Variable | Description |
|---|---|
| `HUGGINGFACEHUB_API_TOKEN` | Hugging Face API token (used by LangChain) |
| `HF_TOKEN` | Hugging Face API token (used by `huggingface_hub`) |

> ⚠️ Never commit your `.env` file or API tokens. If a token is ever exposed, revoke it immediately at huggingface.co/settings/tokens and generate a new one.

---

## 📝 Notes

- **Embeddings run locally** — no API cost, no internet required after the first model download.
- **The LLM runs remotely** via the Hugging Face Inference API — requires a valid token and an active internet connection.
- The Chroma vector database is rebuilt from `products.pdf` every time the service starts (in-memory, not persisted to disk).
- To update product information, edit/replace `products.pdf` and restart the service.
- If `meta-llama/Llama-3.1-8B-Instruct` is unavailable in your Hugging Face account/region, swap the `repo_id` in `main.py` for another instruction-tuned chat model available on your account's enabled inference providers.

---

## 🧰 Troubleshooting

| Issue | Fix |
|---|---|
| `OSError: ... DLL initialization routine failed` (Windows) | Install the Microsoft Visual C++ Redistributable (x64) and restart your PC |
| `model_not_supported` error from Hugging Face | The model isn't enabled for your account's providers — try a different `repo_id` or enable providers at huggingface.co/settings/inference-providers |
| `Warning: unauthenticated requests to the HF Hub` | Ensure both `HUGGINGFACEHUB_API_TOKEN` and `HF_TOKEN` are set in `.env` |
| `ModuleNotFoundError` | Make sure the virtual environment is activated (`venv\Scripts\activate`) before running `uvicorn` |

---

## 📄 License

This project is for internal use by Crystal Clear Beauty.
