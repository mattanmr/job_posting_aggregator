from fastapi import FastAPI
from .api import router
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from .scheduler import init_scheduler, scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_scheduler()
    print("Background scheduler started for job collection every 12 hours")
    yield
    # Shutdown
    if scheduler.running:
        scheduler.shutdown()
        print("Background scheduler shut down")


app = FastAPI(
    title="Job Posting Aggregator",
    lifespan=lifespan
)

app.include_router(router, prefix="")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
