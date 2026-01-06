import { panel } from "./extension";

export async function sendToBackend(payload: any) {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/analyze/code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    panel?.update(data);
  } catch (err) {
    panel?.update({ error: "Backend not reachable" });
  }
}
