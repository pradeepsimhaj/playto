import { useEffect } from "react";

export default function useSocket(onMessage) {
  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/payouts/");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    return () => ws.close();
  }, []);
}