from marshmallow import fields as f
from supbackend.api.schema import BaseSchema


class TransportationProviderSchema(BaseSchema):
    name = f.Str()
