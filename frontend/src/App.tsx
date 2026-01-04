import React, { useState } from "react";
import { advise } from "./api";

export default function App() {
  const [hand, setHand] = useState<string>("Ah,Kd");
  const [board, setBoard] = useState<string>("");
  const [position, setPosition] = useState<string>("BTN");
  const [output, setOutput] = useState<any>(null);

  async function onAdvise() {
    const payload = {
      hand: hand.split(",").map(s => s.trim()),
      board: board ? board.split(",").map(s => s.trim()) : [],
      position,
      stack: 120,
      pot: 9,
      opponent_style: "TAG",
      action_history: [],
      mode: "beginner"
    };
    try {
      const res = await advise(payload);
      setOutput(res);
    } catch (e) {
      setOutput({ error: String(e) });
    }
  }

  return (
    <div style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1>Poker Advisor (Prototype)</h1>
      <div>
        <label>Hand: <input value={hand} onChange={e => setHand(e.target.value)} /></label>
      </div>
      <div>
        <label>Board: <input value={board} onChange={e => setBoard(e.target.value)} placeholder="Qs,Jh,3c"/></label>
      </div>
      <div>
        <label>Position:
          <select value={position} onChange={e => setPosition(e.target.value)}>
            <option>BTN</option><option>CO</option><option>MP</option><option>UTG</option>
          </select>
        </label>
      </div>
      <button onClick={onAdvise} style={{ marginTop: 12 }}>Advise</button>

      <pre style={{ marginTop: 20 }}>{JSON.stringify(output, null, 2)}</pre>
    </div>
  );
}
