# EXPLAINER.md

## Overview

This project implements a minimal **Payout Engine** similar to real-world payment systems like Playto Pay.

The system allows:

* Merchants to maintain balances via a ledger system
* Request payouts with idempotency
* Process payouts asynchronously using Celery
* Handle retries, failures, and concurrency safely
* View real-time updates via WebSockets

The architecture follows:

Frontend (React + Vercel)
→ Backend (Django + DRF on Azure)
→ Redis (Queue + Channels)
→ Celery Worker (Background processing)

---

# 1. The Ledger

### Balance Calculation Query

```python
result = LedgerEntry.objects.filter(merchant_id=merchant_id).aggregate(
    balance=Sum(
        Case(
            When(type="CREDIT", then=F("amount_paise")),
            When(type="DEBIT", then=-F("amount_paise")),
            When(type="HOLD", then=-F("amount_paise")),
            When(type="RELEASE", then=F("amount_paise")),
            output_field=BigIntegerField()
        )
    )
)
```

### Explanation

* All money is stored as **BigIntegerField in paise**
* No floating point arithmetic is used
* Balance is computed at **database level using aggregation**
* Ledger types:

  * CREDIT → money added
  * DEBIT → money withdrawn
  * HOLD → temporarily blocked funds
  * RELEASE → funds returned

### Why this model?

This ensures:

* Full auditability
* No mutation of balance directly
* Ledger becomes the single source of truth
* Guarantees consistency:
  **credits - debits - holds + releases = balance**

---

# 2. The Lock (Concurrency Control)

### Code

```python
merchant = Merchant.objects.select_for_update().get(id=merchant.id)
```

### Explanation

* Uses **database row-level locking**
* Prevents race conditions during payout creation

### Problem Solved

Scenario:

* Merchant balance = ₹100
* Two requests for ₹60 come simultaneously

Without locking:
→ Both succeed ❌

With locking:
→ One succeeds, one fails ✅

### Primitive Used

* PostgreSQL **row-level lock (SELECT FOR UPDATE)**

---

# 3. The Idempotency

### Implementation

* Idempotency key is passed via header:

```text
Idempotency-Key: <UUID>
```

* Stored in DB with:

```python
unique_together = ("merchant", "idempotency_key")
```

### Flow

1. Request comes with key
2. System checks if key exists
3. If exists → return same response
4. Else → process payout

### Edge Case Handling

If first request is in-flight:

* Second request hits DB constraint
* Returns existing payout safely

### Why this matters

* Prevents duplicate payouts
* Handles network retries safely
* Guarantees API correctness

---

# 4. The State Machine

### Valid Transitions

```
PENDING → PROCESSING → COMPLETED
PENDING → PROCESSING → FAILED
```

### Code Enforcement

```python
if payout.status not in ["PENDING", "PROCESSING"]:
    if payout.status == "FAILED":
        payout.status = "PENDING"
    else:
        return
```

### Invalid Transitions Blocked

* COMPLETED → anything ❌
* FAILED → COMPLETED ❌
* Backward transitions ❌

### Atomicity

* State update + ledger update happen inside:

```python
with transaction.atomic():
```

This ensures:

* No partial updates
* No inconsistent states

---

# 5. Retry Logic

### Implementation

* Celery retries with:

```python
@shared_task(bind=True, max_retries=3)
```

* Timeout handling:

```python
if payout.created_at < timezone.now() - timedelta(seconds=60):
    payout.status = "FAILED"
```

### Additional Retry Task

```python
retry_stuck_payouts()
```

* Detects stuck PROCESSING payouts
* Marks them FAILED
* Returns funds via RELEASE entry

### Behavior

| Case          | Result                  |
| ------------- | ----------------------- |
| Success (70%) | COMPLETED               |
| Failure (20%) | FAILED + funds returned |
| Hang (10%)    | Retried → then FAILED   |

---

# 6. Money Integrity

Ensured via:

* No float usage
* Only integer paise values
* DB-level aggregation
* Atomic ledger updates

Invariant maintained:

```
Sum(CREDIT) - Sum(DEBIT) - Sum(HOLD) + Sum(RELEASE) = Balance
```

---

# 7. Real-time Updates

### Implementation

* Django Channels + Redis

```python
async_to_sync(channel_layer.group_send)
```

### Events

* PROCESSING
* COMPLETED
* FAILED

### Frontend

* WebSocket listener updates UI instantly

---

# 8. Deployment Architecture

* Backend deployed on Azure Container Instances
* Redis deployed separately
* Celery worker deployed as independent container
* Frontend deployed on Vercel

### Challenge Faced

Mixed Content Error:

* HTTPS frontend cannot call HTTP backend

### Solution

Used Vercel proxy:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "http://backend/api/v1/:path*"
    }
  ]
}
```

---

# 9. AI Audit

### Issue Found

AI initially suggested:

```python
balance = sum(entries)
```

### Problem

* Loads data into Python
* Not atomic
* Breaks under concurrency

### Fix Applied

Used DB aggregation:

```python
Sum + Case + F expressions
```

### Learning

* Never trust AI blindly for financial logic
* Always enforce DB-level correctness

---

# 10. Final System Behavior

* Concurrent payouts handled safely
* Duplicate requests prevented
* Funds never lost or duplicated
* Background processing ensures scalability
* Real-time updates improve UX

---

# Conclusion

This system mimics real-world payout engines by focusing on:

* Data integrity
* Concurrency safety
* Idempotent APIs
* Async processing
* Clear state transitions

The design prioritizes correctness over complexity, which is critical for money-moving systems.

---
