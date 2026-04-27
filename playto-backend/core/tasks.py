import random
import requests
from celery import shared_task
from django.db import transaction
from core.models import Payout, LedgerEntry, Event, Webhook, WebhookDelivery

from datetime import timedelta
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@shared_task(bind=True, max_retries=3)
def process_payout(self, payout_id):

    payout = Payout.objects.filter(id=payout_id).first()
    if not payout:
        return

    if payout.status not in ["PENDING", "PROCESSING"]:
        return

    with transaction.atomic():

        payout.status = "PROCESSING"
        payout.attempt_count += 1
        payout.save()

        send_realtime_update({
            "type": "PAYOUT_UPDATE",
            "payout_id": str(payout.id),
            "status": payout.status,
            "amount": payout.amount_paise
            })

        outcome = random.random()

        # ✅ SUCCESS
        if outcome < 0.7:
            payout.status = "COMPLETED"

            # 🔥 RELEASE HOLD (VERY IMPORTANT FIX)
            LedgerEntry.objects.create(
                merchant=payout.merchant,
                type="RELEASE",
                amount_paise=payout.amount_paise,
                reference_id=payout.id
            )

            # 🔥 FINAL DEBIT
            LedgerEntry.objects.create(
                merchant=payout.merchant,
                type="DEBIT",
                amount_paise=payout.amount_paise,
                reference_id=payout.id
            )

        # ❌ FAILURE
        elif outcome < 0.9:
            payout.status = "FAILED"

            # 🔥 RELEASE HOLD (return money)
            LedgerEntry.objects.create(
                merchant=payout.merchant,
                type="RELEASE",
                amount_paise=payout.amount_paise,
                reference_id=payout.id
            )

        else:
            raise self.retry(countdown=10)

        payout.save()

        # ✅ EVENT LOG
        Event.objects.create(
            aggregate_type="PAYOUT",
            aggregate_id=payout.id,
            event_type=payout.status,
            payload={"attempt": payout.attempt_count}
        )

        # ✅ TRIGGER WEBHOOK
        webhooks = Webhook.objects.filter(
            merchant=payout.merchant,
            event_type="PAYOUT_STATUS",
            is_active=True
        )

        for webhook in webhooks:
            send_webhook.delay(str(webhook.id), {
                "payout_id": str(payout.id),
                "status": payout.status,
                "amount": payout.amount_paise
            })


@shared_task(bind=True, max_retries=3)
def send_webhook(self, webhook_id, payload):

    webhook = Webhook.objects.get(id=webhook_id)

    delivery = WebhookDelivery.objects.create(
        webhook=webhook,
        payload=payload
    )

    try:
        response = requests.post(
            webhook.url,
            json=payload,
            timeout=5
        )

        if 200 <= response.status_code < 300:
            delivery.status = "SUCCESS"
        else:
            raise Exception("Webhook failed")

    except Exception as e:
        delivery.attempt_count += 1
        delivery.last_error = str(e)

        if delivery.attempt_count >= 3:
            delivery.status = "FAILED"
            delivery.save()
            return

        delivery.save()
        raise self.retry(countdown=10)

    delivery.save()


@shared_task
def retry_stuck_payouts():

    threshold = timezone.now() - timedelta(seconds=30)

    stuck_payouts = Payout.objects.filter(
        status="PROCESSING",
        updated_at__lt=threshold
    )

    for payout in stuck_payouts:

        if payout.attempt_count >= 3:
            payout.status = "FAILED"
            payout.save()
            continue

        process_payout.delay(payout.id)


@shared_task
def retry_failed_webhooks():

    deliveries = WebhookDelivery.objects.filter(
        status="FAILED",
        attempt_count__lt=3
    )

    for d in deliveries:
        send_webhook.delay(str(d.webhook.id), d.payload)


def send_realtime_update(data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "payouts",
        {
            "type": "send_update",
            "data": data
        }
    )