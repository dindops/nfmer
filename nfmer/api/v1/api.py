import uvicorn
from fastapi import FastAPI

from nfmer.api.v1.routers import composers, compositions, events

api = FastAPI(title="NFMer API", version="v1")

api.include_router(events.router)
api.include_router(compositions.router)
api.include_router(composers.router)

if __name__ == "__main__":
    uvicorn.run("api:api", host="0.0.0.0", port=8000, reload=True)
