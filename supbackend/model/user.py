from enum import Enum, unique
from typing import Any, Mapping

from jetkit.db.extid import ExtID
from jetkit.model.user import CoreUser
from sqlalchemy import Column
from sqlalchemy.types import Text, Enum as SQLAEnum

from supbackend.db import db


@unique
class UserType(Enum):
    normal = "normal"


class User(db.Model, CoreUser, ExtID["User"]):
    _user_type = Column(
        SQLAEnum(UserType), nullable=False, server_default=UserType.normal.value
    )
    avatar_url = db.Column(Text())
    __mapper_args__: Mapping[str, Any] = {"polymorphic_on": _user_type}

    reviews_given = db.relationship(
        "ProviderReview",
        back_populates="reviewer",
        foreign_keys="ProviderReview.reviewer_id",
    )


User.add_create_uuid_extension_trigger()


class NormalUser(User):

    __mapper_args__ = {"polymorphic_identity": UserType.normal}
