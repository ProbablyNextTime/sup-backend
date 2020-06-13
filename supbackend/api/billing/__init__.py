import logging
import warnings
from pprint import pprint
import stripe
from flask import current_app, request
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from supbackend.api.billing.schema import InitiateCheckoutResponse
from supbackend.db import db
from supbackend.model import TransportationOffer
from supbackend.model.constant import PaymentStatus

blp = Blueprint("Billing", __name__, url_prefix="/api/billing")

METADATA_TRANSPORTATION_OFFER_EXTID_KEY = "transportation_offer_extid"

log = logging.getLogger(__name__)


@blp.route(
    "checkout/transportation_offer/<string:transportation_offer_extid>",
    methods=["POST"],
)
@blp.response(InitiateCheckoutResponse)
@jwt_required
def initiate_transportation_offer_checkout(transportation_offer_extid: str):
    """Create a stripe checkout session, that a user can use to purchase."""
    transportation_offer = TransportationOffer.get_by_extid(transportation_offer_extid)
    if not transportation_offer:
        abort(404, "Transportation Offer doesn't exist")

    if transportation_offer.payment_status == PaymentStatus.paid:
        abort(400, "Transportation Offer already paid")

    transportation_provider = transportation_offer.transportation_provider

    # create a stripe customer if we don't have one
    transportation_provider.vivify_stripe_customer()

    if not transportation_offer.deposit_value_in_usd:
        abort(400, "Nothing to be charged")

    # the customer'll be acquiring line items
    line_items = [transportation_offer.get_stripe_line_item()]

    params = {
        "cancel_url": current_app.config["UI_URL"],
        "success_url": current_app.config["UI_URL"] + "/thank-you",
        "payment_method_types": ["card"],  # accept only cards for now
        "billing_address_collection": "auto",
        "customer": transportation_provider.stripe_customer_id,
        # "customer_email": current_user.email,
        "line_items": line_items,
        "payment_intent_data": {
            "metadata": {
                # we can use this to verify a transaction when complete
                METADATA_TRANSPORTATION_OFFER_EXTID_KEY: transportation_offer.extid
            }
        },
    }

    # create the session object
    sess = stripe.checkout.Session.create(**params)

    # save the checkout session on transportation_offer so that we know what we're paying for
    transportation_offer.stripe_checkout_session_id = sess.id
    transportation_offer.stripe_payment_intent_id = sess.payment_intent
    db.session.commit()

    return {"session_id": sess.id}


@blp.route("webhook", methods=["POST"])
@blp.response()
def handle_stripe_webhook():
    try:
        sig_header = request.headers.get("STRIPE_SIGNATURE")
        secret = current_app.config["STRIPE_WEBHOOK_SECRET"]
        event = stripe.Webhook.construct_event(request.get_data(), sig_header, secret,)
    except (ValueError, stripe.webhook.error.SignatureVerificationError) as e:
        abort(400, message=f"Failed to verify request: {e}")
        return

    try:
        handle_stripe_event(event)
    except Exception as e:
        log.exception(e)
        abort(400, message=str(e))

    return "ok"


def handle_stripe_event(event: stripe.Event):
    log.info("Got stripe webhook event:")
    import pprint

    pprint.pprint(event)

    if event.type.startswith("payment_intent."):
        handle_payment_intent_event(event)


def handle_payment_intent_event(event: stripe.Event):
    if event.type != "payment_intent.succeeded":
        return

    # payment succeeded
    intent: stripe.PaymentIntent = event.data.object
    process_transportation_offer_payment(intent)
    pprint(intent)


def process_transportation_offer_payment(intent: stripe.PaymentIntent):
    # for now we are only processing payments for a single transp. offer
    # the offer extid is stored on the payment intent metadata
    meta = intent.metadata

    # try to find transportation_offer
    transportation_offer = None
    if METADATA_TRANSPORTATION_OFFER_EXTID_KEY in meta:
        transportation_offer_extid = meta[METADATA_TRANSPORTATION_OFFER_EXTID_KEY]
        transportation_offer = TransportationOffer.get_by_extid(
            transportation_offer_extid
        )
    else:
        # try to look up the transportation_offer, by payment intent
        transportation_offer = TransportationOffer.query.filter_by(
            stripe_payment_intent_id=intent.id
        ).one_or_none()
        if not transportation_offer:
            raise Exception(
                f"Failed to find {METADATA_TRANSPORTATION_OFFER_EXTID_KEY} in payment intent metadata"
            )
    if not transportation_offer:
        err = f"Stripe webhook received for unknown transportation_offer {transportation_offer_extid}"
        warnings.warn(err)
        if current_app.config.get("IGNORE_STRIPE_WEBHOOK_ERRORS"):
            return "ok"
        raise Exception(err)

    # check that correct amount was billed
    if transportation_offer.get_charge_amount_cents() != intent.amount:
        raise Exception("Transportation offer was charged different amount.")

    # Adjust payment status
    transportation_offer.payment_status = PaymentStatus.paid
    db.session.commit()

    log.info(f"Got payment of {intent.amount / 100}$ for {transportation_offer}!")
