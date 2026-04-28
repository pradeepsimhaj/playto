# Playto Payout Engine 🚀

A minimal **payout engine system** simulating real-world payment infrastructure with strong guarantees around:

* Money integrity
* Concurrency safety
* Idempotent APIs
* Async background processing
* Real-time updates

---

# 📦 Project Structure

```id="gq3c2n"
playto/
│
├── playto-backend/     # Django + DRF + Celery + Redis
├── playto-frontend/    # React + Tailwind (Vite)
└── README.md
```

---

# ⚙️ Tech Stack

### Backend

* Django + DRF
* PostgreSQL
* Celery (background jobs)
* Redis (queue + channels)
* Django Channels (WebSockets)

### Frontend

* React (Vite)
* Tailwind CSS
* Axios

### Deployment

* Backend → Azure Container Instances
* Frontend → Vercel

---

# 🚀 Getting Started (Local Setup)

---

## 🔹 1. Clone Repository

```bash id="5fj3x7"
git clone <your-repo-url>
cd playto
```

---

# 🖥️ BACKEND SETUP

---

## 🔹 2. Navigate to Backend

```bash id="u38o1l"
cd playto-backend
```

---

## 🔹 3. Create Virtual Environment

```bash id="4b6r9v"
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

---

## 🔹 4. Install Dependencies

```bash id="6r9yvl"
pip install -r requirements.txt
```

---

## 🔹 5. Setup Environment Variables

Create `.env`:

```env id="9jv61v"
DEBUG=True
SECRET_KEY=your-secret
DATABASE_URL=postgres://...
REDIS_URL=redis://127.0.0.1:6379/0
```

---

## 🔹 6. Run Migrations

```bash id="nkl1tf"
python manage.py migrate
```

---

## 🔹 7. Seed Data (Optional)

```bash id="y1h7xk"
python manage.py shell
```

Create merchants manually or via script.

---

## 🔹 8. Run Django Server

```bash id="5t0p2k"
python manage.py runserver
```

---

## 🔹 9. Run Redis (Local)

```bash id="m1x3co"
docker run -p 6379:6379 redis
```

---

## 🔹 10. Run Celery Worker

```bash id="m5t6f3"
celery -A payout_engine worker --loglevel=info
```

---

## 🔹 11. Run Celery Beat (Optional)

```bash id="6p0w9f"
celery -A payout_engine beat --loglevel=info
```

---

# 🌐 FRONTEND SETUP

---

## 🔹 1. Navigate to Frontend

```bash id="sk9c8n"
cd ../playto-frontend
```

---

## 🔹 2. Install Dependencies

```bash id="kz7n3p"
npm install
```

---

## 🔹 3. Environment Setup

Create `.env`:

```env id="jv9k2x"
VITE_BACKEND_URL=http://127.0.0.1:8000
```

---

## 🔹 4. Run Frontend

```bash id="4f0p9k"
npm run dev
```

---

# 🐳 DOCKER SETUP (FULL STACK)

---

## 🔹 Build Image

```bash id="v8d2l1"
docker build -t payout-app ./playto-backend
```

---

## 🔹 Run Redis

```bash id="x1n0l7"
docker run -d -p 6379:6379 redis
```

---

## 🔹 Run Django (ASGI)

```bash id="b1k3y9"
docker run -p 8000:8000 payout-app python -m daphne -b 0.0.0.0 -p 8000 payout_engine.asgi:application
```

---

## 🔹 Run Celery

```bash id="p0k8v6"
docker run payout-app celery -A payout_engine worker --loglevel=info
```

---

# 🌍 Deployment

---

## Backend (Azure)

* Docker image pushed to Azure Container Registry
* Deployed via Azure Container Instances
* Redis deployed separately
* Celery worker deployed as another container

---

## Frontend (Vercel)

* Deployed via GitHub integration
* Uses proxy to avoid mixed content issues

---

# 🔁 Architecture Diagram

```id="d5z8n2"
Frontend (Vercel - HTTPS)
        ↓
Vercel Proxy (/api)
        ↓
Backend (Django - Azure)
        ↓
Redis (Queue + Channels)
        ↓
Celery Worker (Async Processing)
```

---

# 🔄 Payout Lifecycle (Sequence)

```id="o1c9e3"
User → API → Create Payout (PENDING)
          ↓
        HOLD funds
          ↓
      Celery Worker
          ↓
   PROCESSING → (random outcome)
          ↓
  COMPLETED → DEBIT
      OR
  FAILED → RELEASE
```

---

# 🧪 Test Explanation

---

## ✅ Concurrency Test

Scenario:

* Merchant balance = ₹100
* Two payout requests of ₹60 sent simultaneously

Expected:

* Only one succeeds
* Second fails

Solution:

* Used `select_for_update()` (DB row lock)

---

## ✅ Idempotency Test

Scenario:

* Same request sent twice with same Idempotency-Key

Expected:

* Only one payout created
* Same response returned

Solution:

* Unique constraint on `(merchant, idempotency_key)`

---

# 🔐 Key Features Implemented

* Ledger-based accounting system
* Strong money integrity (no floats)
* Concurrency-safe payouts
* Idempotent API design
* Async processing via Celery
* Retry + timeout handling
* Real-time updates via WebSockets
* Deployment with Docker + Azure + Vercel

---

# ⚠️ Known Limitations

* No authentication layer (for simplicity)
* Redis not secured (demo purpose)
* HTTPS not enabled for backend (handled via proxy)

---

# 📌 Conclusion

This project focuses on **correctness over complexity**, simulating real-world payment systems with:

* Safe concurrency handling
* Reliable state transitions
* Accurate ledger accounting
* Scalable async processing

---

# 👨‍💻 Author: Pradeep

Built as part of Playto Founding Engineer Challenge.

---
