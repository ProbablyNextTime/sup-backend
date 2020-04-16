from jetkit.db.extid import ExtID
from sqlalchemy import Integer, ForeignKey
from supbackend.db import db


class CustomerOffer(db.Model, ExtID):
    """Assign transportation_offer to customers and vice-versa."""

    customer_id = db.Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))

    transportation_offer_id = db.Column(
        Integer, ForeignKey("transportation_offer.id", ondelete="CASCADE")
    )
