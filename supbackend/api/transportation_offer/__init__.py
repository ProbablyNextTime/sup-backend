from flask_smorest import Blueprint, abort
from flask_crud import ResourceView, CollectionView
from jetkit.api import CursorPage, combined_search_by, sortable_by
from sqlalchemy.orm import joinedload

from supbackend.api.transportation_offer.schema import TransportationOfferSchema
from supbackend.model import TransportationOffer, Cargo, TransportationTag
from supbackend.model.many_to_many.offer_tag import OfferTag

blp = Blueprint(
    "Transportation_Offer", __name__, url_prefix="/api/transportation_offer"
)


@blp.route("")
class TransportationOfferCollection(CollectionView):
    model = TransportationOffer

    list_enabled = True
    create_enabled = True

    @blp.response(TransportationOfferSchema(many=True))
    @blp.paginate(CursorPage)
    @combined_search_by(
        TransportationOffer.title,
        TransportationOffer.departure_point,
        TransportationOffer.destination_point,
        TransportationTag.name,
        Cargo.name,
        search_parameter_name="query",
    )
    @sortable_by(TransportationOffer.arrival_date, TransportationOffer.departure_date)
    def get(self):
        return (
            TransportationOffer.query.join(OfferTag)
            .join(TransportationTag)
            .join(Cargo)
            .options(joinedload(TransportationOffer.transportation_tags))
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
        return super().get(pk)
