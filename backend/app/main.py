from fastapi import FastAPI
from .api import router
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Job Posting Aggregator")
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
