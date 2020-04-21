from marshmallow import fields as f
from supbackend.api.schema import BaseSchema


class CargoSchema(BaseSchema):
    name = f.Str()
