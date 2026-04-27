import {  Routes, Route } from "react-router-dom";
import Merchants from "../pages/Merchants";
import MerchantDetail from "../pages/MerchantDetail";
import Payouts from "../pages/Payouts";
import Ledger from "../pages/Ledger";
import BankAccounts from "../pages/BankAccounts";
import Webhooks from "../pages/Webhooks";
import LedgerAudit from "../pages/LedgerAudit";

export default function AppRoutes() {
  return (
      <Routes>
        <Route path="/" element={<Merchants />} />
        <Route path="/merchants" element={<Merchants />} />
        <Route path="/merchants/:id" element={<MerchantDetail />} />
        <Route path="/payouts" element={<Payouts />} />
        <Route path="/ledger" element={<Ledger />} />
        <Route path="/bank-accounts" element={<BankAccounts />} />
        <Route path="/webhooks" element={<Webhooks />} />
        <Route path="/ledger-audit" element={<LedgerAudit />} />
      </Routes>
  );
}