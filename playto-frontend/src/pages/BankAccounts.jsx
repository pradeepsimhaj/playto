import { useEffect, useState } from "react";
import API from "../api/axios";

export default function BankAccounts() {
  const [accounts, setAccounts] = useState([]);

  useEffect(() => {
    API.get("/bank-accounts").then((res) => setAccounts(res.data));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Bank Accounts</h1>

      <div className="bg-white p-4 rounded shadow">
        {accounts.map((a) => (
          <div key={a.id} className="border-b py-2">
            {a.account_number} - {a.ifsc_code}
          </div>
        ))}
      </div>
    </div>
  );
}