import uuid
from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Merchant, BankAccount, LedgerEntry, Payout


class IdempotencyTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.merchant = Merchant.objects.create(
            name="Test Merchant",
            email="test@test.com"
        )

        self.bank = BankAccount.objects.create(
            merchant=self.merchant,
            account_number="12345678",
            ifsc_code="HDFC0001"
        )

        LedgerEntry.objects.create(
            merchant=self.merchant,
            type="CREDIT",
            amount_paise=10000,
            reference_id=uuid.uuid4()
        )

    def test_idempotency(self):
        key = "test-key"

        data = {
            "amount_paise": 1000,
            "bank_account_id": str(self.bank.id)
        }

        res1 = self.client.post(
            "/api/v1/payouts",
            data,
            format="json",
            HTTP_IDEMPOTENCY_KEY=key
        )

        res2 = self.client.post(
            "/api/v1/payouts",
            data,
            format="json",
            HTTP_IDEMPOTENCY_KEY=key
        )

        self.assertEqual(res1.data["id"], res2.data["id"])

        # 🔥 Extra strong validation
        self.assertEqual(
            Payout.objects.filter(idempotency_key=key).count(), 1
        )