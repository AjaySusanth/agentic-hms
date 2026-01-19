from fastapi import FastAPI

from agents.registration.router import router as registration_router
from agents.queue.router import router as queue_router
app = FastAPI(
    title="HMS Multi-Agent API",
    version="1.0.0"
)

app.include_router(registration_router, prefix="/api")
app.include_router(queue_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
