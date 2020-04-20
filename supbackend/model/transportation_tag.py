from jetkit.db.extid import ExtID
from sqlalchemy import Text

from supbackend.db import db


class TransportationTag(db.Model, ExtID):
    name = db.Column(Text, nullable=False, unique=False)
    transportation_offers = db.relationship(
        "TransportationOffer",
        secondary="offer_tag",
        back_populates="transportation_tags",
    )


TransportationTag.add_create_uuid_extension_trigger()
