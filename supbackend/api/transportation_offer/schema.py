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
    transportation_provider = f.Nested(
        TransportationProviderSchema, data_key="transportationProvider"
    )
    payment_status = EnumField(PaymentStatus, dump_only=True, data_key="paymentStatus")
    deposit_value_in_usd = f.Integer(data_key="depositValueInUsd")
    price_per_unit_in_usd = f.Integer(data_key="pricePerUnitInUsd")
    departure_point = f.Str(data_key="departurePoint")
    destination_point = f.Str(data_key="destinationPoint")
    departure_date = f.DateTime(data_key="departureDate")
    arrival_date = f.DateTime(data_key="arrivalDate")
    pickup_place = f.Str(data_key="pickupPlace")
    delivery_place = f.Str(data_key="deliveryPlace")
    additional_info = f.Str(data_key="additionalInfo")
    transfer_number = f.Str(data_key="transferNumber")
    is_premium = f.Bool(data_key="isPremium")
    transportation_target = EnumField(
        TransportationTarget, data_key="transportationTarget"
    )
    cargo = f.Nested(CargoSchema)
    transportation_tags = f.Nested(
        TransportationTagSchema(many=True), data_key="transportationTags"
    )


class CreateTransportationOfferSchema(BaseSchema):
    departure_date = f.DateTime()
    arrival_date = f.DateTime()
    pickup_place = f.Str()
    delivery_place = f.Str()
    price_per_unit_in_usd = f.Integer()
    cargo = f.Str()
    transportation_tags = f.Nested(TransportationTagSchema(many=True), data_key="tags")
    departure_point = f.Str()
    destination_point = f.Str()
    transportation_target = EnumField(TransportationTarget)


class UpdateTransportationOfferSchema(BaseSchema):
    deposit_value_in_usd = f.Integer()
