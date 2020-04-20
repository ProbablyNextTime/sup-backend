from jetkit.db.extid import ExtID
from sqlalchemy import Text

from supbackend.db import db


class Cargo(db.Model, ExtID):
    name = db.Column(Text, nullable=False, unique=True)
    transportation_offers = db.relationship(
        "TransportationOffer", back_populates="cargo"
    )


Cargo.add_create_uuid_extension_trigger()
