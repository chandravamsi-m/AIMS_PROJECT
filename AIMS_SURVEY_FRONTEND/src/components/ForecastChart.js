// src/components/ForecastChart.jsx
import React, { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  CartesianGrid, ResponsiveContainer, Cell, LabelList
} from "recharts";
import "../styles/survey-result.css";

const HORIZONS = [0, 1, 3, 6];

export default function ForecastChart({ survey, apiBaseUrl = "http://localhost:8080/api", onDataUpdate }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!survey) return;
    setLoading(true);
    setError(null);

    const fetchPrediction = async (monthsAhead) => {
      const payload = { ...survey, monthsAhead };
      const url = monthsAhead === 0 ? `${apiBaseUrl}/predict` : `${apiBaseUrl}/predict-future`;
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`API error ${res.status}`);
      return res.json();
    };

    (async () => {
      try {
        const results = [];
        let lastMeta = null;
        for (const m of HORIZONS) {
          const r = await fetchPrediction(m);
          results.push({
            name: m === 0 ? "Current" : `${m} mo`,
            score: +(r.predictedFutureSeverityScore ?? r.currentSeverityScore ?? r.severityScore ?? 0).toFixed(2),
            meta: r
          });
          lastMeta = r;
        }
        setData(results);
        if (onDataUpdate && lastMeta) {
          onDataUpdate(lastMeta);
        }
      } catch (err) {
        setError(err.message || "Unknown error");
      } finally {
        setLoading(false);
      }
    })();
  }, [survey, apiBaseUrl, onDataUpdate]);

  if (!survey) return <div className="card">Please complete the survey to see predictions.</div>;
  if (loading) return <div className="card">Loading predictions…</div>;
  if (error) return <div className="card" style={{ color: "red" }}>Error: {error}</div>;

  return (
    <div style={{ background: "#fff", borderRadius: "12px", padding: "24px 20px", border: "1px solid #f1f5f9" }}>
      <div style={{ marginBottom: "20px", fontSize: "14px", fontWeight: "700", color: "#1e293b", display: "flex", alignItems: "center", gap: "8px" }}>
        📊 Predicted Severity (Current → 6 months)
      </div>
      <div style={{ height: "220px", width: "100%" }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 10, bottom: 5 }} barSize={48}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis 
              dataKey="name" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 11, fill: "#94a3b8", fontWeight: 500 }} 
              dy={10}
            />
            <YAxis 
              domain={[0, 5]} 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 11, fill: "#94a3b8", fontWeight: 500 }} 
              label={{ value: 'Severity Score', angle: -90, position: 'insideLeft', style: { fontSize: 10, fill: '#94a3b8', fontWeight: 600 } }}
            />
            <Tooltip 
              cursor={{ fill: 'rgba(241, 245, 249, 0.4)' }}
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', fontSize: '12px' }}
            />
            <Bar dataKey="score" radius={[6, 6, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill="#3b82f6" fillOpacity={0.8} />
              ))}
              <LabelList dataKey="score" position="top" style={{ fontSize: 11, fontWeight: 700, fill: '#1e293b' }} offset={10} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div style={{ textAlign: "center", fontSize: "12px", color: "#64748b", marginTop: "16px", fontWeight: "600" }}>
        Predicted Severity Score
      </div>
    </div>
  );
}

