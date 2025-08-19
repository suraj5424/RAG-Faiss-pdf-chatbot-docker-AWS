# 🤖 RAG Chatbot App

**🖥️ Streamlit frontend • 🐍 Python RAG backend • 🐳 Docker Compose • 🌐 NGINX reverse proxy • ☁️ AWS EC2 (t3.micro, Free Tier) • ⏰ cron scheduling**

🔗 **Live App:** [Click here to experience the app](http://51.20.104.45/) 


🎬 Demo Preview 👇

<img src="https://github.com/suraj5424/RAG-Faiss-pdf-chatbot-docker-AWS/blob/main/demo.gif" alt="Demo of Virtual Gesture Mouse" style="width:600px; height:auto;" />


This single README documents the **entire** RAG Chatbot web application: local development, containerized deployment, NGINX reverse proxy, and a low-cost AWS EC2 deployment with scheduled runtime using `cron` to reduce resource usage. Follow this guide to set up, run, deploy, and maintain the app.

---

# 📌 1. Project Title & Description

**Name:** `RAG Chatbot App`

**Short description:**
A web application that combines retrieval (vector search over ingested documents) with a Large Language Model to produce context-aware chat responses (Retrieval-Augmented Generation — RAG). The frontend is a Streamlit chat UI; the backend handles ingestion, embedding generation, vector search, reranking (MMR), and LLM calls. Deployable with Docker Compose behind an NGINX reverse proxy; optimized to run on a Free Tier AWS EC2 `t3.micro` by applying container-level resource limits and scheduled runtime.

---

# 🏗️ 2. Architecture Overview

## Logical diagram (textual)

```
[User Browser]
      |
   (HTTP 80)
      |
   [NGINX Reverse Proxy] -----> [Streamlit Frontend Container (8501)]
      |
      `----> [Backend Container (8000)] (internal API calls from frontend)
```

* **NGINX** listens on port **80** and forwards traffic to the Streamlit frontend container.
* **Frontend (Streamlit)** provides UI, maintains per-session state (`st.session_state`), and calls backend endpoints such as `/chat`, `/ingest`, `/summarize`.
* **Backend (FastAPI or similar)** performs document ingestion, text chunking, embedding generation (ONNX MiniLM or provider), stores vectors (FAISS or managed vector DB), executes retrieval (including MMR), and routes prompts to an LLM provider (OpenAI/OpenRouter/etc.).
* All services are Dockerized and orchestrated by **Docker Compose**.

## Tech-stack summary

* **Frontend:** Streamlit (Python)
* **Backend:** Python (FastAPI), LangChain-like pattern, local ONNX embeddings and FAISS (or external vector store)
* **Reverse proxy:** NGINX
* **Container orchestration:** Docker Compose (v3.8)
* **Hosting:** AWS EC2 (Ubuntu 24.04 LTS, `t3.micro`)
* **Scheduling:** `cron` jobs for start/stop to conserve resources
* **Env management:** `.env` file and (recommended) AWS Secrets Manager for production secrets

---

# ✨ 3. Features

## Backend

* File & URL ingestion (PDFs, web pages)
* Text chunking + embedding generation (ONNX MiniLM or provider-based)
* Vector store integration (FAISS local, or managed vector DB like Qdrant/Pinecone)
* Retriever with MMR re-ranking and configurable fetch/k
* LLM integration via provider (OpenAI / OpenRouter / other)
* API endpoints: `/chat`, `/ingest`, `/summarize`, `/remove_vectors`, `/remove_all_vectors`, `/settings`, `/switch_model`, `/health`

## Frontend

* Streamlit chat UI with `st.chat_input` / `st.chat_message`
* Per-user session isolation via `st.session_state` and `session_id`
* Upload PDFs or provide URLs to ingest
* Control temperature and embedding model mode
* Display AI responses and retrieved source attributions
* Export chat (JSON / Markdown / PDF)

## Infrastructure

* Docker Compose deployment with container-level memory & CPU limits
* NGINX reverse proxy exposes only port **80** (optionally 443)
* Cron jobs to start/stop containers on a schedule to keep costs low

---

# 🧰 4. Technologies Used

* **Languages:** Python 3.10+ (recommended)
* **Frontend:** Streamlit
* **Backend:** FastAPI (or similar), LangChain components (optional)
* **Embeddings model**: **all-MiniLM-L6-v2**
* **Embed / Vector:** ONNX + onnxruntime (ONNX MiniLM), FAISS (local)
* **Qunatisation**: quantised the converted onnx model to increase the  speed and  reduce the model size.
* **LLM and providers:** **deepseek-chat-v3-0324 from Openrouter**
* **Containers:** Docker, Docker Compose (v3.8)
* **Proxy:** NGINX (alpine image)
* **Hosting:** AWS EC2 (Ubuntu 24.04 LTS)
* **Scheduling:** crontab (system cron)
* **Utilities:** python-dotenv, requests/httpx, PyMuPDF/pypdf for PDF handling

---

# 📋 5. System Requirements

**For AWS deployment (recommended minimal config):**

* Instance: `t3.micro` (Free Tier) — 2 vCPUs (burstable), 1 GiB RAM
* Storage: EBS gp3/gp2 — 30 GB (start)
* OS: Ubuntu Server 24.04 LTS (x86\_64)
* Docker & Docker Compose installed

**Local dev requirements:**

* Python 3.10+
* Streamlit & backend dependencies
* Docker (optional for containerized local testing)

> ⚠️ Note: The `t3.micro` is memory-limited. We use swap + container memory limits; for multi-user or heavier embeddings, upgrade the instance.

---

# 🔧 6. Installation & Setup

## Clone repository

```bash
git clone https://github.com/your-repo/rag-chatbot.git
cd rag-chatbot
```

## Project directory

```
rag-chatbot/
├─ backend/                # Python backend (FastAPI)
│  ├─ main.py
│  ├─ Dockerfile
│  └─ requirements.txt
├─ frontend/               # Streamlit app
│  ├─ app.py
│  ├─ css.py
│  └─ requirements.txt
├─ nginx/
│  ├─ Dockerfile
│  └─ nginx.conf
├─ docker-compose.yml
└─ .env
```

## Create & populate `.env`

Copy the file and edit with your secrets:

```bash
cp .env .env
nano .env
```

### Enter you model API KEY.

```env
OPENROUTER_API_KEY=...
```

---

# 🐳 7. Docker Compose — `docker-compose.yml`

Below is a recommended `docker-compose.yml` tuned for a `t3.micro`:

```yaml
version: '3.8'

services:
  backend:
    image: suraj5424/rag-backend:latest
    container_name: rag-backend
    env_file:
      - .env
    expose:
      - "8000"
    volumes:
      - ./backend/onnx_model:/app/onnx_model:ro
      - ./backend/user_data:/app/user_data
    restart: always
    mem_limit: 600m
    cpus: 0.5
    logging:
      driver: "json-file"
      options:
        max-size: "5m"
        max-file: "3"

  frontend:
    image: suraj5424/rag-frontend:latest
    container_name: rag-frontend
    env_file:
      - .env
    expose:
      - "8501"
    depends_on:
      - backend
    restart: always
    mem_limit: 350m
    cpus: 0.4
    logging:
      driver: "json-file"
      options:
        max-size: "5m"
        max-file: "3"

  nginx:
    build: ./nginx
    container_name: nginx-reverse-proxy
    ports:
      - "80:80"
    depends_on:
      - frontend
      - backend
    restart: always
    mem_limit: 200m
    cpus: 0.2
    logging:
      driver: "json-file"
      options:
        max-size: "5m"
        max-file: "3"

networks:
  default:
    driver: bridge
```

**Notes**

* Replace `suraj5424/...` with your actual image names or use local Dockerfiles via `build:`.
* Volume mounts for `onnx_model` and `user_data` ensure persistence across container restarts.

---

# 🌐 8. NGINX Configuration (`nginx/nginx.conf`)

**`nginx/Dockerfile`**

```dockerfile
FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**`nginx/nginx.conf`**

```nginx
server {
    listen 80;
    server_name _;  # replace with your.domain.tld if you have one

    # Proxy base traffic to Streamlit frontend
    location / {
        proxy_pass http://frontend:8501;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_cache_bypass $http_upgrade;
    }

    # Health /status proxied to backend health endpoint
    location /health {
        proxy_pass http://backend:8000/health;
        proxy_set_header Host $host;
    }

    # Optional: static files or admin endpoints can be routed similarly
}
```

**Routing logic summary**

* NGINX listens on host port 80 → proxies to Docker Compose service `frontend:8501`.
* `/health` routed to backend health endpoint so external checks can verify backend status.
* If using a domain, update `server_name` and add TLS blocks for 443 (see Security).

---

# ⏰ 9. Cron Job Scheduling (Start/Stop)

To reduce runtime costs and resource usage, the plan is to run the **backend** only **Mon–Sat 07:00–22:00 (Berlin time)** and allow the **frontend** to stay online during the day.

### Crontab (Berlin timezone approach)

Edit crontab:

```bash
crontab -e
```

Add:

```cron
# Use Berlin time for schedule
TZ=Europe/Berlin

# Start backend at 07:00 Mon-Sat
0 7 * * 1-6 /usr/bin/docker start rag-backend

# Stop backend at 22:00 Mon-Sat
0 22 * * 1-6 /usr/bin/docker stop rag-backend

# Ensure backend is stopped on Sunday at midnight
0 0 * * 0 /usr/bin/docker stop rag-backend

# Start frontend at 07:00 Mon-Sat (frontend may remain running 24/7 if desired)
0 7 * * 1-6 /usr/bin/docker start rag-frontend
```

**Notes & tips**

* Use full paths (`/usr/bin/docker` or `which docker`).
* If you prefer `docker-compose` start/stop behavior, point cron to `docker compose -f /path/to/docker-compose.yml up -d` or `down`.
* Make sure the `ubuntu` user has permissions for Docker commands in crontab or use `sudo` in crons.

---

# 🔐 10. Environment Variables (Detailed)

**`.env.example`**

```env
# LLM provider & keys
MODEL_NAME=your-model-name
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=

# Host references (use service names inside Docker Compose)
BACKEND_HOST=http://backend:8000
FRONTEND_HOST=http://frontend:8501

# App configuration
MAX_UPLOAD_MB=10
RETRIEVER_K=4
RETRIEVER_FETCH_K=10
MMR_LAMBDA=0.7

# Admin / light auth (optional)
ADMIN_API_KEY=changeme
```

**Security note**

* DO NOT commit `.env` to source control. For production, use AWS Secrets Manager, Parameter Store, or Docker secrets.

---

# 💾 11. Resource Management & Rationale

**Compose-level resource limits**

* `backend`: `mem_limit: 600m`, `cpus: 0.5`
  Rationale: Embedding/ML operations are backend-heavy; limit to 600MB to avoid OOM on `t3.micro`, yet leave some headroom.
* `frontend`: `mem_limit: 350m`, `cpus: 0.4`
  Rationale: Streamlit is lightweight but needs memory for session data and rendering.
* `nginx`: `mem_limit: 200m`, `cpus: 0.2`
  Rationale: NGINX is extremely lightweight.

**How this fits Free Tier**

* `t3.micro` has 1 GiB RAM. With swap (recommended 1 GiB) and the above limits, typical demo workloads run with occasional bursts. For heavier loads, upgrade instance.

**Logging & disk**

* Docker logging capped (`max-size: "5m"`, `max-file: "3"`) to avoid disk filling on EBS.

---

# 🚀 12. Usage — Running & Accessing

## Local (non-Docker) quick dev

* Backend: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`
* Frontend: `cd frontend && pip install -r requirements.txt && streamlit run app.py`
* Point frontend to `http://localhost:8000` in env.

## Containerized (recommended)

Build & start:

```bash
docker-compose up -d --build
```

Check containers:

```bash
docker ps
docker logs -f rag-frontend
docker logs -f rag-backend
docker logs -f nginx-reverse-proxy
```

**Access**

* Public: `http://<EC2_PUBLIC_IP>/` (NGINX forwards to Streamlit)
* Health: `http://<EC2_PUBLIC_IP>/health` (if proxied)

**Restart or stop**

```bash
docker-compose restart backend
docker-compose stop backend
docker-compose up -d
```

---

# 🧪 13. API / Frontend Integration (contract summary)

The frontend expects the backend endpoints below. Match payloads exactly for compatibility.

### `POST /chat?session_id=<id>`

**Request JSON**

```json
{
  "query": "What is RAG?",
  "chat_history": [{"role":"user","content":"Hi"}],
  "temperature": 0.7
}
```

**Response JSON**

```json
{
  "response": "Answer text...",
  "source_type": "RAG" | "Tool" | "LLM_Internal_Knowledge",
  "retrieved_sources": [{"source":"file.pdf","page":2}],
  "temperature": 0.7
}
```

### `POST /ingest?session_id=<id>`

* Form-data: `file` (PDF) OR `url` (string)
* Response: ingestion status, content hash

### `POST /summarize?session_id=<id>`

* Form-data: `file` or `url`
* Response: `{ "summary": "..." }`

### `DELETE /remove_vectors?session_id=<id>&source=<source>`

* Removes vectors tied to a source

### `DELETE /remove_all_vectors?session_id=<id>`

* Clears all ingested vectors for session

### `GET/POST /settings?session_id=<id>`

* GET returns session settings, POST updates (e.g., `{"temperature":0.5}`)

### `POST /switch_model?session_id=<id>`

* Form param: `quantized=true|false`
* Switches embeddings model variant

---

# 📜 14. Contribution, License & Credits

**License**

* Add `LICENSE` file (MIT or Apache-2.0 recommended for permissive use).

**Credits**

* Project assembled from Streamlit frontend + Python RAG backend design; NGINX containerization and basic orchestration.

---

# ✅ 15. Quick Deploy Checklist

1. Launch EC2 `t3.micro` (Ubuntu 24.04) and configure security group (SSH + HTTP).
2. SSH into instance and install Docker & Docker Compose.
3. Clone repository into `/home/ubuntu/rag-deploy`.
4. Create `.env` from `.env.example` (do not commit).
5. (Recommended) Create 1GB swapfile to avoid memory OOMs.
6. Place `nginx/nginx.conf` and confirm `docker-compose.yml` values.
7. `docker-compose up -d --build`
8. Add crontab entries for scheduled start/stop.
9. Verify site at `http://<EC2_PUBLIC_IP>/`.
10. Add TLS & secrets in production; consider upgrading instance for heavy use.

---

# 📚 16. Further Enhancements (next steps)

* Add authentication (JWT / API keys) and an admin UI.
* Replace local FAISS with Qdrant (hosted) or Pinecone (managed) for multi-instance scaling.
* Add centralized logs and metrics (Prometheus + Grafana, CloudWatch).
* Integrate CI/CD (GitHub Actions) for image builds and automatic deploys to EC2.

---

## 🙋 Author & Contact

**Author:** Suraj Varma
**Email:** sv3677781@gmail.com  
**GitHub:** [@suraj5424](https://github.com/suraj5424)  
**LinkedIn:** [Suraj Varma](https://www.linkedin.com/in/suraj5424/)  
**Website/Portfolio:** [Suraj Varma](https://suraj-varma.vercel.app/)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## ⭐ Acknowledgments

- Built with [Streamlit](https://streamlit.io), [FastAPI](https://fastapi.tiangolo.com), and [Docker](https://www.docker.com).  
- Reverse proxy powered by [NGINX](https://nginx.org).  
- Hosted on [AWS EC2](https://aws.amazon.com/ec2/).  

---

## 🙏 Support

If you find this project useful, please give it a ⭐ on GitHub!  
