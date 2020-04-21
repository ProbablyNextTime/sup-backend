from marshmallow import fields as f
from supbackend.api.schema import BaseSchema


class TransportationTagSchema(BaseSchema):
    name = f.Str()
