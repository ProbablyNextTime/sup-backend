from marshmallow import fields as f

from supbackend.api.schema import BaseSchema


class UserSchema(BaseSchema):
    name = f.Str()
    email = f.Str()


class MeSchema(BaseSchema):
    email = f.Str()
