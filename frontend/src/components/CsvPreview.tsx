import React, { useEffect, useState } from "react";
import { getCsvPreview } from "../services/api";
import "../styles/CsvPreview.css";

interface CsvPreviewProps {
  filename: string;
  isOpen: boolean;
  onClose: () => void;
}

interface PreviewData {
  filename: string;
  headers: string[];
  rows: Record<string, string>[];
  total_rows: number;
  has_more: boolean;
}

const CsvPreview: React.FC<CsvPreviewProps> = ({
  filename,
  isOpen,
  onClose,
}) => {
  const [data, setData] = useState<PreviewData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    const loadPreview = async () => {
      setLoading(true);
      setError(null);
      try {
        const preview = await getCsvPreview(filename, 100);
        setData(preview);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load preview"
        );
      } finally {
        setLoading(false);
      }
    };

    loadPreview();
  }, [filename, isOpen]);

  if (!isOpen) return null;

  return (
    <div className="csv-preview-overlay" onClick={onClose}>
      <div className="csv-preview-modal" onClick={(e) => e.stopPropagation()}>
        <div className="csv-preview-header">
          <h2>Preview: {filename}</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="csv-preview-content">
          {loading && <div className="loading">Loading preview...</div>}

          {error && (
            <div className="error-message">
              Error loading preview: {error}
            </div>
          )}

          {data && (
            <>
              <div className="preview-info">
                <p>
                  Showing {data.total_rows} rows
                  {data.has_more && " (first 100 rows shown)"}
                </p>
              </div>

              <div className="csv-table-container">
                <table className="csv-table">
                  <thead>
                    <tr>
                      {data.headers.map((header) => (
                        <th key={header}>{header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.rows.map((row, idx) => (
                      <tr key={idx}>
                        {data.headers.map((header) => (
                          <td
                            key={`${idx}-${header}`}
                            className={
                              header === "keyword"
                                ? "keyword-cell"
                                : ""
                            }
                          >
                            {header === "url" ? (
                              <a 
                                href={row[header]} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                style={{color: "#0284c7", textDecoration: "underline"}}
                              >
                                {row[header]?.substring(0, 50)}...
                              </a>
                            ) : header === "description"
                              ? (row[header] || "").substring(0, 100) + "..."
                              : row[header] || "—"}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {data.has_more && (
                <div className="preview-notice">
                  Note: Preview shows first 100 rows. Download to see all data.
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default CsvPreview;
