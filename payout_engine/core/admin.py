from django.contrib import admin
from .models import Merchant, Payout, LedgerEntry
from django.db import models


class MerchantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "balance")

    def balance(self, obj):
        credits = obj.ledger_entries.filter(entry_type="credit").aggregate(
            total=models.Sum("amount_paise")
        )["total"] or 0

        holds = obj.ledger_entries.filter(entry_type="payout_hold").aggregate(
            total=models.Sum("amount_paise")
        )["total"] or 0

        payouts = obj.ledger_entries.filter(entry_type="payout").aggregate(
            total=models.Sum("amount_paise")
        )["total"] or 0

        refunds = obj.ledger_entries.filter(entry_type="refund").aggregate(
            total=models.Sum("amount_paise")
        )["total"] or 0

        return credits + refunds - holds - payouts

    balance.short_description = "Balance"


class PayoutAdmin(admin.ModelAdmin):
    list_display = ("id", "merchant", "amount_paise", "status", "retry_count", "created_at")
    list_filter = ("status",)
    search_fields = ("merchant__name",)


class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "merchant", "entry_type", "amount_paise", "created_at")
    list_filter = ("entry_type",)
    search_fields = ("merchant__name",)


admin.site.register(Merchant, MerchantAdmin)
admin.site.register(Payout, PayoutAdmin)
admin.site.register(LedgerEntry, LedgerEntryAdmin)