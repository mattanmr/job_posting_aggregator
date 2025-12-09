import { useState, useEffect } from "react";
import {
  getKeywords,
  addKeyword,
  removeKeyword,
} from "../services/api";

export default function KeywordManager() {
  const [keywords, setKeywords] = useState<string[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Load keywords on component mount
  useEffect(() => {
    loadKeywords();
  }, []);

  const loadKeywords = async () => {
    try {
      setLoading(true);
      const kw = await getKeywords();
      setKeywords(kw);
      setError(null);
    } catch (err: any) {
      setError("Failed to load keywords");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddKeyword = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = inputValue.trim();

    if (!trimmed) {
      setError("Keyword cannot be empty");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const kw = await addKeyword(trimmed);
      setKeywords(kw);
      setInputValue("");
      setSuccessMessage(`Keyword "${trimmed}" added successfully`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      if (err.response?.status === 409) {
        setError("Keyword already exists");
      } else {
        setError("Failed to add keyword");
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveKeyword = async (keyword: string) => {
    if (!window.confirm(`Remove keyword "${keyword}"?`)) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const kw = await removeKeyword(keyword);
      setKeywords(kw);
      setSuccessMessage(`Keyword "${keyword}" removed`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setError("Failed to remove keyword");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Job Search Keywords</h2>
      <p style={styles.subtitle}>
        Configure keywords to collect jobs automatically every 12 hours
      </p>

      {/* Add keyword form */}
      <form onSubmit={handleAddKeyword} style={styles.form}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Enter keyword (e.g., Python Developer, React Engineer)"
          disabled={loading}
          style={styles.input}
        />
        <button
          type="submit"
          disabled={loading || !inputValue.trim()}
          style={styles.button}
        >
          {loading ? "Adding..." : "Add Keyword"}
        </button>
      </form>

      {/* Messages */}
      {error && <div style={styles.errorMessage}>{error}</div>}
      {successMessage && (
        <div style={styles.successMessage}>{successMessage}</div>
      )}

      {/* Keywords list */}
      <div style={styles.keywordsList}>
        {keywords.length === 0 ? (
          <p style={styles.emptyMessage}>
            No keywords configured. Add one to start collecting jobs!
          </p>
        ) : (
          <>
            <h3 style={styles.listTitle}>
              Active Keywords ({keywords.length})
            </h3>
            <div style={styles.chipContainer}>
              {keywords.map((keyword) => (
                <div key={keyword} style={styles.chip}>
                  <span>{keyword}</span>
                  <button
                    onClick={() => handleRemoveKeyword(keyword)}
                    disabled={loading}
                    style={styles.removeBtn}
                    title="Remove keyword"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    padding: "20px",
    backgroundColor: "#f9f9f9",
    borderRadius: "8px",
    marginBottom: "20px",
  },
  title: {
    fontSize: "20px",
    fontWeight: "bold",
    marginBottom: "5px",
    color: "#333",
  },
  subtitle: {
    fontSize: "14px",
    color: "#666",
    marginBottom: "15px",
  },
  form: {
    display: "flex",
    gap: "10px",
    marginBottom: "15px",
  },
  input: {
    flex: 1,
    padding: "10px",
    fontSize: "14px",
    border: "1px solid #ddd",
    borderRadius: "4px",
    fontFamily: "inherit",
  },
  button: {
    padding: "10px 20px",
    backgroundColor: "#4CAF50",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500",
  },
  errorMessage: {
    padding: "10px",
    backgroundColor: "#ffebee",
    color: "#c62828",
    borderRadius: "4px",
    marginBottom: "10px",
    fontSize: "14px",
  },
  successMessage: {
    padding: "10px",
    backgroundColor: "#e8f5e9",
    color: "#2e7d32",
    borderRadius: "4px",
    marginBottom: "10px",
    fontSize: "14px",
  },
  keywordsList: {
    marginTop: "15px",
  },
  listTitle: {
    fontSize: "14px",
    fontWeight: "600",
    color: "#555",
    marginBottom: "10px",
  },
  chipContainer: {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px",
  },
  chip: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "8px 12px",
    backgroundColor: "#e3f2fd",
    border: "1px solid #90caf9",
    borderRadius: "16px",
    fontSize: "14px",
    color: "#1565c0",
  },
  removeBtn: {
    background: "none",
    border: "none",
    color: "#1565c0",
    fontSize: "18px",
    cursor: "pointer",
    padding: "0",
    marginLeft: "4px",
    fontWeight: "bold",
  },
  emptyMessage: {
    color: "#999",
    fontSize: "14px",
    textAlign: "center" as const,
    padding: "20px",
  },
};
