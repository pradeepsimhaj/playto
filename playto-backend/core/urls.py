from django.contrib import admin
from django.urls import path
from core.views import (
    MerchantListView,
    MerchantDetailView,
    CreatePayoutView,
    PayoutListView,
    PayoutDetailView,
    LedgerView,
    BankAccountListView,
    WebhookCreateView,
    LedgerAuditView,
    LedgerRepairView,
    RetryPayoutView
)

urlpatterns = [

    path("admin/", admin.site.urls),

    path("merchants", MerchantListView.as_view()),
    path("merchants/<uuid:merchant_id>", MerchantDetailView.as_view()),

    path("payouts", CreatePayoutView.as_view()),  # POST
    path("payouts/list", PayoutListView.as_view()),  # GET
    path("payouts/<uuid:payout_id>", PayoutDetailView.as_view()),

    path("ledger", LedgerView.as_view()),
    path("bank-accounts", BankAccountListView.as_view()),

    path("webhooks", WebhookCreateView.as_view()),

    path("ledger/audit", LedgerAuditView.as_view()),
    path("ledger/repair", LedgerRepairView.as_view()),

    path("payouts/retry/<uuid:payout_id>", RetryPayoutView.as_view()),
]