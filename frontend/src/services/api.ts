import axios from "axios";

const base = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default axios.create({ baseURL: base });
