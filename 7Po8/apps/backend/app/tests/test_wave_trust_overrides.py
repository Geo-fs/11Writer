def _create_wave(client) -> int:
    response = client.post(
        "/api/waves",
        json={
            "name": "Override Wave",
            "description": "wave override testing",
            "focus_type": "mixed",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_wave_trust_override_crud_and_precedence(client) -> None:
    wave_id = _create_wave(client)
    client.post(
        "/api/domain-trust",
        json={
            "domain": "policy.example.gov",
            "trust_level": "trusted",
            "approval_policy": "auto_approve_stable",
        },
    )

    created = client.post(
        f"/api/waves/{wave_id}/trust-overrides",
        json={
            "domain": "policy.example.gov",
            "trust_level": "trusted",
            "approval_policy": "always_review",
            "notes": "manual only for this wave",
        },
    )
    assert created.status_code == 201
    payload = created.json()
    assert payload["domain"] == "policy.example.gov"
    assert payload["approval_policy"] == "always_review"

    listed = client.get(f"/api/waves/{wave_id}/trust-overrides")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    discover = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://policy.example.gov/feed.xml"]},
    )
    assert discover.status_code == 200
    source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert source["status"] == "candidate"
    assert source["policy_source"] == "wave_override"
    assert source["domain_approval_policy"] == "always_review"
    assert source["policy_state"] == "manual_review"

    patched = client.patch(
        f"/api/wave-trust-overrides/{payload['id']}",
        json={"approval_policy": "auto_approve_stable"},
    )
    assert patched.status_code == 200
    assert patched.json()["approval_policy"] == "auto_approve_stable"

    deleted = client.delete(f"/api/wave-trust-overrides/{payload['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/api/waves/{wave_id}/trust-overrides").json() == []


def test_wave_override_can_relax_global_block_for_wave(client) -> None:
    wave_id = _create_wave(client)
    profile = client.post(
        "/api/domain-trust",
        json={
            "domain": "blocked.example.com",
            "trust_level": "blocked",
            "approval_policy": "auto_reject",
        },
    )
    assert profile.status_code == 201

    override = client.post(
        f"/api/waves/{wave_id}/trust-overrides",
        json={
            "domain": "blocked.example.com",
            "trust_level": "neutral",
            "approval_policy": "manual_review",
        },
    )
    assert override.status_code == 201

    discover = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://blocked.example.com/feed.xml"]},
    )
    assert discover.status_code == 200
    source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert source["status"] == "candidate"
    assert source["policy_source"] == "wave_override"
    assert source["policy_state"] == "manual_review"


def test_wave_override_reevaluation_writes_policy_action_log(client) -> None:
    wave_id = _create_wave(client)
    discover = client.post(
        f"/api/waves/{wave_id}/discover-sources",
        json={"seed_urls": ["https://logs.example.gov/feed.xml"]},
    )
    assert discover.status_code == 200

    override = client.post(
        f"/api/waves/{wave_id}/trust-overrides",
        json={
            "domain": "logs.example.gov",
            "trust_level": "blocked",
            "approval_policy": "auto_reject",
        },
    )
    assert override.status_code == 201
    source = client.get(f"/api/waves/{wave_id}/discovered-sources").json()[0]
    assert source["status"] == "rejected"

    actions = client.get(f"/api/waves/{wave_id}/policy-actions")
    assert actions.status_code == 200
    rows = actions.json()
    assert rows
    assert rows[0]["action_type"] == "blocked_by_policy"
    assert rows[0]["triggered_by"] == "wave_override_change"
    assert rows[0]["new_status"] == "rejected"

    source_actions = client.get(f"/api/discovered-sources/{source['id']}/policy-actions")
    assert source_actions.status_code == 200
    assert source_actions.json()[0]["discovered_source_id"] == source["id"]
