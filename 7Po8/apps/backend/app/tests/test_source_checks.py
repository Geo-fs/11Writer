from app.services import source_check_service


def _create_wave(client) -> int:
    response = client.post(
        "/api/waves",
        json={
            "name": "Source Check Wave",
            "description": "Track source reliability",
            "focus_type": "mixed",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_source_check_creation_and_metrics_update(client, monkeypatch) -> None:
    def fake_fetch(url: str) -> tuple[int, str | None, bytes]:
        assert url == "https://example.com/feed.xml"
        return 200, "application/rss+xml", b"<rss><channel></channel></rss>"

    monkeypatch.setattr(source_check_service, "_default_fetch", fake_fetch)
    wave_id = _create_wave(client)

    discovered = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://example.com/feed.xml"]},
    )
    assert discovered.status_code == 200
    source_id = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]["id"]

    check = client.post(f"/api/discovered-sources/{source_id}/check")
    assert check.status_code == 200
    payload = check.json()
    assert payload["status"] == "success"
    assert payload["reachable"] is True
    assert payload["parseable"] is True
    assert payload["http_status"] == 200
    assert payload["content_type"] == "application/rss+xml"

    source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert source["last_checked_at"] is not None
    assert source["last_success_at"] is not None
    assert source["failure_count"] == 0
    assert source["stability_score"] is not None


def test_stability_score_updates_after_failures_and_successes(client, monkeypatch) -> None:
    responses = [
        (503, "text/plain", b"down"),
        (503, "text/plain", b"down"),
        (200, "application/rss+xml", b"<rss><channel></channel></rss>"),
    ]

    def fake_fetch(_url: str) -> tuple[int, str | None, bytes]:
        return responses.pop(0)

    monkeypatch.setattr(source_check_service, "_default_fetch", fake_fetch)
    wave_id = _create_wave(client)
    client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://example.com/feed.xml"]},
    )
    source_id = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]["id"]

    client.post(f"/api/discovered-sources/{source_id}/check")
    first_source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    first_score = first_source["stability_score"]
    assert first_source["failure_count"] == 1

    client.post(f"/api/discovered-sources/{source_id}/check")
    second_source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    second_score = second_source["stability_score"]
    assert second_source["failure_count"] == 2
    assert second_score <= first_score

    client.post(f"/api/discovered-sources/{source_id}/check")
    third_source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    third_score = third_source["stability_score"]
    assert third_source["last_success_at"] is not None
    assert third_score >= second_score


def test_parseable_content_type_handling(client, monkeypatch) -> None:
    def fake_fetch(url: str) -> tuple[int, str | None, bytes]:
        assert url == "https://example.com/events.json"
        return 200, "text/plain", b"not valid json"

    monkeypatch.setattr(source_check_service, "_default_fetch", fake_fetch)
    wave_id = _create_wave(client)
    client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://example.com/events.json"]},
    )
    source_id = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]["id"]

    check = client.post(f"/api/discovered-sources/{source_id}/check")
    assert check.status_code == 200
    assert check.json()["status"] == "failed"
    assert check.json()["parseable"] is False
    checks = client.get(f"/api/discovered-sources/{source_id}/checks")
    assert checks.status_code == 200
    assert len(checks.json()) == 1


def test_batch_source_check_route_with_skipped_source(client, monkeypatch) -> None:
    def fake_fetch(url: str) -> tuple[int, str | None, bytes]:
        if url.endswith("feed.xml"):
            return 200, "application/rss+xml", b"<rss><channel></channel></rss>"
        return 404, "text/plain", b"missing"

    monkeypatch.setattr(source_check_service, "_default_fetch", fake_fetch)
    wave_id = _create_wave(client)
    client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={
            "seed_urls": [
                "https://example.com/feed.xml",
                "https://example.com/events.json",
            ]
        },
    )
    sources = client.get(f"/api/waves/{wave_id}/discovered-sources").json()
    json_source = next(source for source in sources if source["source_type"] == "api_json")
    client.patch(
        f"/api/discovered-sources/{json_source['id']}",
        json={"status": "ignored"},
    )

    batch = client.post(f"/api/waves/{wave_id}/check-discovered-sources")
    assert batch.status_code == 200
    payload = batch.json()
    assert payload["checked_count"] == 2
    assert payload["success_count"] == 1
    assert payload["failed_count"] == 0
    assert payload["skipped_count"] == 1
