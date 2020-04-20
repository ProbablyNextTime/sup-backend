TOTAL = 100
PER_PAGE = 25


def test_getting_transportation_offer(client, session, transportation_offer_factory):
    toffer1 = transportation_offer_factory()
    session.add(toffer1)
    session.commit()

    assert toffer1.extid

    response = client.get(f"/api/transportation_offer/{toffer1.extid}")

    assert response.status_code == 200


def test_listing_transportation_offers(client, session, offer_tag_factory):
    session.add_all([offer_tag_factory() for _ in range(TOTAL)])
    session.commit()

    for page in range(int(TOTAL / PER_PAGE)):
        page_response = client.get(
            f"/api/transportation_offer?page_size={PER_PAGE}&page={page + 1}"
        )
        assert page_response.status_code == 200
        assert len(page_response.json) == 25
        for transportation_offer in page_response.json:
            assert transportation_offer.get("id")


def test_search_for_transportation_offer(client, session, offer_tag_factory):
    session.add_all([offer_tag_factory() for _ in range(TOTAL)])
    session.commit()

    sample_data = client.get(f"/api/transportation_offer")

    # Search by transportation offer title
    title = sample_data.json[0]["title"]
    response = client.get(f"/api/transportation_offer?query={title}")
    for transportation_offer in response.json:
        assert title in transportation_offer["title"]

    # Search by departure point
    departure_point = sample_data.json[0]["departure_point"]
    response = client.get(f"/api/transportation_offer?query={departure_point}")
    for transportation_offer in response.json:
        assert departure_point in transportation_offer["departure_point"]

    # Search by destination point
    destination_point = sample_data.json[0]["destination_point"]
    response = client.get(f"/api/transportation_offer?query={destination_point}")
    for transportation_offer in response.json:
        assert destination_point in transportation_offer["destination_point"]

    # Search by transportation tag
    tags = sample_data.json[0]["transportation_tags"]
    tag = tags[0]["name"]
    response = client.get(f"/api/transportation_offer?query={tag}")
    for transportation_offer in response.json:
        found_tags = [
            tag["name"] for tag in transportation_offer["transportation_tags"]
        ]
        assert tag in found_tags

    # Search by cargo name
    cargo = sample_data.json[0]["cargo"]
    cargo_name = cargo["name"]
    response = client.get(f"/api/transportation_offer?query={cargo_name}")
    for transportation_offer in response.json:
        assert cargo_name in transportation_offer["cargo"]["name"]
