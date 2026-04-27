import { useEffect } from "react";

const backendUrl = import.meta.env.VITE_BACKEND_URL;


export default function useSocket(onMessage) {
  useEffect(() => {
    const socket = new WebSocket(backendUrl + "/payouts/");

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    return () => socket.close();
  }, []);
}