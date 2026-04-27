from django.db import models
import uuid


class Merchant(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Payout(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    )

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="payouts"
    )
    amount_paise = models.BigIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )

    idempotency_key = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    retry_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('merchant', 'idempotency_key')

    def __str__(self):
        return f"{self.merchant.name} - {self.amount_paise} - {self.status}"

    def clean(self):
        if self.amount_paise <= 0:
            raise ValueError("Amount must be positive")


class LedgerEntry(models.Model):
    TYPE_CREDIT = 'credit'
    TYPE_HOLD = 'payout_hold'
    TYPE_PAYOUT = 'payout'
    TYPE_REFUND = 'refund'

    ENTRY_TYPES = (
        (TYPE_CREDIT, 'Credit'),
        (TYPE_HOLD, 'Payout Hold'),
        (TYPE_PAYOUT, 'Payout'),
        (TYPE_REFUND, 'Refund'),
    )

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="ledger_entries"
    )

    payout = models.ForeignKey(
        Payout,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ledger_entries"
    )

    amount_paise = models.BigIntegerField()
    entry_type = models.CharField(
        max_length=20,
        choices=ENTRY_TYPES,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.merchant.name} - {self.entry_type} - {self.amount_paise}"