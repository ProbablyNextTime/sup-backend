import uuid
from typing import List

from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from flask_crud import ResourceView, CollectionView
from jetkit.api import CursorPage, combined_search_by, sortable_by
from sqlalchemy.orm import joinedload

from supbackend.api.transportation_offer.schema import (
    TransportationOfferSchema,
    UpdateTransportationOfferSchema,
    CreateTransportationOfferSchema,
)
from supbackend.db import db
from supbackend.model import (
    TransportationOffer,
    Cargo,
    TransportationTag,
    TransportationProvider,
)
from supbackend.model.constant import PaymentStatus
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
        TransportationProvider.name,
        search_parameter_name="query",
    )
    @sortable_by(TransportationOffer.arrival_date, TransportationOffer.departure_date)
    @jwt_required
    def get(self) -> List[TransportationOffer]:
        """Get a paginated list of transportation offers."""
        return (
            TransportationOffer.query.filter(
                TransportationOffer.payment_status == PaymentStatus.not_paid,
                TransportationOffer.deposit_value_in_usd.isnot(None),
            )
            .join(OfferTag)
            .join(TransportationTag)
            .join(Cargo)
            .join(TransportationProvider)
            .options(
                joinedload(TransportationOffer.transportation_tags),
                joinedload(TransportationOffer.cargo),
                joinedload(TransportationOffer.transportation_provider),
            )
        )

    @blp.arguments(CreateTransportationOfferSchema)
    @blp.response(TransportationOfferSchema)
    @jwt_required
    def post(self, args: dict) -> TransportationOffer:
        """Create a transportation offer."""
        print(args)
        cargo = Cargo(name=args.get("cargo"))
        transportation_offer = TransportationOffer(
            transfer_number=uuid.uuid4().hex,
            departure_date=args.get("departure_date"),
            arrival_date=args.get("arrival_date"),
            pickup_place=args.get("pickup_place"),
            delivery_place=args.get("delivery_place"),
            price_per_unit_in_usd=args.get("price_per_unit_in_usd"),
            departure_point=args.get("departure_point"),
            destination_point=args.get("destination_point"),
            cargo=cargo,
            transportation_target=args.get("transportation_target"),
        )

        db.session.add(cargo)
        db.session.add(transportation_offer)

        for tag in args.get("transportation_tags"):  # type:ignore
            to_be_added_tag: TransportationTag = TransportationTag.query.filter(
                TransportationTag.name == tag.get("name")
            ).one_or_none()
            offer_tag = OfferTag(
                transportation_offer=transportation_offer,
                transportation_tag=to_be_added_tag,
            )
            db.session.add(offer_tag)

        db.session.commit()

        return transportation_offer


@blp.route("/<string:pk>")
class TransportationOfferView(ResourceView):
    model = TransportationOffer()
    get_enabled: bool = True
    update_enabled: bool = True

    def _lookup(self, pk):
        """Get model by external key."""
        item = self.model.query.filter_by(extid=pk).one_or_none()
        if not item:
            abort(404)
        return item

    @blp.response(TransportationOfferSchema)
    @jwt_required
    def get(self, pk: str) -> TransportationOffer:
        """Get a single offer."""
        return super().get(pk)

    @blp.arguments(UpdateTransportationOfferSchema)
    @blp.response(TransportationOfferSchema)
    @jwt_required
    def patch(self, args: dict, pk: str) -> TransportationOffer:
        """Update transportation offer."""
        return super().patch(args=args, pk=pk)

    @blp.response()
    @jwt_required
    def delete(self, pk: str):
        """Delete transportation offer."""
        return super().delete(pk)
