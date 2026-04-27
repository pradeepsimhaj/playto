from django.db import transaction, IntegrityError
from core.models import Merchant, LedgerEntry, Payout, Event, AuditLog
from core.services.ledger import get_balance
from core.tasks import process_payout


def create_payout(merchant, amount, bank_account, idempotency_key):

    with transaction.atomic():

        merchant = Merchant.objects.select_for_update().get(id=merchant.id)

        balance = get_balance(merchant.id)

        # ❌ INSUFFICIENT BALANCE → CANCELLED
        if balance < amount:

            payout = Payout.objects.create(
                merchant=merchant,
                amount_paise=amount,
                bank_account_id=bank_account,
                status="CANCELLED",
                idempotency_key=idempotency_key,
                cancel_reason="INSUFFICIENT_FUNDS",
                snapshot_balance=balance
            )

            # EVENT
            Event.objects.create(
                aggregate_type="PAYOUT",
                aggregate_id=payout.id,
                event_type="PAYOUT_CANCELLED",
                payload={
                    "reason": "INSUFFICIENT_FUNDS",
                    "balance": balance
                }
            )

            # AUDIT
            AuditLog.objects.create(
                actor="SYSTEM",
                action="PAYOUT_CANCELLED",
                entity_type="PAYOUT",
                entity_id=payout.id
            )

            return payout, balance

        # ✅ NORMAL FLOW
        try:
            payout = Payout.objects.create(
                merchant=merchant,
                amount_paise=amount,
                bank_account_id=bank_account,
                status="PENDING",
                idempotency_key=idempotency_key
            )
        except IntegrityError:
            existing = Payout.objects.get(
                merchant=merchant,
                idempotency_key=idempotency_key
            )
            return existing, balance

        # HOLD
        LedgerEntry.objects.create(
            merchant=merchant,
            type="HOLD",
            amount_paise=amount,
            reference_id=payout.id
        )

        # EVENT
        Event.objects.create(
            aggregate_type="PAYOUT",
            aggregate_id=payout.id,
            event_type="PAYOUT_CREATED",
            payload={"amount": amount}
        )

        # AUDIT
        AuditLog.objects.create(
            actor="SYSTEM",
            action="PAYOUT_CREATED",
            entity_type="PAYOUT",
            entity_id=payout.id
        )

        transaction.on_commit(lambda: process_payout.delay(str(payout.id)))

        return payout, balance