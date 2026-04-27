from rest_framework import serializers
from core.models import Merchant, Payout, LedgerEntry, BankAccount, Webhook


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ["id", "name", "email"]


class BankAccountSerializer(serializers.ModelSerializer):
    merchant = serializers.UUIDField(source="merchant.id")
    merchant_name = serializers.CharField(source="merchant.name", read_only=True)

    class Meta:
        model = BankAccount
        fields = ["id", "account_number", "ifsc_code", "merchant", "merchant_name"]


class LedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = ["id", "type", "amount_paise", "created_at"]


class PayoutSerializer(serializers.ModelSerializer):
    
    merchant_name = serializers.CharField(source="merchant.name")

    class Meta:
        model = Payout
        fields = ["id", "amount_paise", "status", "created_at", "merchant_name", "snapshot_balance", "cancel_reason"]


class CreatePayoutSerializer(serializers.Serializer):
    amount_paise = serializers.IntegerField()
    bank_account_id = serializers.UUIDField()

class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = ["id", "url", "event_type", "created_at"]
