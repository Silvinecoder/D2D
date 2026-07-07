from fastapi import FastAPI

import app.models

from app.endpoints import users, users_unlock_request


app = FastAPI(
    title="Destination2Development API",
)

app.include_router(users.router)
app.include_router(users_unlock_request.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
