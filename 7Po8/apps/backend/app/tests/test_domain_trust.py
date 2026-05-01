from app.services import source_check_service


def _create_wave(client) -> int:
    response = client.post(
        "/api/waves",
        json={
            "name": "Trust Wave",
            "description": "policy testing",
            "focus_type": "mixed",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_domain_profile(
    client,
    *,
    domain: str,
    trust_level: str,
    approval_policy: str,
    notes: str | None = None,
):
    response = client.post(
        "/api/domain-trust",
        json={
            "domain": domain,
            "trust_level": trust_level,
            "approval_policy": approval_policy,
            "notes": notes,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_domain_trust_profile_crud(client) -> None:
    created = _create_domain_profile(
        client,
        domain="city.example.gov",
        trust_level="trusted",
        approval_policy="auto_approve_stable",
        notes="city open-data feeds",
    )
    assert created["domain"] == "city.example.gov"
    assert created["source_count"] == 0

    listed = client.get("/api/domain-trust")
    assert listed.status_code == 200
    assert listed.json()[0]["domain"] == "city.example.gov"

    patched = client.patch(
        f"/api/domain-trust/{created['id']}",
        json={"trust_level": "blocked", "approval_policy": "auto_reject"},
    )
    assert patched.status_code == 200
    assert patched.json()["trust_level"] == "blocked"
    assert patched.json()["approval_policy"] == "auto_reject"

    deleted = client.delete(f"/api/domain-trust/{created['id']}")
    assert deleted.status_code == 204
    assert client.get("/api/domain-trust").json() == []


def test_blocked_domain_sources_are_rejected_and_signaled(client) -> None:
    wave_id = _create_wave(client)
    _create_domain_profile(
        client,
        domain="blocked.example.com",
        trust_level="blocked",
        approval_policy="auto_reject",
    )

    discover = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://blocked.example.com/feed.xml"]},
    )
    assert discover.status_code == 200

    source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert source["status"] == "rejected"
    assert source["domain_trust_level"] == "blocked"
    assert source["domain_approval_policy"] == "auto_reject"
    assert source["policy_state"] == "blocked"
    assert source["approval_origin"] == "policy_blocked"

    approve = client.post(f"/api/discovered-sources/{source['id']}/approve")
    assert approve.status_code == 409

    signals = client.get(f"/api/waves/{wave_id}/signals").json()
    signal_types = {signal["type"] for signal in signals}
    assert "discovered_source_blocked_by_policy" in signal_types


def test_existing_stable_source_auto_approves_after_policy_change(client, monkeypatch) -> None:
    def success_fetch(_url: str) -> tuple[int, str | None, bytes]:
        return 200, "application/rss+xml", b"<rss><channel></channel></rss>"

    monkeypatch.setattr(source_check_service, "_default_fetch", success_fetch)
    wave_id = _create_wave(client)

    discover = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://policy.example.gov/feed.xml"]},
    )
    assert discover.status_code == 200
    source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]

    client.post(f"/api/discovered-sources/{source['id']}/check")
    client.post(f"/api/discovered-sources/{source['id']}/check")

    created = _create_domain_profile(
        client,
        domain="policy.example.gov",
        trust_level="trusted",
        approval_policy="auto_approve_stable",
    )
    assert created["approved_source_count"] == 1

    refreshed = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert refreshed["status"] == "approved"
    assert refreshed["approval_origin"] == "policy_auto"

    signals = client.get(f"/api/waves/{wave_id}/signals").json()
    signal_types = {signal["type"] for signal in signals}
    assert "source_graduated_from_sandbox" in signal_types


def test_existing_source_becomes_blocked_after_profile_update(client) -> None:
    wave_id = _create_wave(client)
    _create_domain_profile(
        client,
        domain="city.example.gov",
        trust_level="neutral",
        approval_policy="manual_review",
    )

    discover = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://city.example.gov/feed.xml"]},
    )
    assert discover.status_code == 200

    profiles = client.get("/api/domain-trust").json()
    profile = next(item for item in profiles if item["domain"] == "city.example.gov")

    patched = client.patch(
        f"/api/domain-trust/{profile['id']}",
        json={"trust_level": "blocked", "approval_policy": "auto_reject"},
    )
    assert patched.status_code == 200

    refreshed = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert refreshed["status"] == "rejected"
    assert refreshed["approval_origin"] == "policy_blocked"
    assert refreshed["policy_state"] == "blocked"

    signals = client.get(f"/api/waves/{wave_id}/signals").json()
    signal_types = {signal["type"] for signal in signals}
    assert "discovered_source_blocked_by_policy" in signal_types


def test_trusted_domain_stable_rss_source_auto_approves(client, monkeypatch) -> None:
    def success_fetch(_url: str) -> tuple[int, str | None, bytes]:
        return 200, "application/rss+xml", b"<rss><channel></channel></rss>"

    monkeypatch.setattr(source_check_service, "_default_fetch", success_fetch)
    wave_id = _create_wave(client)
    _create_domain_profile(
        client,
        domain="trusted.example.com",
        trust_level="trusted",
        approval_policy="auto_approve_stable",
    )

    discover = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://trusted.example.com/feed.xml"]},
    )
    assert discover.status_code == 200

    source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert source["status"] == "candidate"
    assert source["policy_state"] in {"manual_review", "ineligible"}

    first_check = client.post(f"/api/discovered-sources/{source['id']}/check")
    assert first_check.status_code == 200
    second_check = client.post(f"/api/discovered-sources/{source['id']}/check")
    assert second_check.status_code == 200

    refreshed = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert refreshed["status"] == "approved"
    assert refreshed["approval_origin"] == "policy_auto"
    assert refreshed["policy_state"] == "auto_approved"

    connectors = client.get(f"/api/waves/{wave_id}/connectors")
    assert connectors.status_code == 200
    assert len(connectors.json()) == 1
    assert connectors.json()[0]["config_json"]["feed_url"] == refreshed["url"]

    signals = client.get(f"/api/waves/{wave_id}/signals").json()
    signal_types = {signal["type"] for signal in signals}
    assert "source_graduated_from_sandbox" in signal_types


def test_policy_blocked_source_becomes_reviewable_after_relaxation(client, monkeypatch) -> None:
    def success_fetch(_url: str) -> tuple[int, str | None, bytes]:
        return 200, "application/rss+xml", b"<rss><channel></channel></rss>"

    monkeypatch.setattr(source_check_service, "_default_fetch", success_fetch)
    wave_id = _create_wave(client)
    created = _create_domain_profile(
        client,
        domain="relax.example.com",
        trust_level="blocked",
        approval_policy="auto_reject",
    )

    discover = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://relax.example.com/feed.xml"]},
    )
    assert discover.status_code == 200
    source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert source["status"] == "rejected"
    assert source["approval_origin"] == "policy_blocked"

    client.post(f"/api/discovered-sources/{source['id']}/check")
    relaxed = client.patch(
        f"/api/domain-trust/{created['id']}",
        json={"trust_level": "trusted", "approval_policy": "always_review"},
    )
    assert relaxed.status_code == 200

    refreshed = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert refreshed["status"] == "candidate"
    assert refreshed["approval_origin"] is None
    assert refreshed["policy_state"] == "manual_review"

    signals = client.get(f"/api/waves/{wave_id}/signals").json()
    signal_types = {signal["type"] for signal in signals}
    assert "discovered_source_became_reviewable_after_policy_change" in signal_types


def test_trusted_domain_always_review_source_emits_review_signal(client, monkeypatch) -> None:
    def success_fetch(_url: str) -> tuple[int, str | None, bytes]:
        return 200, "application/rss+xml", b"<rss><channel></channel></rss>"

    monkeypatch.setattr(source_check_service, "_default_fetch", success_fetch)
    wave_id = _create_wave(client)
    _create_domain_profile(
        client,
        domain="review.example.com",
        trust_level="trusted",
        approval_policy="always_review",
    )

    discover = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://review.example.com/feed.xml"]},
    )
    assert discover.status_code == 200
    source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]

    check = client.post(f"/api/discovered-sources/{source['id']}/check")
    assert check.status_code == 200

    refreshed = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert refreshed["status"] == "sandboxed"
    assert refreshed["domain_trust_level"] == "trusted"
    assert refreshed["domain_approval_policy"] == "always_review"
    assert refreshed["policy_state"] == "manual_review"

    signals = client.get(f"/api/waves/{wave_id}/signals").json()
    signal_types = {signal["type"] for signal in signals}
    assert "source_entered_sandbox" in signal_types


def test_ignored_source_is_preserved_during_policy_reevaluation(client) -> None:
    wave_id = _create_wave(client)
    discover = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://ignored.example.com/feed.xml"]},
    )
    assert discover.status_code == 200
    source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    ignored = client.patch(
        f"/api/discovered-sources/{source['id']}",
        json={"status": "ignored"},
    )
    assert ignored.status_code == 200

    created = _create_domain_profile(
        client,
        domain="ignored.example.com",
        trust_level="blocked",
        approval_policy="auto_reject",
    )
    result = client.post(f"/api/domain-trust/{created['id']}/reevaluate")
    assert result.status_code == 200
    assert result.json()["changed_count"] == 0

    refreshed = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert refreshed["status"] == "ignored"
    assert refreshed["policy_state"] == "blocked"


def test_unstable_source_cannot_be_manually_approved(client, monkeypatch) -> None:
    responses = [
        (503, "text/plain", b"down"),
        (503, "text/plain", b"down"),
        (503, "text/plain", b"down"),
    ]

    def failing_fetch(_url: str) -> tuple[int, str | None, bytes]:
        return responses.pop(0)

    monkeypatch.setattr(source_check_service, "_default_fetch", failing_fetch)
    wave_id = _create_wave(client)
    _create_domain_profile(
        client,
        domain="unstable.example.com",
        trust_level="trusted",
        approval_policy="auto_approve_stable",
    )

    discover = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://unstable.example.com/feed.xml"]},
    )
    assert discover.status_code == 200
    source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]

    client.post(f"/api/discovered-sources/{source['id']}/check")
    client.post(f"/api/discovered-sources/{source['id']}/check")
    client.post(f"/api/discovered-sources/{source['id']}/check")

    approve = client.post(f"/api/discovered-sources/{source['id']}/approve")
    assert approve.status_code == 409
    assert "unstable" in approve.json()["detail"].casefold()


def test_policy_reevaluation_is_idempotent(client, monkeypatch) -> None:
    def success_fetch(_url: str) -> tuple[int, str | None, bytes]:
        return 200, "application/rss+xml", b"<rss><channel></channel></rss>"

    monkeypatch.setattr(source_check_service, "_default_fetch", success_fetch)
    wave_id = _create_wave(client)

    discover = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://repeat.example.com/feed.xml"]},
    )
    assert discover.status_code == 200
    source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    client.post(f"/api/discovered-sources/{source['id']}/check")
    client.post(f"/api/discovered-sources/{source['id']}/check")

    profile = _create_domain_profile(
        client,
        domain="repeat.example.com",
        trust_level="trusted",
        approval_policy="auto_approve_stable",
    )

    first = client.post(f"/api/domain-trust/{profile['id']}/reevaluate")
    second = client.post(f"/api/domain-trust/{profile['id']}/reevaluate")
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["changed_count"] == 0

    signals = client.get(f"/api/waves/{wave_id}/signals").json()
    auto_approved_signals = [
        signal
        for signal in signals
        if signal["type"] == "source_graduated_from_sandbox"
    ]
    assert len(auto_approved_signals) == 1
