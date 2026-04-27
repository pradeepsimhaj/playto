from django.core.management.base import BaseCommand
from core.models import Merchant, BankAccount, LedgerEntry
import random

import uuid


class Command(BaseCommand):
    help = "Seed database with merchants, bank accounts, and ledger credits"

    def handle(self, *args, **kwargs):

        self.stdout.write("Seeding data...")

        # Clear existing data (optional but useful)
        Merchant.objects.all().delete()
        BankAccount.objects.all().delete()
        LedgerEntry.objects.all().delete()

        merchants = []

        # Create merchants
        for i in range(5):
            merchant = Merchant.objects.create(
                name=f"Merchant {i+1}",
                email=f"merchant{i+1}@test.com"
            )
            merchants.append(merchant)

        self.stdout.write("Created merchants")

        # Create bank accounts
        for merchant in merchants:
            BankAccount.objects.create(
                merchant=merchant,
                account_number=str(random.randint(10000000, 99999999)),
                ifsc_code="HDFC0001234"
            )

        self.stdout.write("Created bank accounts")

        # Add ledger credits
        for merchant in merchants:
            for _ in range(3):  # 3 credits each
                amount = random.randint(5000, 20000)

                LedgerEntry.objects.create(
                    merchant=merchant,
                    type="CREDIT",
                    amount_paise=amount,
                    reference_id=uuid.uuid4()
                )

        self.stdout.write(self.style.SUCCESS("Seed data created successfully!"))