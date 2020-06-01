from jetkit.db.extid import ExtID
from sqlalchemy import Text, Index

from supbackend.db import db


class TransportationTag(db.Model, ExtID):
    name = db.Column(Text, nullable=False, unique=False)
    transportation_offers = db.relationship(
        "TransportationOffer",
        secondary="offer_tag",
        back_populates="transportation_tags",
    )

    transportation_tag_name_idx = Index("transportation_tag_name_idx", name)

    @classmethod
    def upsert(cls, *, name: str):
        return cls.upsert_row(
            row_class=cls,
            index_elements=["name"],
            set_=dict(name=name),
            values=dict(name=name),
        )


TransportationTag.add_create_uuid_extension_trigger()
