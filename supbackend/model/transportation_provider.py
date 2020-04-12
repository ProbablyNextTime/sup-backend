import os

import stripe
from jetkit.db.extid import ExtID
from sqlalchemy import Text

from supbackend.db import db


class TransportationProvider(db.Model, ExtID):
    name = db.Column(Text, unique=True)
    transportation_offers = db.relationship(
        "TransportationOffer", back_populates="transportation_provider"
    )
    stripe_customer_id = db.Column(Text, unique=True)
    stripe_default_source_id = db.Column(Text, unique=True)
    stripe_customer_email = db.Column(Text, unique=True)

    @classmethod
    def create_transportation_provider(cls, name: str):
        """Create transportation provider."""
        return super().upsert_row(
            row_class=cls, index_elements=["name"], values=dict(name=name),
        )

    def vivify_stripe_customer(self):
        """Create a stripe customer if it doesn't already exist."""
        if self.stripe_customer_id:
            return

        description = f"id={self.id}"
        stage = os.getenv("STAGE", "unknown")  # noqa: F841
        params = dict(description=description)

        if self.name:
            params["name"] = self.name
        cust = stripe.Customer.create(**params)
        self.stripe_customer_id = cust.id


TransportationProvider.add_create_uuid_extension_trigger()
