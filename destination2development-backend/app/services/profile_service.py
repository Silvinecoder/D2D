from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.models.user import User


class ProfileNotFoundError(Exception):
    pass


class ProfileAlreadyExistsError(Exception):
    pass


class ProfileService:
    def __init__(self, session: Session):
        self.session = session

    def create_profile(self, user: User) -> Profile:
        existing = self.get_by_user_id(user.id)

        if existing:
            raise ProfileAlreadyExistsError()

        profile = Profile(user_id=user.id)

        self.session.add(profile)
        self.session.flush()

        return profile

    def get_by_user_id(self, user_id: uuid.UUID) -> Profile | None:
        stmt = select(Profile).where(Profile.user_id == user_id)

        return self.session.execute(stmt).scalar_one_or_none()

    def get_profile_or_raise(self, user_id: uuid.UUID) -> Profile:
        profile = self.get_by_user_id(user_id)

        if profile is None:
            raise ProfileNotFoundError()

        return profile

    def update_profile(
        self,
        user_id: uuid.UUID,
        *,
        qualification: str | None = None,
        date_of_birth: date | None = None,
        gender: str | None = None,
        city: str | None = None,
        education_level: str | None = None,
    ) -> Profile:

        profile = self.get_profile_or_raise(user_id)

        if qualification is not None:
            profile.qualification = qualification

        if date_of_birth is not None:
            profile.date_of_birth = date_of_birth

        if gender is not None:
            profile.gender = gender

        if city is not None:
            profile.city = city

        if education_level is not None:
            profile.education_level = education_level

        return profile
