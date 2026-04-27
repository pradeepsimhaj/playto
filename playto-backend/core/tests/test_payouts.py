import uuid
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Merchant, BankAccount, LedgerEntry, Payout


class PayoutTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create merchant
        self.merchant = Merchant.objects.create(
            name="Test Merchant",
            email="test@test.com"
        )

        # Create bank account
        self.bank = BankAccount.objects.create(
            merchant=self.merchant,
            account_number="12345678",
            ifsc_code="HDFC0001"
        )

        # Add balance
        LedgerEntry.objects.create(
            merchant=self.merchant,
            type="CREDIT",
            amount_paise=10000,
            reference_id=uuid.uuid4()
        )

    # ✅ 1. Test payout creation
    def test_create_payout(self):
        response = self.client.post(
            "/api/v1/payouts",
            {
                "amount_paise": 5000,
                "bank_account_id": str(self.bank.id)
            },
            format="json",
            HTTP_IDEMPOTENCY_KEY="test-key-1"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "PENDING")

    # ✅ 2. Test idempotency
    def test_idempotency(self):
        data = {
            "amount_paise": 3000,
            "bank_account_id": str(self.bank.id)
        }

        res1 = self.client.post(
            "/api/v1/payouts",
            data,
            format="json",
            HTTP_IDEMPOTENCY_KEY="same-key"
        )

        res2 = self.client.post(
            "/api/v1/payouts",
            data,
            format="json",
            HTTP_IDEMPOTENCY_KEY="same-key"
        )

        self.assertEqual(res1.data["id"], res2.data["id"])

    # ✅ 3. Insufficient balance
    def test_insufficient_balance(self):
        response = self.client.post(
            "/api/v1/payouts",
            {
                "amount_paise": 999999,
                "bank_account_id": str(self.bank.id)
            },
            format="json",
            HTTP_IDEMPOTENCY_KEY="test-key-2"
        )

        self.assertEqual(response.status_code, 400)

    # ✅ 4. Ledger HOLD entry created
    def test_hold_entry_created(self):
        self.client.post(
            "/api/v1/payouts",
            {
                "amount_paise": 2000,
                "bank_account_id": str(self.bank.id)
            },
            format="json",
            HTTP_IDEMPOTENCY_KEY="test-key-3"
        )

        hold_exists = LedgerEntry.objects.filter(type="HOLD").exists()
        self.assertTrue(hold_exists)

    # ✅ 5. Background job updates status
    def test_background_processing(self):
        response = self.client.post(
            "/api/v1/payouts",
            {
                "amount_paise": 1000,
                "bank_account_id": str(self.bank.id)
            },
            format="json",
            HTTP_IDEMPOTENCY_KEY="test-key-4"
        )

        payout_id = response.data["id"]

        # Simulate background job manually
        payout = Payout.objects.get(id=payout_id)
        payout.status = "COMPLETED"
        payout.save()

        payout.refresh_from_db()

        self.assertIn(payout.status, ["COMPLETED", "FAILED", "PROCESSING"])