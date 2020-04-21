from jetkit.db.extid import ExtID
from sqlalchemy import Integer, ForeignKey

from supbackend.db import db


class OfferTag(db.Model, ExtID):
    transportation_tag_id = db.Column(
        Integer, ForeignKey("transportation_tag.id", ondelete="CASCADE"), nullable=False
    )
    transportation_tag = db.relationship("TransportationTag")
    transportation_offer_id = db.Column(
        Integer,
        ForeignKey("transportation_offer.id", ondelete="CASCADE"),
        nullable=False,
    )
    transportation_offer = db.relationship("TransportationOffer")


OfferTag.add_create_uuid_extension_trigger()
