# Job Posting Aggregator

A comprehensive job posting aggregator with automated job collection, keyword management, and CSV data storage. Built with Python FastAPI backend and React/TypeScript frontend.

## Features

### Core Features
- **Real-time job search** - Search jobs by keyword, location, country, and language
- **Automated job collection** - Collect jobs every 12 hours for configured keywords
- **Keyword management** - Add/remove search keywords for automated collection
- **CSV storage** - Save collected jobs to CSV files with structured data
- **Collection status** - View countdown timer to next collection and last collection time
- **CSV viewer** - Browse and download collected job data
- **Multi-source integration** - Support for SerpAPI Google Jobs and mock data (fallback)
- **Extensible connector architecture** - Easy to add more job sources
- **Modern React UI** - TypeScript frontend with responsive design

### Data Collected
Each job posting includes:
- Job title
- Company name
- Location
- **Diploma/Education required** (parsed from job description)
- **Years of experience required** (parsed from job description)
- Job posting URL
- Posted date
- Job description

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
│   │   ├── connectors/           # Job source connectors
│   │   │   ├── base.py           # Base JobPosting and JobConnector classes
│   │   │   ├── mock_connector.py # Mock data for testing
│   │   │   └── serpapi_connector.py # SerpAPI integration
│   │   ├── data/                 # Data storage (generated at runtime)
│   │   │   ├── csv_files/        # Collected job CSV files
│   │   │   ├── keywords.json     # Configured keywords
│   │   │   └── collection_metadata.json # Collection timestamps
│   │   ├── api.py                # FastAPI routes
│   │   ├── main.py               # App setup with lifespan
│   │   ├── scheduler.py          # Background job scheduler
│   │   ├── schemas.py            # Pydantic models
│   │   ├── storage.py            # CSV and keyword storage operations
│   │   ├── utils.py              # Helpers
│   │   └── __init__.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── Search.tsx        # Manual job search
│   │   │   ├── KeywordManager.tsx # Add/remove keywords
│   │   │   ├── CollectionStatus.tsx # Collection countdown timer
│   │   │   └── CsvViewer.tsx     # View and download CSV files
│   │   ├── services/
│   │   │   └── api.ts            # API client with typed functions
│   │   ├── types/
│   │   │   └── index.ts          # TypeScript interfaces
│   │   ├── App.tsx               # Root component
│   │   └── index.tsx             # Entry point
│   ├── public/
│   ├── Dockerfile
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Job Search
- `GET /search` - Search for jobs
  - Query parameters:
    - `q` (required): Search keywords
    - `location` (optional): Location to search in (e.g., "New York", "London")
    - `gl` (optional): Country code (default: us) - e.g., us, uk, il
    - `hl` (optional): Language code (default: en) - e.g., en, es, he
    - `page` (optional): Page number (1-10)
  - Returns: Array of JobOut objects with title, company, location, diploma_required, years_experience, url, etc.

### Keyword Management
- `GET /api/keywords` - Get all configured keywords
  - Returns: `{ keywords: ["keyword1", "keyword2", ...] }`

- `POST /api/keywords` - Add a new keyword
  - Body: `{ "keyword": "Python Developer" }`
  - Returns: Updated keywords list

- `DELETE /api/keywords/{keyword}` - Remove a keyword
  - Returns: Updated keywords list

### CSV File Management
- `GET /api/csv-files` - List all collected CSV files
  - Returns: Array of CsvFileInfo objects with filename, keyword, timestamp, size, job_count

- `GET /api/csv-files/{filename}` - Download a specific CSV file
  - Returns: CSV file download

### Collection Status
- `GET /api/next-collection` - Get next collection time and status
  - Returns: CollectionStatus with next_collection_timestamp, last_collection_timestamp

### System
- `GET /health` - Health check
  - Returns: `{ "status": "ok" }`

- `GET /docs` - Swagger API documentation

## Scheduled Job Collection

Jobs are collected automatically every **12 hours** for all configured keywords.

### How it Works
1. Add keywords through the frontend "Job Search Keywords" section
2. The backend scheduler automatically collects jobs for all keywords every 12 hours
3. Collected jobs are stored in CSV files in `backend/app/data/csv_files/`
4. View the countdown timer on the "Job Collection Status" section
5. Download collected CSV files from "Collected Job Data" section

### Collection Data
Each CSV file contains:
- Job Title
- Company Name
- Location
- Diploma Required (parsed from job description using regex patterns)
- Years of Experience (parsed from job description using regex patterns)
- Job URL
- Posted Date
- Description (first 500 characters)

## Architecture

### Backend (FastAPI)
- **Modular Connector System**: Abstract `JobConnector` base class with implementations for different job sources
- **APScheduler Integration**: Background scheduler for 12-hour job collection cycles
- **CSV Storage**: Persistent storage of collected jobs with timestamp and keyword organization
- **Keyword Management**: JSON-based keyword configuration
- **Regex Parsing**: Extracts education and experience requirements from job descriptions

### Frontend (React + TypeScript)
- **Component-based**: Modular React components for each feature
- **Real-time Updates**: 12-hour countdown timer updates every second
- **API Service Layer**: Typed axios client with dedicated functions for each API operation
- **Error Handling**: Comprehensive error messages and loading states
- **Responsive Design**: Mobile-friendly layout using inline styles

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
If no API key is configured, or if SerpAPI returns no results, the app falls back to mock data for testing and demonstration purposes.

## Development Notes

### Adding New Job Sources
To add a new job source:
1. Create a new connector class in `backend/app/connectors/` extending `JobConnector`
2. Implement the `search()` method returning a list of `JobPosting` objects
3. Update the scheduled collection in `backend/app/scheduler.py` to use the new connector
4. The connector will be automatically integrated into both manual search and scheduled collection

### Parsing Education and Experience
The backend uses regex patterns to extract education and experience requirements from job descriptions:

**Education patterns** (in `serpapi_connector.py`):
- PhD/Doctorate
- Master's Degree
- Bachelor's Degree
- Associate's Degree
- High School Diploma

**Experience patterns**:
- "3-5 years" → "3-5 years"
- "5+ years" → "5+ years"
- "minimum of 3 years" → "3+ years"
- "at least 5 years" → "5+ years"

### Environment Variables
- `FASTAPI_PORT` - Backend port (default: 8000)
- `SERPAPI_KEY` - SerpAPI authentication key (optional)
- `REACT_APP_API_URL` - Frontend API URL (default: http://localhost:8000)
- `PYTHONUNBUFFERED` - Python unbuffered output (set to 1)

## Troubleshooting

### Jobs not being collected
- Check that keywords are added in the frontend
- Verify backend is running: `docker-compose logs backend`
- Check scheduler logs for errors
- Ensure at least one keyword is configured

### No jobs found in search
- Check keyword spelling
- Try a broader search term (e.g., "Developer" instead of "Python Developer")
- Verify SerpAPI key if configured
- Check backend logs for API errors

### CSV download not working
- Ensure backend `/api/csv-files` endpoint is accessible
- Check browser console for errors
- Verify CSV files were created in `backend/app/data/csv_files/`

### Scheduler not running
- Check that apscheduler is installed: `pip install apscheduler`
- Verify backend logs show scheduler startup message
- Ensure backend container has not crashed

## Future Enhancements

Potential improvements for future versions:
- Database integration (PostgreSQL) for persistent storage and querying
- Advanced filtering options (salary range, job type, etc.)
- Job bookmarking and saved searches
- Email notifications for new jobs
- Integration with more job sources (LinkedIn, Indeed, etc.)
- Manual refresh button for on-demand collection
- CSV file retention policies and cleanup
- Search history and analytics
- User authentication and profiles
- Rate limiting for API endpoints
