from celery import shared_task
import random
import time

from django.db import transaction
from core.models import Payout, LedgerEntry


@shared_task(bind=True, max_retries=3)
def process_payout(self, payout_id):
    """
    Moves payout:
    pending -> processing -> completed/failed
    Retries if 'stuck'
    """

    try:
        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(id=payout_id)

            # ❌ Block illegal transitions
            if payout.status != Payout.STATUS_PENDING:
                return

            # 👉 Move to processing
            payout.status = Payout.STATUS_PROCESSING
            payout.save()

        # ⏳ Simulate bank delay (outside transaction)
        time.sleep(2)

        outcome = random.random()

        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(id=payout_id)

            # Safety: only process if still processing
            if payout.status != Payout.STATUS_PROCESSING:
                return

            # ✅ 70% success
            if outcome < 0.7:
                payout.status = Payout.STATUS_COMPLETED
                payout.save()
                return

            # ❌ 20% failure → refund
            elif outcome < 0.9:
                payout.status = Payout.STATUS_FAILED
                payout.save()

                # 💰 Refund funds
                LedgerEntry.objects.create(
                    merchant=payout.merchant,
                    payout=payout,
                    amount_paise=payout.amount_paise,
                    entry_type=LedgerEntry.TYPE_REFUND
                )
                return

            # ⏳ 10% stuck → retry
            else:
                payout.retry_count += 1
                payout.save()

                if payout.retry_count >= 3:
                    # fail after retries
                    payout.status = Payout.STATUS_FAILED
                    payout.save()

                    LedgerEntry.objects.create(
                        merchant=payout.merchant,
                        payout=payout,
                        amount_paise=payout.amount_paise,
                        entry_type=LedgerEntry.TYPE_REFUND
                    )
                    return

                raise self.retry(countdown=5 * (2 ** payout.retry_count))

    except Exception as e:
        raise self.retry(exc=e, countdown=5)