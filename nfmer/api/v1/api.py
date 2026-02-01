import uvicorn
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from nfmer.api.v1.routers import composers, compositions, events, pages

STATIC_DIR = Path(__file__).parent.parent / "static"

api = FastAPI(title="NFMer API", version="v1")

api.include_router(events.router)
api.include_router(compositions.router)
api.include_router(composers.router)
api.include_router(pages.router)

api.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if __name__ == "__main__":
    uvicorn.run("api:api", host="0.0.0.0", port=8000, reload=True)
