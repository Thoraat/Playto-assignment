# 💸 Payout Engine System

A simplified **fintech-style payout system** built with:

* Django (Backend)
* PostgreSQL (Database)
* Celery + Redis (Async processing)
* React + Vite (Frontend)

---

## 🚀 Features

* Create payouts safely
* Idempotent API (no duplicate payouts)
* Ledger-based balance system
* Concurrency-safe (no double spending)
* Async payout processing
* Retry + failure simulation
* Real-time status tracking

---

## 🧠 Key Concepts Implemented

* Ledger system (credits/debits)
* Row-level locking (`SELECT FOR UPDATE`)
* Idempotency keys
* State machine (pending → processing → completed/failed)
* Async task queue (Celery)

---

## 📄 Detailed Explanation

👉 See [EXPLAINER.md](./EXPLAINER.md)

---

## 🏗️ Project Structure

```bash
PLAYTO/
├── payout_engine/        # Django backend
├── playto-frontend/     # React frontend
├── EXPLAINER.md
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Backend

```bash
cd payout_engine
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate (Windows)

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

### 2. Redis + Celery

Start Redis:

```bash
redis-server
```

Start Celery worker:

```bash
celery -A payout_engine worker -l info
```

---

### 3. Frontend

```bash
cd playto-frontend
npm install
npm run dev
```

---

## 🌐 API Endpoints

### Create Payout

```
POST /api/v1/payouts
```

### Get Payout Status

```
GET /api/v1/payouts/{id}
```

### Get Merchant Balance

```
GET /api/v1/merchant/{id}/balance
```

### Get Payout History

```
GET /api/v1/merchant/{id}/payouts
```

---

## 🧪 Example Request

```json
{
  "merchant_id": 9,
  "amount_paise": 5000,
  "bank_account_id": 1
}
```

Header:

```
Idempotency-Key: <uuid>
```

---

## 🎯 Highlights

* Prevents race conditions
* Prevents duplicate payouts
* Fully auditable ledger system
* Scalable async architecture

---

## ⚠️ Note

This is a **simulation system**, not real banking integration.

---

## 👨‍💻 Author

Amosh Singh
