import { useState, useEffect } from "react";
import { getCollectionStatus } from "../services/api";

interface Status {
  nextTime: Date | null;
  lastTime: string | null;
  timeUntilNext: string;
  loading: boolean;
  error: string | null;
}

export default function CollectionStatus() {
  const [status, setStatus] = useState<Status>({
    nextTime: null,
    lastTime: null,
    timeUntilNext: "Loading...",
    loading: true,
    error: null,
  });

  // Load status on mount and refresh every second for countdown
  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 1000);
    return () => clearInterval(interval);
  }, []);

  const loadStatus = async () => {
    try {
      const data = await getCollectionStatus();
      const nextDate = new Date(data.next_collection_timestamp);

      setStatus({
        nextTime: nextDate,
        lastTime: data.last_collection_time,
        timeUntilNext: calculateTimeUntil(nextDate),
        loading: false,
        error: null,
      });
    } catch (err: any) {
      console.error("Failed to load collection status:", err);
      setStatus((prev) => ({
        ...prev,
        loading: false,
        error: "Failed to load collection status",
      }));
    }
  };

  const calculateTimeUntil = (futureDate: Date): string => {
    const now = new Date();
    const diff = futureDate.getTime() - now.getTime();

    if (diff <= 0) {
      return "Collection in progress or overdue";
    }

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else {
      return `${seconds}s`;
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Job Collection Status</h2>

      {status.loading ? (
        <p style={styles.loading}>Loading collection status...</p>
      ) : status.error ? (
        <div style={styles.errorMessage}>{status.error}</div>
      ) : (
        <>
          {/* Next Collection */}
          <div style={styles.statusBox}>
            <div style={styles.statusItem}>
              <span style={styles.label}>Next Collection:</span>
              <div style={styles.countdownContainer}>
                <div style={styles.countdown}>{status.timeUntilNext}</div>
                <div style={styles.countdownLabel}>
                  {status.nextTime?.toLocaleString()}
                </div>
              </div>
            </div>

            {/* Last Collection */}
            {status.lastTime && (
              <div style={styles.statusItem}>
                <span style={styles.label}>Last Collection:</span>
                <span style={styles.value}>{status.lastTime}</span>
              </div>
            )}

            {/* Info message */}
            <div style={styles.infoBox}>
              <p style={styles.infoText}>
                Jobs are collected automatically every 12 hours for all configured keywords.
                Add keywords to start collecting job postings.
              </p>
            </div>
          </div>

          {/* Collection frequency info */}
          <div style={styles.scheduleInfo}>
            <strong>Collection Schedule:</strong> Every 12 hours
            <br />
            <strong>Data Stored:</strong> CSV files with job details
            <br />
            <strong>Job Fields:</strong> Title, Company, Location, Diploma, Experience, Link
          </div>
        </>
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
    marginBottom: "15px",
    color: "#333",
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
    fontSize: "14px",
  },
  statusBox: {
    backgroundColor: "white",
    border: "1px solid #ddd",
    borderRadius: "6px",
    padding: "15px",
    marginBottom: "15px",
  },
  statusItem: {
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
  countdownContainer: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "5px",
  },
  countdown: {
    fontSize: "28px",
    fontWeight: "bold",
    color: "#4CAF50",
    fontFamily: "monospace",
  },
  countdownLabel: {
    fontSize: "12px",
    color: "#999",
  },
  value: {
    fontSize: "14px",
    color: "#333",
  },
  infoBox: {
    backgroundColor: "#e8f5e9",
    border: "1px solid #c8e6c9",
    borderRadius: "4px",
    padding: "10px",
    marginTop: "10px",
  },
  infoText: {
    margin: "0",
    fontSize: "13px",
    color: "#2e7d32",
    lineHeight: "1.5",
  },
  scheduleInfo: {
    backgroundColor: "white",
    border: "1px solid #ddd",
    borderRadius: "6px",
    padding: "12px",
    fontSize: "13px",
    color: "#666",
    lineHeight: "1.8",
  },
};
