import KeywordManager from "./components/KeywordManager";
import CollectionStatus from "./components/CollectionStatus";
import SchedulingConfig from "./components/SchedulingConfig";
import CsvViewer from "./components/CsvViewer";

export default function App() {
  return (
    <div
      style={{
        padding: "24px",
        fontFamily: "Arial, sans-serif",
        backgroundColor: "#fafafa",
        minHeight: "100vh",
      }}
    >
      <header
        style={{
          marginBottom: "32px",
          borderBottom: "2px solid #0066cc",
          paddingBottom: "16px",
        }}
      >
        <h1 style={{ margin: "0 0 8px 0", color: "#333" }}>
          Job Posting Aggregator
        </h1>
        <p style={{ margin: 0, color: "#666", fontSize: "14px" }}>
          Search job postings and set up automated collection with keyword management
        </p>
      </header>
      {/* Row 1: Keywords + Collection Status */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))",
          gap: "20px",
          alignItems: "start",
          marginBottom: "20px",
        }}
      >
        <section>
          <KeywordManager />
        </section>
        <section>
          <CollectionStatus />
        </section>
      </div>

      {/* Row 2: Scheduling + CSV Viewer */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))",
          gap: "20px",
          alignItems: "start",
          marginBottom: "20px",
        }}
      >
        <section>
          <SchedulingConfig />
        </section>
        <section>
          <CsvViewer />
        </section>
      </div>
    </div>
  );
}
