from jetkit.db.extid import ExtID
from sqlalchemy import Text

from supbackend.db import db


class Cargo(db.Model, ExtID):
    name = db.Column(Text, nullable=False, unique=True)
    transportation_offers = db.relationship(
        "TransportationOffer", back_populates="cargo"
    )

    @classmethod
    def upsert(cls, *, name: str):
        """Upsert cargo."""
        return cls.upsert_row(
            row_class=cls,
            index_elements=["name"],
            set_=dict(name=name),
            values=dict(name=name),
        )


Cargo.add_create_uuid_extension_trigger()
