from django.db.models import Sum
from core.models import LedgerEntry, Payout


def audit_ledger():
    issues = []

    holds = LedgerEntry.objects.filter(type="HOLD")

    for h in holds:
        released = LedgerEntry.objects.filter(
            reference_id=h.reference_id,
            type="RELEASE"
        ).aggregate(total=Sum("amount_paise"))["total"] or 0

        if released < h.amount_paise:
            issues.append({
                "type": "MISSING_RELEASE",
                "payout_id": str(h.reference_id),
                "hold": h.amount_paise,
                "released": released,
                "missing": h.amount_paise - released
            })

        elif released > h.amount_paise:
            issues.append({
                "type": "OVER_RELEASE",
                "payout_id": str(h.reference_id),
                "hold": h.amount_paise,
                "released": released
            })

    # 🔍 Check payouts without ledger entries
    payouts = Payout.objects.all()

    for p in payouts:
        hold_exists = LedgerEntry.objects.filter(
            reference_id=p.id,
            type="HOLD"
        ).exists()

        if p.status in ["PENDING", "PROCESSING"] and not hold_exists:
            issues.append({
                "type": "MISSING_HOLD",
                "payout_id": str(p.id)
            })

    return issues