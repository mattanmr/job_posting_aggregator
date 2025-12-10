import { useState, useEffect } from "react";
import {
  getScheduleConfig,
  updateScheduleConfig,
} from "../services/api";
import { ScheduleConfig } from "../types";

export default function SchedulingConfig() {
  const [config, setConfig] = useState<ScheduleConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [inputValue, setInputValue] = useState("12");
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const data = await getScheduleConfig();
      setConfig(data);
      setInputValue(data.interval_hours.toString());
      setError(null);
    } catch (err: any) {
      console.error("Failed to load schedule config:", err);
      setError("Failed to load schedule configuration");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfig = async () => {
    const value = parseInt(inputValue, 10);

    if (isNaN(value)) {
      setError("Please enter a valid number");
      return;
    }

    if (!config || (value === config.interval_hours && !editing)) {
      setEditing(false);
      return;
    }

    try {
      setSaving(true);
      setError(null);
      const newConfig = await updateScheduleConfig(value);
      setConfig(newConfig);
      setInputValue(newConfig.interval_hours.toString());
      setEditing(false);
      setSuccessMessage(
        `Schedule updated to every ${newConfig.interval_hours} hour${newConfig.interval_hours !== 1 ? "s" : ""}`
      );
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      if (err.response?.status === 400) {
        setError(err.response?.data?.detail || "Invalid interval");
      } else {
        setError("Failed to update schedule configuration");
      }
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditing(false);
    if (config) {
      setInputValue(config.interval_hours.toString());
    }
    setError(null);
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <h2 style={styles.title}>Collection Schedule</h2>
        <p style={styles.loading}>Loading schedule configuration...</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Collection Schedule</h2>
      <p style={styles.subtitle}>
        Configure how often jobs are collected automatically
      </p>

      {error && <div style={styles.errorMessage}>{error}</div>}
      {successMessage && (
        <div style={styles.successMessage}>{successMessage}</div>
      )}

      {config && (
        <div style={styles.configBox}>
          <div style={styles.currentConfig}>
            <span style={styles.label}>Current Interval:</span>
            {!editing ? (
              <div style={styles.displayValue}>
                <span style={styles.value}>
                  Every {config.interval_hours} hour{config.interval_hours !== 1 ? "s" : ""}
                </span>
                <button
                  onClick={() => setEditing(true)}
                  style={styles.editBtn}
                  title="Edit schedule"
                >
                  Edit
                </button>
              </div>
            ) : (
              <div style={styles.editValue}>
                <input
                  type="number"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  min={config.min_interval}
                  max={config.max_interval}
                  style={styles.input}
                  disabled={saving}
                />
                <span style={styles.unit}>hours</span>
                <button
                  onClick={handleSaveConfig}
                  disabled={saving}
                  style={styles.saveBtn}
                >
                  {saving ? "Saving..." : "Save"}
                </button>
                <button
                  onClick={handleCancel}
                  disabled={saving}
                  style={styles.cancelBtn}
                >
                  Cancel
                </button>
              </div>
            )}
          </div>

          {/* Range info */}
          <div style={styles.rangeInfo}>
            <p style={styles.rangeText}>
              Valid range: {config.min_interval} to {config.max_interval} hours
              <br />
              ({Math.floor(config.max_interval / 24)} weeks maximum)
            </p>
          </div>

          {/* Schedule examples */}
          <div style={styles.examplesBox}>
            <strong style={styles.examplesTitle}>Quick Set:</strong>
            <div style={styles.buttonGrid}>
              {[1, 6, 12, 24, 48].map((hours) => (
                <button
                  key={hours}
                  onClick={() => {
                    setInputValue(hours.toString());
                    if (editing) {
                      // Will save on next action
                    }
                  }}
                  style={{
                    ...styles.quickBtn,
                    backgroundColor:
                      parseInt(inputValue) === hours ? "#4CAF50" : "#e0e0e0",
                    color: parseInt(inputValue) === hours ? "white" : "#333",
                  }}
                  title={`Set to ${hours} hour${hours !== 1 ? "s" : ""}`}
                >
                  {hours}h
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
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
  loading: {
    color: "#666",
    fontSize: "14px",
    textAlign: "center" as const,
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
  configBox: {
    backgroundColor: "white",
    border: "1px solid #ddd",
    borderRadius: "6px",
    padding: "15px",
  },
  currentConfig: {
    marginBottom: "15px",
    paddingBottom: "15px",
    borderBottom: "1px solid #eee",
  },
  label: {
    fontWeight: "600",
    color: "#555",
    display: "block",
    marginBottom: "8px",
    fontSize: "14px",
  },
  displayValue: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },
  value: {
    fontSize: "16px",
    color: "#333",
    fontWeight: "500",
  },
  editBtn: {
    padding: "6px 12px",
    backgroundColor: "#2196F3",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: "500",
  },
  editValue: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
  },
  input: {
    padding: "8px",
    fontSize: "14px",
    border: "1px solid #ddd",
    borderRadius: "4px",
    width: "80px",
    fontFamily: "inherit",
  },
  unit: {
    fontSize: "14px",
    color: "#666",
    minWidth: "50px",
  },
  saveBtn: {
    padding: "8px 16px",
    backgroundColor: "#4CAF50",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: "500",
  },
  cancelBtn: {
    padding: "8px 16px",
    backgroundColor: "#f44336",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: "500",
  },
  rangeInfo: {
    backgroundColor: "#f5f5f5",
    border: "1px solid #e0e0e0",
    borderRadius: "4px",
    padding: "10px",
    marginBottom: "10px",
  },
  rangeText: {
    margin: "0",
    fontSize: "13px",
    color: "#666",
    lineHeight: "1.5",
  },
  examplesBox: {
    backgroundColor: "#f9f9f9",
    border: "1px solid #e0e0e0",
    borderRadius: "4px",
    padding: "10px",
  },
  examplesTitle: {
    fontSize: "13px",
    color: "#555",
    display: "block",
    marginBottom: "8px",
  },
  buttonGrid: {
    display: "flex",
    gap: "8px",
    flexWrap: "wrap",
  },
  quickBtn: {
    padding: "6px 12px",
    border: "1px solid #ccc",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: "500",
    transition: "all 0.2s",
  },
};
