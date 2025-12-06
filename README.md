# Job Posting Aggregator

A clean, minimal job posting aggregator with Python FastAPI backend and React/TypeScript frontend.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Run with Docker Compose

```bash
docker-compose up --build
```

Then open:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

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

- Search jobs by keyword
- Mock data source built-in
- Extensible connector architecture for adding real sources (Adzuna, LinkedIn, etc.)
- RESTful API with FastAPI
- Modern React UI with TypeScript
- Docker-ready setup

## API Endpoints

- `GET /search?q=<keyword>` - Search for jobs
- `GET /health` - Health check
- `GET /docs` - Swagger documentation

## Next Steps

- Add real job source connectors (Adzuna API, LinkedIn, etc.)
- Add filtering (location, salary, date range)
- Add job details page
- Add saved jobs/favorites
- Improve UI/UX
- Add authentication
