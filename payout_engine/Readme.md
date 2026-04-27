# Backend – Payout Engine

Django-based backend for handling payout logic.

---

## ⚙️ Tech Stack

* Django
* Django REST Framework
* PostgreSQL
* Celery
* Redis

---

## 🚀 Setup

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🔑 Core Concepts

### Ledger System

* All transactions stored as entries
* Balance = sum of entries

---

### Idempotency

* Prevents duplicate payouts
* Uses unique UUID key per request

---

### Concurrency Safety

* Uses `select_for_update()`
* Prevents double spending

---

### Async Processing

* Celery processes payouts
* Simulates success/failure

---

## 📡 API Endpoints

| Endpoint                 | Method | Description       |
| ------------------------ | ------ | ----------------- |
| `/payouts`               | POST   | Create payout     |
| `/payouts/{id}`          | GET    | Get payout status |
| `/merchant/{id}/balance` | GET    | Get balance       |
| `/merchant/{id}/payouts` | GET    | List payouts      |

---

## 🧠 Flow

1. Lock merchant row
2. Check balance
3. Create payout
4. Hold funds (ledger)
5. Trigger async task
6. Update status

---

## 🧪 Run Celery

```bash
celery -A payout_engine worker -l info
```

---

## ⚠️ Notes

* Designed for correctness, not production scale
* Focus on financial system concepts
