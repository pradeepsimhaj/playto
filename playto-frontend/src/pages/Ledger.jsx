import { useEffect, useState } from "react";
import API from "../api/axios";

export default function Ledger() {
  const [data, setData] = useState([]);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});

  const fetchLedger = async () => {
    const res = await API.get(`/ledger?page=${page}&limit=10`);
    setData(res.data.results);
    setPagination(res.data.pagination);
  };

  useEffect(() => {
    fetchLedger();
  }, [page]);

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Ledger</h1>

      <div className="bg-white rounded-xl shadow overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-3 text-left">Type</th>
              <th className="p-3 text-left">Amount</th>
              <th className="p-3 text-left">Date</th>
            </tr>
          </thead>

          <tbody>
            {data.map((l) => (
              <tr key={l.id} className="border-t">
                <td className="p-3">{l.type}</td>
                <td className="p-3">₹{l.amount_paise}</td>
                <td className="p-3 text-xs text-gray-500">
                  {new Date(l.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
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