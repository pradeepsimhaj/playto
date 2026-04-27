import uuid
from threading import Thread
from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Merchant, BankAccount, LedgerEntry, Payout


class ConcurrencyTest(TestCase):

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

        # Only enough for ONE payout
        LedgerEntry.objects.create(
            merchant=self.merchant,
            type="CREDIT",
            amount_paise=6000,
            reference_id=uuid.uuid4()
        )

    def test_double_spend(self):

        def make_request():
            self.client.post(
                "/api/v1/payouts",
                {
                    "amount_paise": 6000,
                    "bank_account_id": str(self.bank.id)
                },
                format="json",
                HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4())
            )

        t1 = Thread(target=make_request)
        t2 = Thread(target=make_request)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        payouts = Payout.objects.all()

        # ✅ Only ONE payout should succeed
        self.assertTrue(payouts.count() <= 1)