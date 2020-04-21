from supbackend.db.fixtures import DEFAULT_PASSWORD


def test_login(client_unauthenticated, user):
    response = client_unauthenticated.post(
        "/api/auth/login", json=dict(email=user.email, password=DEFAULT_PASSWORD)
    )
    assert response.status_code == 200
    assert response.json.get("access_token")
    assert response.json.get("refresh_token")

    # attempt refresh
    refresh_token = response.json.get("refresh_token")
    response = client_unauthenticated.post(
        "/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
    ).json
    access_token = response.get("access_token")

    # test new token
    response = client_unauthenticated.get(
        "/api/auth/check", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200


def test_sign_up(session, client_unauthenticated):
    test_email = "testsignup@gmail.com"
    sign_up_response = client_unauthenticated.post(
        "/api/auth/sign-up", json=dict(email=test_email, password=DEFAULT_PASSWORD)
    )
    assert sign_up_response.status_code == 200
    assert sign_up_response.json["email"] == test_email

    log_in_response = client_unauthenticated.post(
        "/api/auth/login", json=dict(email=test_email, password=DEFAULT_PASSWORD)
    )

    assert log_in_response.status_code == 200
    assert log_in_response.json["access_token"] is not None
    assert log_in_response.json["refresh_token"] is not None
    assert log_in_response.json["user"].get("id") is not None

    sign_up_response = client_unauthenticated.post(
        "/api/auth/sign-up", json=dict(email=test_email, password=DEFAULT_PASSWORD)
    )

    assert not sign_up_response == 200
