from jetkit.db.extid import ExtID
from jetkit.db.model import TSTZ
from sqlalchemy import Text, Integer, ForeignKey, Enum
from supbackend.db import db
from supbackend.model.constant import (
    TransportationOfferStatus,
    PaymentStatus,
    TransportationTarget,
)


class TransportationOffer(db.Model, ExtID):
    """Transportation offer about transporting cargo/people, includes delivery and price details."""

    title = db.Column(Text)
    departure_point = db.Column(Text)
    destination_point = db.Column(Text)
    departure_date = db.Column(TSTZ)
    arrival_date = db.Column(TSTZ)
    pickup_place = db.Column(Text)
    delivery_place = db.Column(Text)
    additional_info = db.Column(Text)
    transfer_number = db.Column(Text)
    transportation_target = db.Column(
        db.Enum(TransportationTarget), nullable=False, server_default="cargo"
    )
    cargo_id = db.Column(Integer, ForeignKey("cargo.id", ondelete="SET NULL"))
    cargo = db.relationship("Cargo", back_populates="transportation_offers")
    transportation_tags = db.relationship(
        "TransportationTag",
        secondary="offer_tag",
        back_populates="transportation_offers",
    )

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


TransportationOffer.add_create_uuid_extension_trigger()
