from django.db.models import Sum, Case, When, F, BigIntegerField
from core.models import LedgerEntry

def get_balance(merchant_id):
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
    return result["balance"] or 0