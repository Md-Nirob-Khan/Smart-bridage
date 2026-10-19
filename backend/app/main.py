"""FastAPI entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import config, models  # noqa: F401  (models import registers tables)
from app.database import Base, engine
from app.routers import auth_router, bridge_router

for _dir in (config.UPLOAD_DIR, config.RESULTS_DIR, config.WEIGHTS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartBridge AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(bridge_router.router)

# Original and annotated images are served as static files.
app.mount("/uploads", StaticFiles(directory=config.UPLOAD_DIR), name="uploads")
app.mount("/results", StaticFiles(directory=config.RESULTS_DIR), name="results")


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok", "model_trained": config.MODEL_PATH.exists()}
