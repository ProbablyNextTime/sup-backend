from marshmallow import fields as f

from supbackend.api.schema import BaseSchema


class UserSchema(BaseSchema):
    name = f.Str()
