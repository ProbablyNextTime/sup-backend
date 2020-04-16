from marshmallow import Schema, fields as f


class InitiateCheckoutResponse(Schema):
    session_id = f.Str()
