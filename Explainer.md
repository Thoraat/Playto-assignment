# Payout Engine – Explainer

---

## 1. The Ledger

### Balance Calculation

```python
def get_balance(merchant):
    result = LedgerEntry.objects.filter(merchant=merchant).aggregate(
        total=Sum('amount_paise')
    )
    return result['total'] or 0
```

### Design

* Credits → positive values
* Debits / holds → negative values

Why:

* No mutable balance field (avoids race conditions)
* Full audit trail
* Matches real financial systems

---

## 2. The Lock

### Code

```python
with transaction.atomic():
    merchant = Merchant.objects.select_for_update().get(id=merchant_id)
```

### Explanation

* Uses **row-level locking (SELECT FOR UPDATE)**
* Prevents concurrent transactions from modifying the same merchant balance

Without this:
→ double spend is possible

---

## 3. The Idempotency

### Code

```python
existing = Payout.objects.filter(
    merchant=merchant,
    idempotency_key=idempotency_key
).first()

if existing:
    return existing
```

### Behavior

If duplicate request arrives:

* First request acquires lock
* Second waits
* After commit → second sees existing payout
* Returns same result

Ensures:

* No duplicate payouts
* Safe retries

---

## 4. The State Machine

### Code

```python
if payout.status != Payout.STATUS_PENDING:
    return
```

### Flow

```text
pending → processing → completed / failed
```

Prevents:

* failed → completed
* re-processing completed payouts

---

## 5. The AI Audit

### ❌ AI Suggested (Wrong)

```python
merchant = Merchant.objects.get(id=merchant_id)
balance = get_balance(merchant)

if balance >= amount:
    Payout.objects.create(...)
```

### Problem

* No locking
* Race condition
* Double spending possible

---

### ✅ Fixed Version

```python
with transaction.atomic():
    merchant = Merchant.objects.select_for_update().get(id=merchant_id)

    balance = get_balance(merchant)

    if balance < amount:
        raise Exception("Insufficient balance")

    payout = Payout.objects.create(...)
```

### Fix

* Added transaction
* Added row-level lock
* Safe balance check

---

## 6. System Architecture

```text
Frontend → Django API → Service Layer → Database → Celery → Redis
```

---

## 7. Payout Flow

```text
1. User creates payout
2. Backend locks merchant row
3. Balance checked via ledger
4. Payout created (pending)
5. Ledger hold entry created
6. Transaction committed
7. Celery processes payout
8. Status → completed / failed
9. Frontend polls status
```

---

## 8. Concurrency Handling

```text
Request A → locks row
Request B → waits

A commits → B resumes
B sees updated state → no duplicate payout
```

---

## 9. Ledger Example

```text
+10000 (credit)
-5000  (hold)

Balance = 5000
```

---

## 10. Key Guarantees

* No double spending → DB locks
* No duplicate payouts → idempotency
* Accurate balance → ledger model
* Scalable processing → Celery

---

## 11. Conclusion

This system demonstrates a production-style payout architecture with:

* Strong consistency guarantees
* Safe concurrency handling
* Async processing
* Real-world failure simulation

---
                 ┌──────────────────────┐
                 │   Frontend (React)   │
                 │  - Create payout     │
                 │  - View balance      │
                 │  - Poll status       │
                 └─────────┬────────────┘
                           │ HTTP API
                           ▼
              ┌──────────────────────────┐
              │   Django REST API        │
              │  (Views + Serializers)  │
              └─────────┬───────────────┘
                        │
                        ▼
           ┌──────────────────────────────┐
           │   Service Layer              │
           │  - Idempotency check        │
           │  - Balance calculation      │
           │  - Row locking              │
           └─────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │   PostgreSQL Database         │
         │  - Merchant                  │
         │  - LedgerEntry               │
         │  - Payout                   │
         └─────────┬────────────────────┘
                   │
                   ▼
         ┌───────────────────────────────┐
         │   Celery Worker               │
         │  - Async processing           │
         │  - Retry logic                │
         │  - State transitions          │
         └─────────┬────────────────────┘
                   │
                   ▼
         ┌───────────────────────────────┐
         │   Redis (Broker)              │
         │  - Task queue                │
         └───────────────────────────────┘