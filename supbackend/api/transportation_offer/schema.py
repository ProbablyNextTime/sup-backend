from marshmallow import fields as f
from marshmallow_enum import EnumField
from supbackend.api.schema import BaseSchema
from supbackend.model.constant import TransportationOfferStatus, PaymentStatus


class TransportationOfferSchema(BaseSchema):
    status = EnumField(TransportationOfferStatus)
    title = f.String()
    transportationProvider = f.String(attribute="transportation_provider.name")
    payment_status = EnumField(PaymentStatus, dump_only=True)
    deposit_value_in_usd = f.Integer()
