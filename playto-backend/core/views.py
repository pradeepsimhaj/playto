from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Case, When, F, BigIntegerField

from core.models import Merchant, LedgerEntry, Payout, BankAccount, Webhook
from core.serializers import (
    MerchantSerializer,
    LedgerSerializer,
    PayoutSerializer,
    BankAccountSerializer,
    CreatePayoutSerializer,
    WebhookSerializer
)

from core.services.payout import create_payout
from core.services.idempotency import get_existing, save_response

from core.services.audit import audit_ledger
from core.services.repair import repair_ledger

# 🔹 Helper function for balance
def get_balances(merchant_id):
    entries = LedgerEntry.objects.filter(merchant_id=merchant_id)

    # ✅ AVAILABLE BALANCE
    available = entries.aggregate(
        balance=Sum(
            Case(
                When(type="CREDIT", then=F("amount_paise")),
                When(type="DEBIT", then=-F("amount_paise")),
                When(type="RELEASE", then=F("amount_paise")),
                When(type="HOLD", then=-F("amount_paise")),
                output_field=BigIntegerField()
            )
        )
    )["balance"] or 0

    # 🔥 CORRECT HELD (per payout)
    holds = LedgerEntry.objects.filter(
        merchant_id=merchant_id,
        type="HOLD"
    )

    held = 0

    for h in holds:
        released = LedgerEntry.objects.filter(
            reference_id=h.reference_id,
            type="RELEASE"
        ).aggregate(total=Sum("amount_paise"))["total"] or 0

        remaining = h.amount_paise - released

        if remaining > 0:
            held += remaining

    return available, held

# ✅ 1. Merchants List
class MerchantListView(APIView):
    def get(self, request):
        merchants = Merchant.objects.all()
        return Response(MerchantSerializer(merchants, many=True).data)


# ✅ 2. Merchant Detail
class MerchantDetailView(APIView):
    def get(self, request, merchant_id):
        merchant = Merchant.objects.get(id=merchant_id)

        available, held = get_balances(merchant_id)

        # ✅ Pagination params
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 5))

        start = (page - 1) * limit
        end = start + limit

        all_transactions = LedgerEntry.objects.filter(
            merchant=merchant
        ).order_by("-created_at")

        total = all_transactions.count()

        transactions = all_transactions[start:end]

        return Response({
            "merchant": MerchantSerializer(merchant).data,
            "available_balance": available,
            "held_balance": held,
            "recent_transactions": LedgerSerializer(transactions, many=True).data,

            # ✅ pagination info
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "has_next": end < total,
                "has_prev": page > 1
            }
        })


# ✅ 3. Create Payout
class CreatePayoutView(APIView):

    def post(self, request):
        serializer = CreatePayoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bank_account = BankAccount.objects.get(
            id=serializer.validated_data["bank_account_id"]
        )

        merchant = bank_account.merchant

        key = request.headers.get("Idempotency-Key")

        existing = get_existing(merchant, key)
        if existing:
            return Response(existing.response_body, status=existing.status_code)

        payout, balance = create_payout(
            merchant,
            serializer.validated_data["amount_paise"],
            bank_account.id,
            key
        )

        response = {
            "id": str(payout.id),
            "status": payout.status,
            "available_balance": balance,
            "merchant_name": merchant.name
        }

        save_response(merchant, key, response, 201)

        return Response(response, status=201)
    

# ✅ 4. List Payouts
class PayoutListView(APIView):
    def get(self, request):
        merchant_id = request.GET.get("merchant_id")
        payouts = Payout.objects.all()

        if merchant_id:
            payouts = payouts.filter(merchant_id=merchant_id)

        payouts = payouts.order_by("-created_at")

        return Response(PayoutSerializer(payouts, many=True).data)


# ✅ 5. Payout Detail
class PayoutDetailView(APIView):
    def get(self, request, payout_id):
        payout = Payout.objects.get(id=payout_id)
        return Response(PayoutSerializer(payout).data)


# ✅ 6. Ledger
class LedgerView(APIView):
    def get(self, request):
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))

        start = (page - 1) * limit
        end = start + limit

        entries = LedgerEntry.objects.all().order_by("-created_at")

        total = entries.count()

        data = entries[start:end]

        return Response({
            "results": LedgerSerializer(data, many=True).data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "has_next": end < total,
                "has_prev": page > 1
            }
        })


# ✅ 7. Bank Accounts
class BankAccountListView(APIView):
    def get(self, request):
        accounts = BankAccount.objects.all()
        return Response(BankAccountSerializer(accounts, many=True).data)
    

# ✅ 8. Webhooks
class WebhookCreateView(APIView):
    def post(self, request):
        merchant = Merchant.objects.first()

        serializer = WebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        webhook = serializer.save(merchant=merchant)

        return Response(WebhookSerializer(webhook).data, status=201)
    

# 🔍 Audit Ledger
class LedgerAuditView(APIView):
    def get(self, request):
        issues = audit_ledger()
        return Response({
            "total_issues": len(issues),
            "issues": issues
        })


# 🔧 Repair Ledger
class LedgerRepairView(APIView):
    def post(self, request):
        fixes = repair_ledger()
        return Response({
            "fixed_count": len(fixes),
            "fixes": fixes
        })
    


class RetryPayoutView(APIView):
    def post(self, request, payout_id):
        from core.tasks import process_payout

        try:
            payout = Payout.objects.get(id=payout_id)

            # 🔥 Reset payout for retry
            payout.status = "PENDING"
            payout.save()

            process_payout.delay(str(payout.id))

            return Response({
                "message": "Retry started",
                "id": str(payout.id),
                "status": payout.status
            }, status=200)

        except Payout.DoesNotExist:
            return Response({"error": "Payout not found"}, status=404)