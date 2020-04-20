from unittest.mock import patch, Mock, ANY

import stripe

from supbackend.api.billing import (
    METADATA_TRANSPORTATION_OFFER_EXTID_KEY,
    handle_stripe_event,
)
from supbackend.model import TransportationOffer
from supbackend.model.constant import PaymentStatus


def test_initiate_checkout(client, session, transportation_offer_factory, mock_stripe):
    transportation_offer = transportation_offer_factory()
    transportation_offer.payment_status = PaymentStatus.not_paid
    session.add(transportation_offer)
    session.commit()

    SESSION_ID = "ss_1234"  # checkout session ID

    with patch("stripe.checkout.Session.create") as session_create_patch:
        session_create_patch.return_value = Mock(
            id=SESSION_ID, payment_intent="pi_1234"
        )
        res = client.post(
            f"/api/billing/checkout/transportation_offer/{transportation_offer.extid}"
        )
        assert res.status_code == 200
        res = res.json
        session_create_patch.assert_called_once_with(
            line_items=[
                {
                    "name": ANY,
                    "amount": transportation_offer.get_charge_amount_cents(),
                    "currency": "usd",
                    "description": ANY,
                    "quantity": 1,
                }
            ],
            customer=ANY,
            cancel_url=ANY,
            # customer_email=ANY,
            billing_address_collection=ANY,
            payment_method_types=ANY,
            success_url=ANY,
            payment_intent_data={
                "metadata": {"transportation_offer_extid": transportation_offer.extid}
            },
        )
        assert res["session_id"] == SESSION_ID
        assert transportation_offer.stripe_checkout_session_id == SESSION_ID


def test_transportation_offer_checkout_session_webhook(
    transportation_offer_factory, session
):
    transportation_offer = transportation_offer_factory()
    transportation_offer.payment_status = PaymentStatus.not_paid
    session.add(transportation_offer)
    session.commit()

    handle_stripe_event(
        stripe_checkout_success_event(transportation_offer=transportation_offer)
    )
    session.expire(transportation_offer)

    assert transportation_offer.payment_status == PaymentStatus.paid


def stripe_checkout_success_event(
    transportation_offer: TransportationOffer, amount: int = None
):
    if amount is None:
        amount = transportation_offer.get_charge_amount_cents()
    return stripe.Event.construct_from(
        key=None,
        values={
            "api_version": "2019-12-03",
            "created": 1577721584,
            "data": {
                "object": {
                    "amount": amount,
                    "amount_capturable": 0,
                    "amount_received": amount,
                    "application": None,
                    "application_fee_amount": None,
                    "canceled_at": None,
                    "cancellation_reason": None,
                    "capture_method": "automatic",
                    "charges": {
                        "data": [
                            {
                                "amount": amount,
                                "amount_refunded": 0,
                                "application": None,
                                "application_fee": None,
                                "application_fee_amount": None,
                                "balance_transaction": "txn_1FvQeiFPl7dG66Mw9AmN81tC",
                                "billing_details": {
                                    "address": {
                                        "city": None,
                                        "country": None,
                                        "line1": None,
                                        "line2": None,
                                        "postal_code": None,
                                        "state": None,
                                    },
                                    "email": "stripe@example.com",
                                    "name": None,
                                    "phone": None,
                                },
                                "captured": True,
                                "created": 1577721583,
                                "currency": "usd",
                                "customer": "cus_GSLLvBgGT5Vtv1",
                                "description": None,
                                "destination": None,
                                "dispute": None,
                                "disputed": False,
                                "failure_code": None,
                                "failure_message": None,
                                "fraud_details": {},
                                "id": "ch_1FvQehFPl7dG66MwvPpWhe5e",
                                "invoice": None,
                                "livemode": False,
                                "metadata": {},
                                "object": "charge",
                                "on_behalf_of": None,
                                "order": None,
                                "outcome": {
                                    "network_status": "approved_by_network",
                                    "reason": None,
                                    "risk_level": "normal",
                                    "risk_score": 22,
                                    "seller_message": "Payment " "complete.",
                                    "type": "authorized",
                                },
                                "paid": True,
                                "payment_intent": "pi_1FvQefFPl7dG66MwjxeHxgQp",
                                "payment_method": "pm_1FvQegFPl7dG66Mwj44ItnxI",
                                "payment_method_details": {
                                    "card": {
                                        "brand": "visa",
                                        "checks": {
                                            "address_line1_check": None,
                                            "address_postal_code_check": None,
                                            "cvc_check": None,
                                        },
                                        "country": "US",
                                        "exp_month": 12,
                                        "exp_year": 2020,
                                        "fingerprint": "g5Q1YaVr8AcwaeQ8",
                                        "funding": "credit",
                                        "installments": None,
                                        "last4": "4242",
                                        "network": "visa",
                                        "three_d_secure": None,
                                        "wallet": None,
                                    },
                                    "type": "card",
                                },
                                "receipt_email": None,
                                "receipt_number": None,
                                "receipt_url": "https://pay.stripe.com/receipts/acct_1Dy4oUFPl7dG66Mw/ch_1FvQehFPl7dG66MwvPpWhe5e/rcpt_GSLLCdIbCqWQ7Z0mUravEgDNsf0kq46",
                                "refunded": False,
                                "refunds": {},
                                "review": None,
                                "shipping": None,
                                "source": None,
                                "source_transfer": None,
                                "statement_descriptor": None,
                                "statement_descriptor_suffix": None,
                                "status": "succeeded",
                                "transfer_data": None,
                                "transfer_group": None,
                            }
                        ],
                        "has_more": False,
                        "object": "list",
                        "total_count": 1,
                        "url": "/v1/charges?payment_intent=pi_1FvQefFPl7dG66MwjxeHxgQp",
                    },
                    "client_secret": "pi_1FvQefFPl7dG66MwjxeHxgQp_secret_klKRoeXYj29HM20nN5Sao2ke7",
                    "confirmation_method": "automatic",
                    "created": 1577721581,
                    "currency": "usd",
                    "customer": "cus_GSLLvBgGT5Vtv1",
                    "description": None,
                    "id": "pi_1FvQefFPl7dG66MwjxeHxgQp",
                    "invoice": None,
                    "last_payment_error": None,
                    "livemode": False,
                    "metadata": {
                        METADATA_TRANSPORTATION_OFFER_EXTID_KEY: str(
                            transportation_offer.extid
                        )
                    },
                    "next_action": None,
                    "object": "payment_intent",
                    "on_behalf_of": None,
                    "payment_method": "pm_1FvQegFPl7dG66Mwj44ItnxI",
                    "payment_method_options": {
                        "card": {
                            "installments": None,
                            "request_three_d_secure": "automatic",
                        }
                    },
                    "payment_method_types": ["card"],
                    "receipt_email": None,
                    "review": None,
                    "setup_future_usage": None,
                    "shipping": None,
                    "source": None,
                    "statement_descriptor": None,
                    "statement_descriptor_suffix": None,
                    "status": "succeeded",
                    "transfer_data": None,
                    "transfer_group": None,
                }
            },
            "id": "evt_1FvQeiFPl7dG66MwqLqBuxAr",
            "livemode": False,
            "object": "event",
            "pending_webhooks": 1,
            "request": {"id": "req_yJT89XdUsjIBDy", "idempotency_key": None},
            "type": "payment_intent.succeeded",
        },
    )
