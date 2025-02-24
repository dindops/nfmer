import uvicorn
from fastapi import FastAPI

from nfmer.api.v1.routers import events

api = FastAPI(title="NFMer API", version="v1")

api.include_router(events.router)

if __name__ == "__main__":
    uvicorn.run("api:api", host="127.0.0.1", port=8000, reload=True)
