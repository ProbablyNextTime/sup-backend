from marshmallow import fields as f
from marshmallow.fields import String

from supbackend.api.review.schema import ReviewSchema
from supbackend.api.schema import BaseSchema


class TransportationProviderSchema(BaseSchema):
    name = f.Str()
    reviews_received = f.Nested(ReviewSchema(many=True), data_key="reviewsReceived")
    additional_details = f.List(String)
