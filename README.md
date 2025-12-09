# Job Posting Aggregator

A clean, minimal job posting aggregator with Python FastAPI backend and React/TypeScript frontend.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- SerpAPI Key (optional, for real job data - get it from https://serpapi.com/ - free tier includes 100 searches/month)

### Setup

1. **Clone the repository**

2. **Configure API Keys (Optional)**
   ```bash
   cp .env.example .env
   # Edit .env and add your SerpAPI key
   ```
   
   If no API key is provided, the app will use mock data.

### Run with Docker Compose

**Linux/Mac:**
```bash
./start.sh
```

**Windows (with WSL + Docker):**
```powershell
.\start.ps1
```

**Or manually:**
```bash
docker-compose up --build
```

Then open:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

To stop:
```bash
docker-compose down
```

### Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
export PYTHONPATH=/path/to/backend
python -m uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
job_posting_aggregator/
├── backend/
│   ├── app/
│   │   ├── connectors/       # Job source connectors
│   │   ├── api.py            # FastAPI routes
│   │   ├── main.py           # App setup
│   │   ├── schemas.py        # Pydantic models
│   │   └── utils.py          # Helpers
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── public/
│   ├── Dockerfile
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Features

- **Search jobs by keyword and location**
- **Real job data from Google Jobs via SerpAPI** (with API key) or mock data (fallback)
- Supports multiple countries and languages (US, UK, Israel, etc.)
- Comprehensive job details including highlights, qualifications, and responsibilities
- Filter by job type, date posted, and more
- Extensible connector architecture for adding more sources
- RESTful API with FastAPI
- Modern React UI with TypeScript
- Docker-ready setup

## Data Sources

### SerpAPI Google Jobs (Primary)
The app integrates with [SerpAPI's Google Jobs API](https://serpapi.com/google-jobs-api) to provide real job listings aggregated by Google from thousands of sources worldwide.

**Features:**
- Global coverage with 195+ countries
- Multi-language support
- Job highlights and detailed descriptions
- Advanced filters (job type, date posted, etc.)
- Free tier: 100 searches/month
- Easy signup - no approval needed

**Setup:**
1. Sign up at https://serpapi.com/ (takes 30 seconds)
2. Get your API key from the dashboard
3. Add to `.env` file: `SERPAPI_KEY=your_key_here`
4. Restart the application

### Mock Data (Fallback)
If no API key is configured, or if SerpAPI returns no results, the app falls back to mock data for testing.

## API Endpoints

- `GET /search?q=<keyword>&location=<location>&gl=<country>&hl=<language>` - Search for jobs
  - Query parameters:
    - `q` (required): Search keywords
    - `location` (optional): Location to search in (e.g., "New York", "London")
    - `gl` (optional): Country code (default: us) - e.g., us, uk, il
    - `hl` (optional): Language code (default: en) - e.g., en, es, he
    - `page` (optional): Page number (1-10)
- `GET /health` - Health check
- `GET /docs` - Swagger documentation
