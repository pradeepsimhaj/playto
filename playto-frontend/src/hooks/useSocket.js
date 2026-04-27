import { useEffect } from "react";

export default function useSocket(onMessage) {
  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/payouts/");

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    return () => socket.close();
  }, []);
}