from marshmallow import fields as f

from supbackend.api.schema import BaseSchema


class ReviewSchema(BaseSchema):
    review_text = f.Str(required=True)
