from jetkit.db.extid import ExtID
from sqlalchemy import Integer, ForeignKey, Index
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

    idx_unique_offer_tag = Index(
        "unique_offer_tag_idx",
        transportation_offer_id,
        transportation_tag_id,
        unique=True,
    )

    @classmethod
    def upsert(
        cls, *, transportation_offer_id: int, transportation_tag_id: int,
    ):
        values = dict(
            transportation_offer_id=transportation_offer_id,
            transportation_tag_id=transportation_tag_id,
        )
        return cls.upsert_row(
            row_class=cls,
            index_elements=["transportation_tag_id", "transportation_offer_id"],
            set_=values,
            values=values,
        )


OfferTag.add_create_uuid_extension_trigger()
