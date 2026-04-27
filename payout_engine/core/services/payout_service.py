from django.db import transaction
from django.db.models import Sum
from core.models import Merchant, LedgerEntry, Payout
from core.tasks import process_payout


def get_balance(merchant):
    result = LedgerEntry.objects.filter(merchant=merchant).aggregate(
        total=Sum('amount_paise')
    )
    return result['total'] or 0


def create_payout(merchant_id, amount_paise, idempotency_key):
    with transaction.atomic():

        # 🔒 LOCK merchant row
        merchant = Merchant.objects.select_for_update().get(id=merchant_id)

        # ✅ Idempotency
        existing = Payout.objects.filter(
            merchant=merchant,
            idempotency_key=idempotency_key
        ).first()

        if existing:
            return existing

        # 💰 Balance check
        balance = get_balance(merchant)
        if balance < amount_paise:
            raise Exception("Insufficient balance")

        # 🧾 Create payout
        payout = Payout.objects.create(
            merchant=merchant,
            amount_paise=amount_paise,
            status=Payout.STATUS_PENDING,
            idempotency_key=idempotency_key
        )

        # 🧾 Hold funds
        LedgerEntry.objects.create(
            merchant=merchant,
            payout=payout,
            amount_paise=-amount_paise,
            entry_type=LedgerEntry.TYPE_HOLD
        )

        # ✅ Trigger task ONLY AFTER COMMIT
        transaction.on_commit(lambda: process_payout.delay(payout.id))

        return payout