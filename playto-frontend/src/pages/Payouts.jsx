import { useEffect, useState } from "react";
import API from "../api/axios";

import useSocket from "../hooks/useSocket";

import AlertToast from "../components/AlertToast";

export default function Payouts() {
  const [payouts, setPayouts] = useState([]);
  const [amount, setAmount] = useState("");
  const [bankId, setBankId] = useState("");
  const [merchantId, setMerchantId] = useState("");
  const [merchants, setMerchants] = useState([]);
  const [search, setSearch] = useState("");
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [polling, setPolling] = useState(false);

  // 🔥 NEW STATES
  const [selectedPayout, setSelectedPayout] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const [alert, setAlert] = useState(null);

  // Fetch merchants
  useEffect(() => {
    API.get("/merchants").then((res) => {
      setMerchants(res.data);
      if (res.data.length > 0) {
        setMerchantId(res.data[0].id);
      }
    });
  }, []);

  // Fetch bank accounts
  useEffect(() => {
    API.get("/bank-accounts").then((res) => setAccounts(res.data));
  }, []);
  // Fetch payouts
  const fetchPayouts = async () => {
    if (!merchantId) return;

    try {
      const res = await API.get(
        `/payouts/list?merchant_id=${merchantId}`
      );
      setPayouts(res.data);

      const hasPending = res.data.some(
        (p) => p.status === "PENDING" || p.status === "PROCESSING"
      );

      setPolling(hasPending);
    } catch (err) {
      console.error(err);
    }
  };

useSocket((data) => {
  if (data.type === "PAYOUT_UPDATE") {
    fetchPayouts();

    if (data.status === "FAILED") {
      setAlert({ type: "error", message: "Payout Failed ❌" });
    }

    if (data.status === "COMPLETED") {
      setAlert({ type: "success", message: "Payout Completed ✅" });
    }
  }
});


  useEffect(() => {
    fetchPayouts();
  }, [merchantId]);

  useEffect(() => {
    if (!polling) return;

    const interval = setInterval(fetchPayouts, 3000);
    return () => clearInterval(interval);
  }, [polling]);

  // 🚀 UPDATED CREATE PAYOUT
  const createPayout = async () => {
    if (!amount || !bankId) return alert("Fill all fields");

    setLoading(true);

    try {
      const res = await API.post(
        "/payouts",
        {
          amount_paise: amount,
          bank_account_id: bankId,
        },
        {
          headers: {
            "Idempotency-Key": Date.now(),
          },
        }
      );

      const data = res.data;

      // 🚫 CANCELLED → SHOW POPUP
      if (data.status === "CANCELLED") {
        setSelectedPayout(data);
        setShowModal(true);
      }

      setAmount("");
      setBankId("");

      setPolling(true);
      fetchPayouts();
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  const filtered = payouts.filter((p) =>
    p.id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6">


      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Payouts</h1>

        <button
          onClick={fetchPayouts}
          className="bg-gray-200 hover:bg-gray-300 px-4 py-2 rounded-lg text-sm"
        >
          Refresh
        </button>
      </div>

      {/* Merchant Selector */}
      <div className="mb-4">
        <select
          className="border px-3 py-2 rounded-lg w-full md:w-1/3"
          value={merchantId}
          onChange={(e) => setMerchantId(e.target.value)}
        >
          {merchants.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name}
            </option>
          ))}
        </select>
      </div>

      {/* Form */}
      <div className="bg-white p-4 rounded-xl shadow-md mb-5 flex flex-col md:flex-row gap-3 items-center">
        <input
          placeholder="Amount"
          className="border px-3 py-2 rounded-lg"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />

        <select
          className="border px-3 py-2 rounded-lg"
          value={bankId}
          onChange={(e) => setBankId(e.target.value)}
        >
          <option value="">Select Bank Account</option>

          {accounts
            .filter((acc) =>
              String(acc.merchant) === String(merchantId)
            )
            .map((acc) => (
              <option key={acc.id} value={acc.id}>
                {acc.account_number} ({acc.merchant_name})
              </option>
            ))}
        </select>

        <button
          onClick={createPayout}
          disabled={!amount || !bankId || loading}
          className="bg-blue-500 text-white px-5 py-2 rounded-lg"
        >
          {loading ? "Creating..." : "Create"}
        </button>
      </div>

      {/* Search */}
      <input
        placeholder="Search by payout ID..."
        className="border px-3 py-2 rounded-lg mb-4 w-full"
        onChange={(e) => setSearch(e.target.value)}
      />

      {/* Table */}
      <div className="bg-white rounded-xl shadow overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-3 text-left">ID</th>
              <th className="p-3 text-left">Amount</th>
              <th className="p-3 text-left">Status</th>
            </tr>
          </thead>

          <tbody>
            {filtered.map((p) => (
              <tr
                key={p.id}
                className="border-t hover:bg-gray-50 cursor-pointer transition"
                onClick={() => {
                  if (p.status === "CANCELLED") {
                    setSelectedPayout(p);
                    setShowModal(true);
                  }
                }}
              >
                <td className="p-3 text-xs">{p.id}</td>
                <td className="p-3">₹{p.amount_paise}</td>
                <td className="p-3">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      p.status === "COMPLETED"
                        ? "bg-green-100 text-green-700"
                        : p.status === "FAILED"
                        ? "bg-red-100 text-red-700"
                        : p.status === "CANCELLED"
                        ? "bg-gray-200 text-gray-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}
                  >
                    {p.status === "CANCELLED"
                      ? "CANCELLED (Insufficient Funds)"
                      : p.status}
                  </span>
                  {p.status === "FAILED" && (
  <button
    onClick={() => API.post(`/payouts/retry/${p.id}`)}
    className="text-blue-500 ml-2"
  >
    Retry
  </button>
)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {alert && <AlertToast {...alert} />}

      {/* 🚀 MODAL */}
      {showModal && selectedPayout && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 animate-fadeIn">

            <h2 className="text-xl font-bold mb-4 text-gray-800">
              🚫 Transaction Cancelled
            </h2>

            <div className="space-y-2 text-sm">
              <p><strong>Payout ID:</strong> {selectedPayout.id}</p>
              <p><strong>Status:</strong> CANCELLED</p>

              <p className="text-red-600 font-medium">
                  Reason: {selectedPayout.cancel_reason || "Insufficient Balance"}
              </p>

              <hr className="my-2" />

              <p>
                <strong>Available Balance:</strong> ₹
                  {selectedPayout.snapshot_balance || selectedPayout.available_balance || "N/A"}
              </p>

              <p>
                <strong>Merchant:</strong>{" "}
                {selectedPayout.merchant_name || "N/A"}
              </p>
            </div>

            <button
              onClick={() => setShowModal(false)}
              className="mt-5 w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}