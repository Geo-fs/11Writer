def test_create_and_list_waves(client) -> None:
    create_response = client.post(
        "/api/waves",
        json={
            "name": "Austin Development Watch",
            "description": "Track permit and zoning updates",
            "focus_type": "location",
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/api/waves")
    assert list_response.status_code == 200
    payload = list_response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Austin Development Watch"
