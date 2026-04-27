import { useEffect, useState } from "react";
import API from "../api/axios";
import { Link } from "react-router-dom";

export default function Merchants() {
  const [merchants, setMerchants] = useState([]);

  useEffect(() => {
    API.get("/merchants")
      .then((res) => setMerchants(res.data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Merchants</h1>

      <div className="bg-white shadow rounded p-4">
        {merchants.map((m) => (
          <Link
            key={m.id}
            to={`/merchants/${m.id}`}
            className="block p-2 border-b hover:bg-gray-100"
          >
            {m.name} - {m.email}
          </Link>
        ))}
      </div>
    </div>
  );
}