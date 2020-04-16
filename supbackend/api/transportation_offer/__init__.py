from flask_smorest import Blueprint, abort
from flask_crud import ResourceView

from supbackend.api.transportation_offer.schema import TransportationOfferSchema
from supbackend.model import TransportationOffer

blp = Blueprint(
    "Transportation_Offer", __name__, url_prefix="/api/transportation_offer"
)


@blp.route("/<string:pk>")
class TransportationOfferView(ResourceView):
    model = TransportationOffer
    get_enabled: bool = True
    update_enabled: bool = True

    def _lookup(self, pk):
        """Get model by external key."""
        item = self.model.query.filter_by(extid=pk).one_or_none()
        if not item:
            abort(404)
        return item

    @blp.response(TransportationOfferSchema)
    def get(self, pk: str):
        """Get a single offer."""
        return TransportationOffer.get_by_extid(pk)
