from fastapi import FastAPI

import app.models

from app.endpoints import (
    profile_documents,
    profiles,
    users,
    users_unlock_request,
)

app = FastAPI(
    title="Destination2Development API",
)

app.include_router(users.router)
app.include_router(users_unlock_request.router)
app.include_router(profiles.router)
app.include_router(profile_documents.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
