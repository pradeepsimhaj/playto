import { useState } from "react";
import API from "../api/axios";

export default function Webhooks() {
  const [url, setUrl] = useState("");

  const createWebhook = async () => {
    await API.post("/webhooks", {
      url,
      event_type: "PAYOUT_STATUS",
    });
    alert("Webhook created!");
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Webhooks</h1>

      <div className="bg-white p-4 rounded shadow flex gap-2">
        <input
          placeholder="Webhook URL"
          className="border p-2 rounded flex-1"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button
          onClick={createWebhook}
          className="bg-green-500 text-white px-4 rounded"
        >
          Add
        </button>
      </div>
    </div>
  );
}