import { useState, useEffect } from "react";
import { getCsvFiles, downloadCsvFile } from "../services/api";
import { CsvFileInfo } from "../types";

export default function CsvViewer() {
  const [files, setFiles] = useState<CsvFileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    loadCsvFiles();
    // Refresh file list every 30 seconds
    const interval = setInterval(loadCsvFiles, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadCsvFiles = async () => {
    try {
      setError(null);
      const csvFiles = await getCsvFiles();
      setFiles(csvFiles);
    } catch (err: any) {
      console.error("Failed to load CSV files:", err);
      setError("Failed to load CSV files");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (filename: string) => {
    try {
      setDownloading(filename);
      await downloadCsvFile(filename);
    } catch (err: any) {
      console.error("Failed to download file:", err);
      alert("Failed to download file");
    } finally {
      setDownloading(null);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Collected Job Data</h2>
      <p style={styles.subtitle}>
        Download CSV files containing collected job postings
      </p>

      {error && <div style={styles.errorMessage}>{error}</div>}

      {loading ? (
        <p style={styles.loading}>Loading CSV files...</p>
      ) : files.length === 0 ? (
        <div style={styles.emptyState}>
          <p style={styles.emptyText}>
            No CSV files collected yet. Add keywords to start collecting jobs!
          </p>
        </div>
      ) : (
        <div style={styles.tableContainer}>
          <table style={styles.table}>
            <thead>
              <tr style={styles.headerRow}>
                <th style={styles.headerCell}>Collection Date</th>
                <th style={styles.headerCell}>Job Count</th>
                <th style={styles.headerCell}>File Size</th>
                <th style={styles.headerCell}>Action</th>
              </tr>
            </thead>
            <tbody>
              {files.map((file, index) => (
                <tr key={index} style={styles.bodyRow}>
                  <td style={styles.cell}>
                    <div style={styles.timestamp}>
                      <div>{file.timestamp.split("T")[0]}</div>
                      <div style={styles.time}>
                        {file.timestamp.split("T")[1]?.substring(0, 5)}
                      </div>
                    </div>
                  </td>
                  <td style={styles.cell}>
                    <span style={styles.jobCount}>{file.job_count}</span>
                  </td>
                  <td style={styles.cell}>{formatFileSize(file.size)}</td>
                  <td style={styles.cell}>
                    <button
                      onClick={() => handleDownload(file.filename)}
                      disabled={downloading === file.filename}
                      style={styles.downloadBtn}
                      title="Download CSV file"
                    >
                      {downloading === file.filename
                        ? "Downloading..."
                        : "Download"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Info box */}
      <div style={styles.infoBox}>
        <strong>CSV File Contents:</strong>
        <div style={styles.fieldsList}>
          • Job Title<br />
          • Company Name<br />
          • Location<br />
          • Diploma Required<br />
          • Years of Experience<br />
          • Job Posting Link<br />
          • Posted Date<br />
          • Description (first 500 characters)<br />
        </div>
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
  errorMessage: {
    padding: "10px",
    backgroundColor: "#ffebee",
    color: "#c62828",
    borderRadius: "4px",
    marginBottom: "10px",
    fontSize: "14px",
  },
  loading: {
    color: "#666",
    fontSize: "14px",
    textAlign: "center" as const,
    padding: "20px",
  },
  emptyState: {
    textAlign: "center" as const,
    padding: "30px 20px",
    backgroundColor: "white",
    borderRadius: "6px",
    border: "1px solid #ddd",
  },
  emptyText: {
    color: "#999",
    fontSize: "14px",
    margin: "0",
  },
  tableContainer: {
    overflowX: "auto" as const,
    marginBottom: "15px",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse" as const,
    backgroundColor: "white",
    borderRadius: "6px",
    overflow: "hidden",
    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
  },
  headerRow: {
    backgroundColor: "#f5f5f5",
    borderBottom: "2px solid #ddd",
  },
  headerCell: {
    padding: "12px",
    textAlign: "left" as const,
    fontWeight: "600",
    fontSize: "13px",
    color: "#555",
  },
  bodyRow: {
    borderBottom: "1px solid #eee",
  },
  cell: {
    padding: "12px",
    fontSize: "13px",
    color: "#333",
  },
  keywordTag: {
    display: "inline-block",
    backgroundColor: "#e3f2fd",
    color: "#1565c0",
    padding: "4px 8px",
    borderRadius: "4px",
    fontSize: "12px",
    fontWeight: "500",
  },
  timestamp: {
    fontSize: "13px",
  },
  time: {
    fontSize: "11px",
    color: "#999",
    marginTop: "2px",
  },
  jobCount: {
    display: "inline-block",
    backgroundColor: "#fff3e0",
    color: "#e65100",
    padding: "4px 8px",
    borderRadius: "4px",
    fontSize: "12px",
    fontWeight: "600",
  },
  downloadBtn: {
    padding: "6px 12px",
    backgroundColor: "#2196F3",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: "500",
  },
  infoBox: {
    backgroundColor: "white",
    border: "1px solid #ddd",
    borderRadius: "6px",
    padding: "12px",
    fontSize: "13px",
    color: "#555",
    lineHeight: "1.6",
  },
  fieldsList: {
    marginTop: "8px",
    marginLeft: "0",
    lineHeight: "1.8",
  },
};
