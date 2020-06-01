from flask_crud import CollectionView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from jetkit.api import CursorPage

from supbackend.api.transportation_tag.schema import TransportationTagSchema
from supbackend.model import TransportationTag

blp = Blueprint("Transportation_Tag", __name__, url_prefix="/api/transportation_tag")


@blp.route("")
class TransportationTagCollection(CollectionView):
    model = TransportationTag

    list_enabled = True
    create_enabled = True

    @blp.response(TransportationTagSchema(many=True))
    @blp.paginate(CursorPage)
    @jwt_required
    def get(self) -> TransportationTag:
        """Return a page of transportation tags."""
        return super().get()
