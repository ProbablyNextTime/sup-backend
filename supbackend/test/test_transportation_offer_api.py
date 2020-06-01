from datetime import datetime, timezone
from supbackend.model import TransportationOffer
from supbackend.model.constant import PaymentStatus

TOTAL = 100
PER_PAGE = 25


def test_getting_transportation_offer(client, session, transportation_offer_factory):
    toffer1 = transportation_offer_factory(payment_status=PaymentStatus.not_paid)
    session.add(toffer1)
    session.commit()

    assert toffer1.extid

    response = client.get(f"/api/transportation_offer/{toffer1.extid}")

    assert response.status_code == 200


def test_listing_transportation_offers(
    client, session, offer_tag_factory, transportation_offer_factory
):
    session.add_all(
        [
            offer_tag_factory(
                transportation_offer=transportation_offer_factory(
                    payment_status=PaymentStatus.not_paid
                )
            )
            for _ in range(TOTAL)
        ]
    )
    session.commit()

    for page in range(int(TOTAL / PER_PAGE)):
        page_response = client.get(
            f"/api/transportation_offer?page_size={PER_PAGE}&page={page + 1}"
        )
        assert page_response.status_code == 200
        assert len(page_response.json) == 25
        for transportation_offer in page_response.json:
            assert transportation_offer.get("id")
            assert transportation_offer.get("transportationProvider")
            assert transportation_offer.get("cargo")
            assert transportation_offer.get("transportationTags")


def test_search_for_transportation_offer(client, session, offer_tag_factory):
    session.add_all([offer_tag_factory() for _ in range(TOTAL)])
    session.commit()

    sample_data = client.get("/api/transportation_offer")

    # Search by transportation offer title
    title = sample_data.json[0]["title"]
    response = client.get(f"/api/transportation_offer?query={title}")
    for transportation_offer in response.json:
        assert title in transportation_offer["title"]

    # Search by departure point
    departure_point = sample_data.json[0]["departurePoint"]
    response = client.get(f"/api/transportation_offer?query={departure_point}")
    for transportation_offer in response.json:
        assert departure_point in transportation_offer["departurePoint"]

    # Search by destination point
    destination_point = sample_data.json[0]["destinationPoint"]
    response = client.get(f"/api/transportation_offer?query={destination_point}")
    for transportation_offer in response.json:
        assert destination_point in transportation_offer["destinationPoint"]

    # Search by transportation tag
    tags = sample_data.json[0]["transportationTags"]
    tag = tags[0]["name"]
    response = client.get(f"/api/transportation_offer?query={tag}")
    for transportation_offer in response.json:
        found_tags = [tag["name"] for tag in transportation_offer["transportationTags"]]
        assert tag in found_tags

    # Search by cargo name
    cargo = sample_data.json[0]["cargo"]
    cargo_name = cargo["name"]
    response = client.get(f"/api/transportation_offer?query={cargo_name}")
    for transportation_offer in response.json:
        assert cargo_name in transportation_offer["cargo"]["name"]

    # Search by transportation provider name
    transportation_provider = sample_data.json[0]["transportationProvider"]
    transportation_provider_name = transportation_provider["name"]
    response = client.get(
        f"/api/transportation_offer?query={transportation_provider_name}"
    )
    for transportation_offer in response.json:
        assert (
            transportation_provider_name
            in transportation_offer["transportationProvider"]["name"]
        )


def test_adding_transportation_offer(client, session):
    departure_date = datetime.now(timezone.utc)
    arrival_date = datetime.now(timezone.utc)
    new_transportation_tag_json = {
        "departure_date": str(departure_date),
        "arrival_date": str(arrival_date),
        "pickup_place": "somewhere",
        "delivery_place": "test",
        "price_per_unit_in_usd": 10,
        "cargo": "test",
        "tags": [{"name": "tag1"}, {"name": "tag2"}, {"name": "tag3"}],
        "transportation_target": "cargo",
    }

    print(f"ATTENTION: {new_transportation_tag_json}")

    response = client.post(
        "/api/transportation_offer", json=new_transportation_tag_json
    )

    assert response.status_code == 200

    offer = TransportationOffer.query.first()

    assert offer.cargo.name == new_transportation_tag_json.get("cargo")
    assert offer.departure_date == departure_date
    assert offer.arrival_date == arrival_date
    assert len(offer.transportation_tags) == 3
