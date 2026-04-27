from django.db.models import Sum
from core.models import LedgerEntry


def repair_ledger():
    fixes = []

    holds = LedgerEntry.objects.filter(type="HOLD")

    for h in holds:
        released = LedgerEntry.objects.filter(
            reference_id=h.reference_id,
            type="RELEASE"
        ).aggregate(total=Sum("amount_paise"))["total"] or 0

        if released < h.amount_paise:
            missing = h.amount_paise - released

            LedgerEntry.objects.create(
                merchant=h.merchant,
                type="RELEASE",
                amount_paise=missing,
                reference_id=h.reference_id
            )

            fixes.append({
                "payout_id": str(h.reference_id),
                "fixed_release": missing
            })

    return fixes