# Frontend – Payout Dashboard

React + Vite UI for interacting with the payout system.

---

## ⚙️ Tech Stack

* React
* Vite
* Axios
* Tailwind CSS

---

## 🚀 Setup

```bash
npm install
npm run dev
```

---

## 🌐 Runs on

```
http://localhost:5173
```

---

## 🔗 Backend Connection

Make sure backend is running at:

```
http://127.0.0.1:8000
```

---

## ✨ Features

* Create payout
* View payout status
* View merchant balance
* View payout history

---

## 🧠 How It Works

* Sends POST request to create payout
* Generates idempotency key per request
* Polls backend for status updates
* Displays live results

---

## 📦 API Calls

```js
POST /api/v1/payouts
GET  /api/v1/payouts/{id}
GET  /api/v1/merchant/{id}/balance
GET  /api/v1/merchant/{id}/payouts
```

---

## ⚠️ Common Issues

### CORS Error

Fix in backend settings:

```python
CORS_ALLOW_ALL_ORIGINS = True
```

---

### Backend Not Running

Make sure Django server is active:

```bash
python manage.py runserver
```

---

## 🎯 Purpose

This frontend is a simple UI to demonstrate:

* Payout creation
* Status tracking
* Ledger-based balance system

---

## 👨‍💻 Author

Amosh Singh
