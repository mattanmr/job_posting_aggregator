import { useState } from "react";
import api from "../../services/api";

export default function Search() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function doSearch() {
    if (!q.trim()) return;
    
    setLoading(true);
    setError("");
    
    try {
      const res = await api.get("/search", { params: { q } });
      setResults(res.data);
    } catch (err) {
      setError("Failed to fetch jobs. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      doSearch();
    }
  };

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto" }}>
      <div style={{ marginBottom: "20px" }}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Search jobs (e.g., Python, React, DevOps)"
          style={{
            padding: "10px",
            width: "100%",
            maxWidth: "500px",
            fontSize: "16px",
            border: "1px solid #ddd",
            borderRadius: "4px",
          }}
        />
        <button
          onClick={doSearch}
          disabled={loading}
          style={{
            marginLeft: "10px",
            padding: "10px 20px",
            backgroundColor: "#0066cc",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: loading ? "not-allowed" : "pointer",
            fontSize: "16px",
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {error && (
        <div style={{ color: "red", marginBottom: "20px", padding: "10px", backgroundColor: "#ffe6e6", borderRadius: "4px" }}>
          {error}
        </div>
      )}

      {loading && (
        <div style={{ textAlign: "center", padding: "20px", color: "#666" }}>
          Loading results...
        </div>
      )}

      {!loading && results.length === 0 && q && (
        <div style={{ textAlign: "center", padding: "20px", color: "#999" }}>
          No jobs found for "{q}"
        </div>
      )}

      <ul style={{ listStyle: "none", padding: 0 }}>
        {results.map((r) => (
          <li
            key={r.id}
            style={{
              marginBottom: "20px",
              padding: "15px",
              border: "1px solid #e0e0e0",
              borderRadius: "4px",
              backgroundColor: "#f9f9f9",
            }}
          >
            <div style={{ marginBottom: "8px" }}>
              <span style={{ fontWeight: "bold", fontSize: "18px" }}>
                {r.title}
              </span>
              <span
                style={{
                  marginLeft: "10px",
                  padding: "4px 8px",
                  backgroundColor: "#e3f2fd",
                  borderRadius: "3px",
                  fontSize: "12px",
                  color: "#1976d2",
                }}
              >
                {r.source}
              </span>
            </div>
            <div style={{ color: "#555", marginBottom: "8px" }}>
              <strong>{r.company}</strong>
              {r.location && (
                <>
                  {" "}
                  — <span style={{ color: "#777" }}>{r.location}</span>
                </>
              )}
            </div>

            {/* Education and Experience Requirements */}
            <div style={{ marginBottom: "8px", display: "flex", gap: "15px", flexWrap: "wrap" }}>
              {r.diploma_required && (
                <div style={{ fontSize: "13px" }}>
                  <span style={{ fontWeight: "600", color: "#555" }}>Education:</span>{" "}
                  <span style={{ color: "#666" }}>{r.diploma_required}</span>
                </div>
              )}
              {r.years_experience && (
                <div style={{ fontSize: "13px" }}>
                  <span style={{ fontWeight: "600", color: "#555" }}>Experience:</span>{" "}
                  <span style={{ color: "#666" }}>{r.years_experience}</span>
                </div>
              )}
            </div>

            {r.description && (
              <div
                style={{
                  color: "#666",
                  marginBottom: "10px",
                  lineHeight: "1.5",
                  fontSize: "14px",
                }}
              >
                {r.description.length > 300
                  ? r.description.slice(0, 300) + "..."
                  : r.description}
              </div>
            )}
            {r.url && (
              <a
                href={r.url}
                target="_blank"
                rel="noreferrer"
                style={{
                  display: "inline-block",
                  padding: "8px 16px",
                  backgroundColor: "#0066cc",
                  color: "white",
                  textDecoration: "none",
                  borderRadius: "4px",
                  fontSize: "14px",
                }}
              >
                View Job →
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
