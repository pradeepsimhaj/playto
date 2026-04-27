import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import API from "../api/axios";

export default function MerchantDetail() {
  const { id } = useParams();

  const [data, setData] = useState(null);
  const [page, setPage] = useState(1);
  const [polling, setPolling] = useState(false);

  const fetchMerchant = async () => {
    try {
      const res = await API.get(`/merchants/${id}?page=${page}&limit=5`);
      setData(res.data);

      // ✅ SMART POLLING CONDITION
      if (res.data.held_balance > 0) {
        setPolling(true);
      } else {
        setPolling(false);
      }

    } catch (err) {
      console.error(err);
    }
  };

  // Initial + page change
  useEffect(() => {
    fetchMerchant();
  }, [id, page]);

  // 🔥 AUTO REFRESH ONLY WHEN HELD > 0
  useEffect(() => {
    if (!polling) return;

    const interval = setInterval(fetchMerchant, 3000);

    return () => clearInterval(interval);
  }, [polling]);

  if (!data) return <div className="p-6">Loading...</div>;

  const { merchant, pagination } = data;

  return (
    <div className="p-6">

      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Merchant Details</h1>

        <button
          onClick={fetchMerchant}
          className="bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded text-sm"
        >
          Refresh
        </button>
      </div>

      {/* Merchant Card */}
      <div className="bg-white p-5 rounded-xl shadow mb-5">

        <p><b>Name:</b> {merchant.name}</p>
        <p><b>Email:</b> {merchant.email}</p>

        <p className="text-green-600 font-semibold">
          <b>Available:</b> ₹{data.available_balance}
        </p>

        {/* 🔥 HELD FIX */}
        <p
          className={`font-semibold ${
            data.held_balance > 0
              ? "text-yellow-600 animate-pulse"
              : "text-gray-500"
          }`}
        >
          <b>Held:</b> ₹{data.held_balance}
        </p>

        {data.held_balance > 0 && (
          <p className="text-xs text-yellow-500 mt-1">
            Processing payout... updating automatically
          </p>
        )}
      </div>

      {/* Transactions */}
      <h2 className="text-lg font-semibold mb-3">Recent Transactions</h2>

      <div className="bg-white rounded-xl shadow divide-y">
        {data.recent_transactions.map((t) => (
          <div key={t.id} className="p-3 flex justify-between">

            <span
              className={`font-medium ${
                t.type === "DEBIT"
                  ? "text-red-600"
                  : t.type === "CREDIT"
                  ? "text-green-600"
                  : t.type === "HOLD"
                  ? "text-yellow-600"
                  : t.type === "RELEASE"
                  ? "text-blue-600"
                  : "text-gray-600"
              }`}
            >
              {t.type}
            </span>

            <span>₹{t.amount_paise}</span>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center mt-4">
        <button
          disabled={!pagination?.has_prev}
          onClick={() => setPage((p) => p - 1)}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Previous
        </button>

        <span className="text-sm">
          Page {pagination?.page}
        </span>

        <button
          disabled={!pagination?.has_next}
          onClick={() => setPage((p) => p + 1)}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>

    </div>
  );
}