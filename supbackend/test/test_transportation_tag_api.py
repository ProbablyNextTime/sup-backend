TOTAL = 100
PER_PAGE = 25


def test_listing_transportation_tags(client, session, transportation_tag_factory):
    session.add_all([transportation_tag_factory() for _ in range(TOTAL)])
    session.commit()

    for page in range(int(TOTAL / PER_PAGE)):
        page_response = client.get(
            f"/api/transportation_tag?page_size={PER_PAGE}&page={page + 1}"
        )
        assert page_response.status_code == 200
        assert len(page_response.json) == 25
        for transportation_tag in page_response.json:
            assert transportation_tag.get("id")
            assert transportation_tag.get("name")
