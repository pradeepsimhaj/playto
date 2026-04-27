import { useEffect, useState } from "react";
import API from "../api/axios";

export default function LedgerAudit() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fixing, setFixing] = useState(false);

  const fetchAudit = async () => {
    setLoading(true);
    const res = await API.get("/ledger/audit");
    setIssues(res.data.issues);
    setLoading(false);
  };

  const fixIssues = async () => {
    setFixing(true);
    await API.post("/ledger/repair");
    await fetchAudit();
    setFixing(false);
  };

  useEffect(() => {
    fetchAudit();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Ledger Audit Dashboard</h1>

      <div className="flex gap-2 mb-4">
        <button
          onClick={fetchAudit}
          className="bg-gray-200 px-4 py-2 rounded"
        >
          Refresh
        </button>

        <button
          onClick={fixIssues}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          {fixing ? "Fixing..." : "Auto Fix Issues"}
        </button>
      </div>

      {loading ? (
        <div>Loading...</div>
      ) : issues.length === 0 ? (
        <div className="text-green-600 font-semibold">
          ✅ No Issues Found
        </div>
      ) : (
        <div className="bg-white rounded shadow p-4">
          {issues.map((issue, i) => (
            <div key={i} className="border-b py-2">
              <p><b>Type:</b> {issue.type}</p>
              <p><b>Payout:</b> {issue.payout_id}</p>

              {issue.missing && (
                <p className="text-red-500">
                  Missing Release: ₹{issue.missing}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}