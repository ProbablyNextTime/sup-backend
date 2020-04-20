from marshmallow import fields as f
from marshmallow_enum import EnumField

from supbackend.api.cargo.schema import CargoSchema
from supbackend.api.schema import BaseSchema
from supbackend.api.transportation_provider.schema import TransportationProviderSchema
from supbackend.api.transportation_tag.schema import TransportationTagSchema
from supbackend.model.constant import (
    TransportationOfferStatus,
    PaymentStatus,
    TransportationTarget,
)


class TransportationOfferSchema(BaseSchema):
    title = f.Str()
    status = EnumField(TransportationOfferStatus)
    transportationProvider = f.Nested(TransportationProviderSchema)
    payment_status = EnumField(PaymentStatus, dump_only=True)
    deposit_value_in_usd = f.Integer()
    price_per_unit_in_usd = f.Integer()
    departure_point = f.Str()
    destination_point = f.Str()
    departure_date = f.DateTime()
    arrival_date = f.DateTime()
    pickup_place = f.Str()
    delivery_place = f.Str()
    additional_info = f.Str()
    transfer_number = f.Str()
    transportation_target = EnumField(TransportationTarget)
    cargo = f.Nested(CargoSchema)
    transportation_tags = f.Nested(TransportationTagSchema(many=True))
