from fastapi import FastAPI

from app.database import init_db

app = FastAPI(title="Smart Score Backend")


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()


@app.get("/health")
async def health_check():
    return {"status": "ok"}
