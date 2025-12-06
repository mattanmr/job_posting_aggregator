import Search from "./components/Search";

export default function App() {
  return (
    <div style={{ padding: "24px", fontFamily: "Arial, sans-serif", backgroundColor: "#fafafa", minHeight: "100vh" }}>
      <header style={{ marginBottom: "32px", borderBottom: "2px solid #0066cc", paddingBottom: "16px" }}>
        <h1 style={{ margin: "0 0 8px 0", color: "#333" }}>Job Posting Aggregator</h1>
        <p style={{ margin: 0, color: "#666", fontSize: "14px" }}>
          Search job postings from multiple sources in one place
        </p>
      </header>
      <Search />
    </div>
  );
}
