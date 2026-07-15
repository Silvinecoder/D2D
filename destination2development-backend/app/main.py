from fastapi import FastAPI

import app.models

import app.handler.notification

from app.endpoints import (
    notification,
    support_ticket,
    message_thread,
    message_thread_participant,
    message,
    profile_language,
    language,
    document_access_request,
    profile_document,
    profile,
    user,
    users_unlock_request,
)

app = FastAPI(
    title="Destination2Development API",
)

app.include_router(user.router)
app.include_router(users_unlock_request.router)
app.include_router(profile.router)
app.include_router(profile_document.router)
app.include_router(document_access_request.router)
app.include_router(language.router)
app.include_router(profile_language.router)
app.include_router(message.router)
app.include_router(message_thread_participant.router)
app.include_router(message_thread.router)
app.include_router(support_ticket.router)
app.include_router(notification.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
