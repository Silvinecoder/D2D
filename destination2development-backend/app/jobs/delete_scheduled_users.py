from app.core.database import SessionLocal

from app.services.user_auth0_service import Auth0Service
from app.services.user_service import UserService


def run():

    session = SessionLocal()

    try:

        auth0 = Auth0Service()
        users = UserService(session)

        expired = users.get_users_ready_for_deletion()

        for user in expired:

            auth0.delete_user(
                user.auth0_id,
            )

            users.permanently_delete_user(
                user.id,
            )

        session.commit()

    finally:

        session.close()


if __name__ == "__main__":
    run()