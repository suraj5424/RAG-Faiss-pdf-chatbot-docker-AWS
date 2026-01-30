# 🤖 RAG Chatbot App
**🖥️ Streamlit frontend • 🐍 Python RAG backend • 🐳 Docker Compose • 🌐 NGINX reverse proxy • ☁️ AWS EC2 (t3.micro, Free Tier) • ⏰ cron scheduling**

🔗 **Live App:** [Click here to experience the app](http://13.48.71.0/)

---

## 🎬 Demo Preview 👇

<!-- <img src="https://github.com/suraj5424/RAG-Faiss-pdf-chatbot-docker-AWS/blob/main/demo.gif" alt="Demo of RAG Chatbot Application" style="width:600px; height:auto;" />file -->

### **Reduce the video speed to 0.25×**

https://github.com/user-attachments/assets/cc2f212c-ef5d-4a87-bb59-cf206771e045



This README documents the **entire** RAG Chatbot web application: local development, containerized deployment, NGINX reverse proxy, and a low‑cost AWS EC2 deployment with scheduled runtime using `cron` to reduce resource usage. Follow this guide to set up, run, deploy, and maintain the app.

---

# 📌 1. Project Title & Description

**Name:** `RAG Chatbot App`

**Short description:**  
A web application that combines retrieval (vector search over ingested documents) with a Large Language Model to produce context‑aware chat responses (Retrieval‑Augmented Generation — RAG). The frontend is a Streamlit chat UI; the backend handles ingestion, embedding generation, vector search, reranking (MMR), and LLM calls. Deployable with Docker Compose behind an NGINX reverse proxy; optimized to run on a Free Tier AWS EC2 `t3.micro` by applying container‑level resource limits and scheduled runtime.

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
* **Frontend (Streamlit)** provides UI, maintains per‑session state (`st.session_state`), and calls backend endpoints such as `/chat`, `/ingest`, `/summarize`.
* **Backend (FastAPI)** performs document ingestion, text chunking, embedding generation (ONNX MiniLM), stores vectors (FAISS), executes retrieval (including MMR), and routes prompts to an LLM provider (OpenAI/OpenRouter/etc.).
* All services are Dockerized and orchestrated by **Docker Compose**.

## Tech‑stack summary

* **Frontend:** Streamlit (Python)
* **Backend:** Python (FastAPI) with LangChain‑style components
* **Embeddings model:** `all‑MiniLM‑L6‑v2` (ONNX)
* **Vector store:** FAISS (local)
* **Reverse proxy:** NGINX (Alpine)
* **Container orchestration:** Docker Compose (v3.8)
* **Hosting:** AWS EC2 (Ubuntu 24.04 LTS, `t3.micro`)
* **Scheduling:** `cron` jobs for start/stop to conserve resources
* **Env management:** `.env` file (recommended to keep secrets out of source control)

---

# ✨ 3. Features

## Backend

* File & URL ingestion (PDFs, web pages)
* Text chunking + embedding generation (ONNX MiniLM)
* Vector store integration (FAISS local)
* Retriever with MMR re‑ranking and configurable `k`
* LLM integration via provider (OpenAI / OpenRouter / Cerebras)
* API endpoints: `/chat`, `/ingest`, `/summarize`, `/remove_vectors`, `/remove_all_vectors`, `/settings`, `/switch_model`, `/health`

## Frontend

* Streamlit chat UI with `st.chat_input` / `st.chat_message`
* Per‑user session isolation via `st.session_state` and `session_id`
* Upload PDFs or provide URLs to ingest
* Control temperature and embedding model mode
* Display AI responses and retrieved source attributions
* Export chat (JSON / Markdown / PDF)

## Infrastructure

* Docker Compose deployment with container‑level memory & CPU limits
* NGINX reverse proxy exposes only port **80** (optionally 443)
* Cron jobs to start/stop containers on a schedule to keep costs low

---

# 🧰 4. Technologies Used

* **Languages:** Python 3.10+
* **Frontend:** Streamlit
* **Backend:** FastAPI, LangChain‑style components
* **Embeddings model:** `all‑MiniLM‑L6‑v2` (ONNX)
* **Vector store:** FAISS (local)
* **Quantization:** Quantized ONNX model for speed & size reduction
* **LLM providers:** `deepseek‑chat‑v3‑0324` (OpenRouter) & Cerebras (`gpt‑oss‑120b`)
* **Containers:** Docker, Docker Compose (v3.8)
* **Proxy:** NGINX (Alpine)
* **Hosting:** AWS EC2 (Ubuntu 24.04 LTS)
* **Scheduling:** `cron`
* **Utilities:** `python‑dotenv`, `requests/httpx`, `PyMuPDF/pypdf`, `BeautifulSoup`

---

# 📋 5. System Requirements

**For AWS deployment (recommended minimal config):**

* Instance: `t3.micro` (Free Tier) — 2 vCPUs (burstable), 1 GiB RAM
* Storage: EBS gp3/gp2 — 30 GB (start)
* OS: Ubuntu Server 24.04 LTS (x86_64)
* Docker & Docker Compose installed

**Local development requirements:**

* Python 3.10+
* Streamlit & backend dependencies (`pip install -r requirements.txt`)
* Docker (optional for containerised local testing)

> ⚠️ Note: The `t3.micro` is memory‑limited. We use swap + container memory limits; for multi‑user or heavier workloads, upgrade the instance.

---

# 🔧 6. Installation & Setup

## Clone the repository

```bash
git clone https://github.com/your-repo/rag-chatbot.git
cd rag-chatbot
```

## Project directory layout

```
rag-chatbot/
├─ rag_pdfchatbot_backend/   # Python backend (FastAPI)
│  ├─ main.py
│  ├─ Dockerfile
│  └─ requirements.txt
├─ rag_pdfchatbot_frontend/  # Streamlit app
│  ├─ app.py
│  ├─ css.py
│  └─ requirements.txt
├─ nginx/
│  ├─ Dockerfile
│  └─ default.conf
├─ onnx_model/               # ONNX model files
├─ user_data/                # FAISS vector store (created at runtime)
├─ docker-compose.yml
└─ .env
```

## Create & populate `.env`

Copy the example and edit with your secrets:

```bash
cp .env.example .env
nano .env
```

### Required variables

```env
OPENROUTER_API_KEY=...
CEREBRAS_API_KEY=...
MODEL_NAME=deepseek-chat-v3-0324   # or any supported model
```

> **Security note:** Do **not** commit `.env` to source control. Use AWS Secrets Manager or Docker secrets for production.

---

# 🐳 7. Docker Compose – `docker-compose.yml`

The current `docker-compose.yml` builds the backend, frontend, and NGINX from the repository:

```yaml
version: '3.8'

services:
  backend:
    build: ./rag_pdfchatbot_backend
    container_name: rag-backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: always
    volumes:
      - ./onnx_model:/app/onnx_model   # model files
      - ./user_data:/app/user_data     # persistent FAISS index
    mem_limit: 600m
    cpus: 0.5

  frontend:
    build: ./rag_pdfchatbot_frontend
    container_name: rag-frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
    restart: always
    mem_limit: 350m
    cpus: 0.4

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

networks:
  default:
    driver: bridge
```

**Key points**

* **Build** is used instead of pre‑built images – the containers are built from the local `Dockerfile`s.
* **Volumes** mount the ONNX model and a persistent `user_data` directory for the FAISS index.
* **Resource limits** keep the containers within the memory budget of a `t3.micro`.

---

# 🌐 8. NGINX Configuration (`nginx/default.conf`)

```nginx
server {
    listen 80;
    server_name _;  # replace with your.domain.tld if you have one

    # Proxy traffic to the Streamlit frontend
    location / {
        proxy_pass http://frontend:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_cache_bypass $http_upgrade;
    }

    # Health endpoint proxied to the backend
    location /health {
        proxy_pass http://backend:8000/health;
        proxy_set_header Host $host;
    }
}
```

* The configuration forwards all user traffic to the Streamlit container and exposes a `/health` endpoint that forwards to the FastAPI health check.

---

# ⏰ 9. Cron Job Scheduling (Start/Stop)

To minimise AWS costs, the backend runs only during working hours (Mon‑Sat 07:00‑22:00 Berlin time). The frontend can stay up 24/7 or follow the same schedule.

```cron
# Use Berlin time for schedule
TZ=Europe/Berlin

# Start backend at 07:00 Mon‑Sat
0 7 * * 1-6 /usr/bin/docker start rag-backend

# Stop backend at 22:00 Mon‑Sat
0 22 * * 1-6 /usr/bin/docker stop rag-backend

# Ensure backend is stopped on Sunday at midnight
0 0 * * 0 /usr/bin/docker stop rag-backend

# Start frontend at 07:00 Mon‑Sat (optional – comment out to keep it always running)
0 7 * * 1-6 /usr/bin/docker start rag-frontend
```

* Use full paths (`/usr/bin/docker`) to avoid PATH issues in cron.
* Ensure the `ubuntu` user (or whichever user runs cron) has permission to run Docker commands (add to `docker` group or use `sudo`).

---

# 🔐 10. Environment Variables (Detailed)

```env
# LLM provider & keys
MODEL_NAME=deepseek-chat-v3-0324
OPENROUTER_API_KEY=...
CEREBRAS_API_KEY=...

# Host references (service names inside Docker Compose)
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

**Security note** – keep this file out of version control. In production, store secrets in AWS Secrets Manager or Parameter Store.

---

# 💾 11. Resource Management & Rationale

| Service   | Memory limit | CPU share | Rationale |
|-----------|--------------|----------|-----------|
| backend   | 600 MiB      | 0.5      | Embedding & LLM calls are the heaviest; limit prevents OOM on `t3.micro`. |
| frontend  | 350 MiB      | 0.4      | Streamlit is lightweight but needs headroom for session data. |
| nginx     | 200 MiB      | 0.2      | NGINX is very lightweight; limit is generous. |

With 1 GiB RAM on the instance and a swap file (recommended 1 GiB), the containers stay within the budget while leaving room for OS overhead.

---

# 🚀 12. Usage – Running & Accessing

## Local (non‑Docker) quick dev

```bash
# Backend
cd rag_pdfchatbot_backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd rag_pdfchatbot_frontend
pip install -r requirements.txt
streamlit run app.py
```

Set `BACKEND_HOST` in `.env` to `http://localhost:8000` for local testing.

## Containerised (recommended)

```bash
docker-compose up -d --build
```

### Verify containers

```bash
docker ps
docker logs -f rag-frontend
docker logs -f rag-backend
docker logs -f nginx-reverse-proxy
```

### Access the app

* Public URL: `http://<EC2_PUBLIC_IP>/` (NGINX forwards to Streamlit)
* Health check: `http://<EC2_PUBLIC_IP>/health`

### Restart / stop

```bash
docker-compose restart backend
docker-compose stop backend
docker-compose up -d
```

---

# 🧪 13. API / Frontend Integration (contract summary)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | `POST` | Chat with the RAG bot. |
| `/ingest` | `POST` | Upload a PDF or provide a URL to ingest. |
| `/summarize` | `POST` | Generate a summary of a PDF or URL (does **not** store vectors). |
| `/remove_vectors` | `DELETE` | Delete vectors for a specific source. |
| `/remove_all_vectors` | `DELETE` | Delete **all** vectors for the session. |
| `/settings` | `GET/POST` | Get or update session settings (e.g., temperature). |
| `/switch_model` | `POST` | Switch between quantised / regular ONNX model. |
| `/health` | `GET` | Simple health check (used by NGINX). |

All endpoints require a `session_id` query parameter (UUID‑style) to isolate user data.

---

# 📜 14. Contribution, License & Credits

* **License** – MIT (see `LICENSE` file).  
* **Contributions** – Fork the repo, create a feature branch, and open a Pull Request.  
* **Credits** – Built with Streamlit, FastAPI, LangChain‑style components, Docker, and NGINX. Hosted on AWS EC2.

---

# ✅ 15. Quick Deploy Checklist

1. Launch an AWS `t3.micro` instance (Ubuntu 24.04) and open ports 22 (SSH) and 80 (HTTP).  
2. SSH into the instance and install Docker & Docker Compose.  
3. Clone the repository into `/home/ubuntu/rag-chatbot`.  
4. Copy `.env.example` → `.env` and fill in API keys.  
5. (Recommended) Create a 1 GiB swap file to avoid OOM.  
6. Ensure `nginx/default.conf` and `docker-compose.yml` are present.  
7. Run `docker-compose up -d --build`.  
8. Add the cron entries from section 9.  
9. Verify the site at `http://<EC2_PUBLIC_IP>/`.  
10. (Optional) Add TLS via Let's Encrypt and harden security groups.  
11. Monitor logs; adjust `mem_limit`/`cpus` if needed.

---

# 📚 16. Further Enhancements (next steps)

* **Authentication** – JWT or API‑key based auth for the backend.  
* **Scalable vector store** – Replace local FAISS with Qdrant or Pinecone for multi‑instance scaling.  
* **Observability** – Add Prometheus + Grafana dashboards; ship logs to CloudWatch.  
* **CI/CD** – GitHub Actions to build Docker images and deploy automatically to EC2.  
* **TLS** – Automate HTTPS with Certbot (Let's Encrypt) behind NGINX.

---

## 🙋 Author & Contact

**Author:** Suraj Varma  
**Email:** sv3677781@gmail.com  
**GitHub:** [@suraj5424](https://github.com/suraj5424)  
**LinkedIn:** [Suraj Varma](https://www.linkedin.com/in/suraj5424/)  
**Portfolio:** [suraj‑varma.vercel.app](https://suraj-varma.vercel.app/)

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## ⭐ Acknowledgments

* Streamlit – UI framework  
* FastAPI – backend framework  
* Docker – containerisation  
* NGINX – reverse proxy  
* AWS EC2 – hosting

---

## 🙏 Support

If you find this project useful, please give it a ⭐ on GitHub!
