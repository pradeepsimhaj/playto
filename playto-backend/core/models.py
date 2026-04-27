import uuid
from django.db import models

class Merchant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)


class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)


class LedgerEntry(models.Model):
    class Type(models.TextChoices):
        CREDIT = "CREDIT"
        DEBIT = "DEBIT"
        HOLD = "HOLD"
        RELEASE = "RELEASE"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=Type.choices)
    amount_paise = models.BigIntegerField()
    reference_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)


class Payout(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        PROCESSING = "PROCESSING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"
        CANCELLED = "CANCELLED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    amount_paise = models.BigIntegerField()
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices)
    idempotency_key = models.CharField(max_length=255)
    attempt_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    cancel_reason = models.CharField(max_length=255, null=True, blank=True)
    snapshot_balance = models.BigIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("merchant", "idempotency_key")


class IdempotencyKey(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    response_body = models.JSONField()
    status_code = models.IntegerField()

    class Meta:
        unique_together = ("merchant", "key")


# ================= NEW MODELS =================

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    aggregate_type = models.CharField(max_length=50)
    aggregate_id = models.UUIDField()

    event_type = models.CharField(max_length=50)
    payload = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)


class Webhook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)

    url = models.URLField()
    event_type = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WebhookDelivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    payload = models.JSONField()

    status = models.CharField(max_length=20, default="PENDING")
    attempt_count = models.IntegerField(default=0)

    last_error = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    actor = models.CharField(max_length=50)
    action = models.CharField(max_length=100)

    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()

    metadata = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)