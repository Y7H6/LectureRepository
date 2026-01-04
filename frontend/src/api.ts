import axios from "axios";

export async function advise(payload: any) {
  const base = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const res = await axios.post(`${base}/api/advise`, payload, { timeout: 30000 });
  return res.data;
}
