import axios from "axios";

const backendUrl = import.meta.env.VITE_BACKEND_URL;

// const backendUrl = "http://127.0.0.1:8000";


const API = axios.create({
  baseURL: backendUrl + "/api/v1",
});

export default API;