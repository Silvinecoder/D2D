from fastapi import FastAPI

import app.models

from app.endpoints import users


app = FastAPI(
    title="Destination2Development API",
)

app.include_router(users.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
