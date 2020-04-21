from jetkit.db.extid import ExtID
from sqlalchemy import Integer, ForeignKey, Text

from supbackend.db import db


class ProviderReview(db.Model, ExtID):
    reviewer_id = db.Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    reviewed_id = db.Column(
        Integer,
        ForeignKey("transportation_provider.id", ondelete="CASCADE"),
        nullable=False,
    )
    review_text = db.Column(Text, nullable=False)
    reviewed = db.relationship(
        "TransportationProvider",
        back_populates="reviews_received",
        foreign_keys="ProviderReview.reviewed_id",
        uselist=False,
    )
    reviewer = db.relationship(
        "User",
        back_populates="reviews_given",
        foreign_keys="ProviderReview.reviewer_id",
        uselist=False,
    )
