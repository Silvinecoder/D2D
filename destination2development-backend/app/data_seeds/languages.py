from app.core.database import SessionLocal
from app.models.language import Language
from app.services.language import LanguageService


DEFAULT_LANGUAGES = [
    {
        "code": "en",
        "name": "English",
    },
    {
        "code": "pt",
        "name": "Portuguese",
    },
    {
        "code": "es",
        "name": "Spanish",
    },
    {
        "code": "fr",
        "name": "French",
    },
]


def seed_languages():
    session = SessionLocal()

    try:
        service = LanguageService(session)

        for item in DEFAULT_LANGUAGES:
            existing = service.get_by_code(item["code"])

            if existing:
                continue

            session.add(
                Language(
                    code=item["code"],
                    name=item["name"],
                )
            )

        session.commit()

    finally:
        session.close()


if __name__ == "__main__":
    seed_languages()
