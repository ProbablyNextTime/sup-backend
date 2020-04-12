from jetkit.db.extid import ExtID
from sqlalchemy import Text, Integer, ForeignKey, Enum

from supbackend.db import db
from supbackend.model.constant import TransportationOfferStatus, PaymentStatus


class TransportationOffer(db.Model, ExtID):
    title = db.Column(Text)
    transportation_provider_id = db.Column(
        Integer, ForeignKey("transportation_provider.id", ondelete="SET NULL")
    )
    transportation_provider = db.relationship(
        "TransportationProvider", back_populates="transportation_offers"
    )
    status = db.Column(
        Enum(TransportationOfferStatus), nullable=False, server_default="opened"
    )
    payment_status = db.Column(
        db.Enum(PaymentStatus), nullable=False, server_default="not_paid"
    )
    price_per_unit_in_usd = db.Column(Integer)

    deposit_value_in_usd = db.Column(Integer, nullable=False)

    stripe_checkout_session_id = db.Column(Text)
    stripe_payment_intent_id = db.Column(Text)

    def get_stripe_line_item(self):
        """Create the offer our clients will pay for."""
        return {
            "name": "Services",
            "description": f"SUP transportation: {self.title}",
            "amount": self.get_charge_amount_cents(),
            "currency": "usd",
            "quantity": 1,
        }

    def get_charge_amount_cents(self) -> int:
        """Convert to cents."""
        return self.deposit_value_in_usd * 100
