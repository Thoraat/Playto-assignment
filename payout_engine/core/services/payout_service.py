# from django.db import transaction
# from django.db.models import Sum
# from core.models import Merchant, LedgerEntry, Payout
# from core.tasks import process_payout


# def get_balance(merchant):
#     result = LedgerEntry.objects.filter(merchant=merchant).aggregate(
#         total=Sum('amount_paise')
#     )
#     return result['total'] or 0


# def create_payout(merchant_id, amount_paise, idempotency_key):
#     with transaction.atomic():

#         # 🔒 LOCK merchant row
#         merchant = Merchant.objects.select_for_update().get(id=merchant_id)

#         # ✅ Idempotency
#         existing = Payout.objects.filter(
#             merchant=merchant,
#             idempotency_key=idempotency_key
#         ).first()

#         if existing:
#             return existing

#         # 💰 Balance check
#         balance = get_balance(merchant)
#         if balance < amount_paise:
#             raise Exception("Insufficient balance")

#         # 🧾 Create payout
#         payout = Payout.objects.create(
#             merchant=merchant,
#             amount_paise=amount_paise,
#             status=Payout.STATUS_PENDING,
#             idempotency_key=idempotency_key
#         )

#         # 🧾 Hold funds
#         LedgerEntry.objects.create(
#             merchant=merchant,
#             payout=payout,
#             amount_paise=-amount_paise,
#             entry_type=LedgerEntry.TYPE_HOLD
#         )

#         # ✅ Trigger task ONLY AFTER COMMIT
#         transaction.on_commit(lambda: process_payout.delay(payout.id))

#         return payout

from core.models import Merchant, Payout, LedgerEntry
from django.db import transaction


def get_balance(merchant):
    credits = merchant.ledger_entries.filter(entry_type="credit").aggregate(
        total=models.Sum("amount_paise")
    )["total"] or 0

    holds = merchant.ledger_entries.filter(entry_type="payout_hold").aggregate(
        total=models.Sum("amount_paise")
    )["total"] or 0

    payouts = merchant.ledger_entries.filter(entry_type="payout").aggregate(
        total=models.Sum("amount_paise")
    )["total"] or 0

    refunds = merchant.ledger_entries.filter(entry_type="refund").aggregate(
        total=models.Sum("amount_paise")
    )["total"] or 0

    return credits + refunds - holds - payouts


from django.db import models


@transaction.atomic
def create_payout(merchant_id, amount_paise, idempotency_key):
    merchant = Merchant.objects.get(id=merchant_id)

    # Idempotency check
    existing = Payout.objects.filter(
        merchant=merchant,
        idempotency_key=idempotency_key
    ).first()

    if existing:
        return existing

    # Check balance
    balance = get_balance(merchant)
    if balance < amount_paise:
        raise Exception("Insufficient balance")

    # Create payout
    payout = Payout.objects.create(
        merchant=merchant,
        amount_paise=amount_paise,
        idempotency_key=idempotency_key,
        status="processing"
    )

    # HOLD money
    LedgerEntry.objects.create(
        merchant=merchant,
        payout=payout,
        amount_paise=amount_paise,
        entry_type="payout_hold"
    )

    # Simulate success (no Celery)
    payout.status = "completed"
    payout.save()

    # Deduct final payout
    LedgerEntry.objects.create(
        merchant=merchant,
        payout=payout,
        amount_paise=amount_paise,
        entry_type="payout"
    )

    return payout