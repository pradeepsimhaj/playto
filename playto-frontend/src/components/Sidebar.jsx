import { Link, useLocation } from "react-router-dom";
import { LayoutDashboard, Wallet, FileText, Building2, Webhook } from "lucide-react";

export default function Sidebar() {
  const { pathname } = useLocation();

  const menu = [
    { name: "Merchants", path: "/merchants", icon: LayoutDashboard },
    { name: "Payouts", path: "/payouts", icon: Wallet },
    { name: "Ledger", path: "/ledger", icon: FileText },
    { name: "Bank Accounts", path: "/bank-accounts", icon: Building2 },
    { name: "Webhooks", path: "/webhooks", icon: Webhook },
  ];

  return (
    <div className="w-64 h-screen bg-gray-900 text-white p-4 hidden md:block">
      <h1 className="text-xl font-bold mb-6">Payout Dashboard</h1>

      {menu.map((item) => (
        <Link
          key={item.path}
          to={item.path}
          className={`flex items-center gap-2 p-3 rounded mb-2 transition ${
            pathname === item.path ? "bg-gray-700" : "hover:bg-gray-800"
          }`}
        >
          <item.icon size={18} />
          {item.name}
        </Link>
      ))}
    </div>
  );
}