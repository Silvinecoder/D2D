from fastapi import FastAPI

import app.models

from app.endpoints import (
    notifications,
    message_threads,
    message_thread_participants,
    messages,
    profile_languages,
    languages,
    documents_access_request,
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
app.include_router(documents_access_request.router)
app.include_router(languages.router)
app.include_router(profile_languages.router)
app.include_router(messages.router)
app.include_router(message_thread_participants.router)
app.include_router(message_threads.router)
app.include_router(notifications.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
