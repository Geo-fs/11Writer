import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { vi } from "vitest";

import { WaveDetailPage } from "../pages/WaveDetailPage";

function jsonResponse(payload: unknown, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function wavePayload() {
  return {
    id: 1,
    name: "Discovery Wave",
    description: "desc",
    status: "active",
    focus_type: "mixed",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    last_run_at: null,
    last_success_at: null,
    last_error_at: null,
    last_error_message: null,
    connector_count: 0,
    record_count: 0,
  };
}

function domainTrustPayload() {
  return [
    {
      id: 1,
      domain: "city.example.gov",
      trust_level: "trusted",
      approval_policy: "auto_approve_stable",
      notes: null,
      created_at: "2026-03-14T09:00:00Z",
      updated_at: "2026-03-14T09:00:00Z",
      source_count: 1,
      approved_source_count: 0,
      blocked_source_count: 0,
      average_stability_score: 0.82,
      last_seen_at: "2026-03-14T10:00:00Z",
    },
  ];
}

describe("Source Discovery", () => {
  it("renders discovered sources and updates status", async () => {
    const fetchMock = vi.spyOn(global, "fetch");
    fetchMock.mockImplementation(async () => jsonResponse([]));

    fetchMock
      .mockResolvedValueOnce(jsonResponse(wavePayload()))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(
        jsonResponse([
          {
            id: 10,
            wave_id: 1,
            url: "https://city.example.gov/feed.xml",
            title: "feed.xml",
            source_type: "rss",
            parent_domain: "city.example.gov",
            status: "new",
            discovery_method: "seed+page-inspection",
            relevance_score: 0.9,
            stability_score: null,
            free_access: true,
            suggested_connector_type: "rss_news",
            description_summary: null,
            metadata_json: {},
            discovered_at: "2026-03-14T10:00:00Z",
            auto_check_enabled: true,
            check_interval_minutes: 60,
            next_check_at: "2026-03-14T11:00:00Z",
            consecutive_failures: 0,
            last_checked_at: "2026-03-14T10:00:00Z",
            last_success_at: null,
            failure_count: 0,
            last_http_status: null,
            last_content_type: null,
            domain_trust_level: "neutral",
            domain_approval_policy: "manual_review",
            policy_state: "manual_review",
            policy_reason: "Domain is not trusted for auto-approval.",
            approval_origin: null,
            policy_source: "default",
            wave_trust_override_id: null,
            global_domain_trust_profile_id: null,
          },
        ])
      )
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(
        jsonResponse({
          id: 10,
          status: "rejected",
          wave_id: 1,
          url: "https://city.example.gov/feed.xml",
        })
      )
      .mockResolvedValueOnce(jsonResponse(wavePayload()))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(
        jsonResponse([
          {
            id: 10,
            wave_id: 1,
            url: "https://city.example.gov/feed.xml",
            title: "feed.xml",
            source_type: "rss",
            parent_domain: "city.example.gov",
            status: "rejected",
            discovery_method: "seed+page-inspection",
            relevance_score: 0.9,
            stability_score: null,
            free_access: true,
            suggested_connector_type: "rss_news",
            description_summary: null,
            metadata_json: {},
            discovered_at: "2026-03-14T10:00:00Z",
            auto_check_enabled: true,
            check_interval_minutes: 60,
            next_check_at: "2026-03-14T11:30:00Z",
            consecutive_failures: 0,
            last_checked_at: "2026-03-14T10:05:00Z",
            last_success_at: null,
            failure_count: 0,
            last_http_status: null,
            last_content_type: null,
            domain_trust_level: "neutral",
            domain_approval_policy: "manual_review",
            policy_state: "manual_review",
            policy_reason: "Domain is not trusted for auto-approval.",
            approval_origin: null,
            policy_source: "default",
            wave_trust_override_id: null,
            global_domain_trust_profile_id: null,
          },
        ])
      )
      .mockResolvedValueOnce(jsonResponse([]));

    render(
      <MemoryRouter initialEntries={["/waves/1"]}>
        <Routes>
          <Route element={<WaveDetailPage />} path="/waves/:waveId" />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText("feed.xml")).toBeInTheDocument());
    expect(screen.getByText(/Policy Source: Default Policy/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Reject" }));

    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some(
          (call) =>
            typeof call[0] === "string" &&
            call[0].includes("/api/discovered-sources/10") &&
            typeof call[1] === "object" &&
            call[1] !== null &&
            "method" in call[1] &&
            (call[1] as RequestInit).method === "PATCH"
        )
      ).toBe(true);
    });
    vi.restoreAllMocks();
  });

  it("shows trust and stability details and triggers source check", async () => {
    const fetchMock = vi.spyOn(global, "fetch");
    fetchMock.mockImplementation(async () => jsonResponse([]));

    const discovered = [
      {
        id: 10,
        wave_id: 1,
        url: "https://city.example.gov/feed.xml",
        title: "feed.xml",
        source_type: "rss",
        parent_domain: "city.example.gov",
        status: "new",
        discovery_method: "seed+page-inspection",
        relevance_score: 0.9,
        stability_score: 0.82,
        free_access: true,
        suggested_connector_type: "rss_news",
        description_summary: null,
        metadata_json: {},
        discovered_at: "2026-03-14T10:00:00Z",
        auto_check_enabled: true,
        check_interval_minutes: 30,
        next_check_at: "2026-03-14T10:35:00Z",
        consecutive_failures: 1,
        last_checked_at: "2026-03-14T10:01:00Z",
        last_success_at: "2026-03-14T10:01:00Z",
        failure_count: 1,
        last_http_status: 200,
        last_content_type: "application/rss+xml",
        domain_trust_level: "trusted",
        domain_approval_policy: "auto_approve_stable",
        policy_state: "auto_approvable",
        policy_reason: "Source meets trusted-domain auto-approval requirements.",
        approval_origin: null,
        policy_source: "global_domain_trust",
        wave_trust_override_id: null,
        global_domain_trust_profile_id: 1,
      },
    ];

    fetchMock
      .mockResolvedValueOnce(jsonResponse(wavePayload()))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse(discovered))
      .mockResolvedValueOnce(jsonResponse(domainTrustPayload()))
      .mockResolvedValueOnce(
        jsonResponse({
          id: 99,
          discovered_source_id: 10,
          checked_at: "2026-03-14T10:05:00Z",
          status: "success",
          http_status: 200,
          content_type: "application/rss+xml",
          latency_ms: 120,
          reachable: true,
          parseable: true,
          metadata_json: null,
        })
      )
      .mockResolvedValueOnce(jsonResponse(wavePayload()))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse(discovered))
      .mockResolvedValueOnce(jsonResponse(domainTrustPayload()));

    render(
      <MemoryRouter initialEntries={["/waves/1"]}>
        <Routes>
          <Route element={<WaveDetailPage />} path="/waves/:waveId" />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText("feed.xml")).toBeInTheDocument());
    expect(screen.getByText(/Stability:/)).toBeInTheDocument();
    expect(screen.getByText(/Auto Check: active/)).toBeInTheDocument();
    expect(screen.getByText(/Interval: 30 min/)).toBeInTheDocument();
    expect(screen.getByText(/Consecutive Failures: 1/)).toBeInTheDocument();
    expect(screen.getByText(/Policy: auto_approve_stable/)).toBeInTheDocument();
    expect(screen.getByText(/auto_approvable/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Check Source" }));
    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some(
          (call) =>
            typeof call[0] === "string" &&
            call[0].includes("/api/discovered-sources/10/check")
        )
      ).toBe(true);
    });
    vi.restoreAllMocks();
  });

  it("creates a domain trust profile from the management panel", async () => {
    const fetchMock = vi.spyOn(global, "fetch");
    fetchMock.mockImplementation(async () => jsonResponse([]));

    fetchMock
      .mockResolvedValueOnce(jsonResponse(wavePayload()))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(
        jsonResponse(
          {
            id: 1,
            domain: "agency.example.gov",
            trust_level: "trusted",
            approval_policy: "auto_approve_stable",
            notes: "gov feed",
            created_at: "2026-03-14T09:00:00Z",
            updated_at: "2026-03-14T09:00:00Z",
            source_count: 0,
            approved_source_count: 0,
            blocked_source_count: 0,
            average_stability_score: null,
            last_seen_at: null,
          },
          201
        )
      )
      .mockResolvedValueOnce(jsonResponse(wavePayload()))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(
        jsonResponse([
          {
            id: 1,
            domain: "agency.example.gov",
            trust_level: "trusted",
            approval_policy: "auto_approve_stable",
            notes: "gov feed",
            created_at: "2026-03-14T09:00:00Z",
            updated_at: "2026-03-14T09:00:00Z",
            source_count: 0,
            approved_source_count: 0,
            blocked_source_count: 0,
            average_stability_score: null,
            last_seen_at: null,
          },
        ])
      );

    render(
      <MemoryRouter initialEntries={["/waves/1"]}>
        <Routes>
          <Route element={<WaveDetailPage />} path="/waves/:waveId" />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Domain Trust" })).toBeInTheDocument()
    );

    fireEvent.change(screen.getAllByPlaceholderText("example.gov")[0], {
      target: { value: "agency.example.gov" },
    });
    fireEvent.change(screen.getByDisplayValue("neutral"), {
      target: { value: "trusted" },
    });
    fireEvent.change(screen.getByDisplayValue("manual_review"), {
      target: { value: "auto_approve_stable" },
    });
    fireEvent.change(screen.getByPlaceholderText("why this domain is trusted"), {
      target: { value: "gov feed" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Add Domain Trust" }));

    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some(
          (call) =>
            typeof call[0] === "string" &&
            call[0].includes("/api/domain-trust") &&
            typeof call[1] === "object" &&
            call[1] !== null &&
            "method" in call[1] &&
            (call[1] as RequestInit).method === "POST"
        )
      ).toBe(true);
    });
    expect(screen.getByText(/Created trust profile for agency.example.gov/)).toBeInTheDocument();
    vi.restoreAllMocks();
  });

  it("refreshes discovered source policy state after trust profile update", async () => {
    const fetchMock = vi.spyOn(global, "fetch");
    fetchMock.mockImplementation(async () => jsonResponse([]));

    const initialSource = {
      id: 10,
      wave_id: 1,
      url: "https://policy.example.gov/feed.xml",
      title: "feed.xml",
      source_type: "rss",
      parent_domain: "policy.example.gov",
      status: "new",
      discovery_method: "seed+page-inspection",
      relevance_score: 0.9,
      stability_score: 0.78,
      free_access: true,
      suggested_connector_type: "rss_news",
      description_summary: null,
      metadata_json: {},
      discovered_at: "2026-03-14T10:00:00Z",
      auto_check_enabled: true,
      check_interval_minutes: 60,
      next_check_at: "2026-03-14T11:00:00Z",
      consecutive_failures: 0,
      last_checked_at: "2026-03-14T10:00:00Z",
      last_success_at: "2026-03-14T10:00:00Z",
      failure_count: 0,
      last_http_status: 200,
      last_content_type: "application/rss+xml",
      domain_trust_level: "neutral",
      domain_approval_policy: "manual_review",
      policy_state: "manual_review",
      policy_reason: "Domain is not trusted for auto-approval.",
      approval_origin: null,
      policy_source: "global_domain_trust",
      wave_trust_override_id: null,
      global_domain_trust_profile_id: 1,
    };
    const blockedSource = {
      ...initialSource,
      status: "rejected",
      domain_trust_level: "blocked",
      domain_approval_policy: "auto_reject",
      policy_state: "blocked",
      policy_reason: "Domain policy blocks this source.",
      approval_origin: "policy_blocked",
      policy_source: "global_domain_trust",
      wave_trust_override_id: null,
      global_domain_trust_profile_id: 1,
    };

    fetchMock
      .mockResolvedValueOnce(jsonResponse(wavePayload()))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([initialSource]))
      .mockResolvedValueOnce(
        jsonResponse([
          {
            id: 1,
            domain: "policy.example.gov",
            trust_level: "neutral",
            approval_policy: "manual_review",
            notes: null,
            created_at: "2026-03-14T09:00:00Z",
            updated_at: "2026-03-14T09:00:00Z",
            source_count: 1,
            approved_source_count: 0,
            blocked_source_count: 0,
            average_stability_score: 0.78,
            last_seen_at: "2026-03-14T10:00:00Z",
          },
        ])
      )
      .mockResolvedValueOnce(
        jsonResponse({
          id: 1,
          domain: "policy.example.gov",
          trust_level: "blocked",
          approval_policy: "auto_reject",
          notes: null,
          created_at: "2026-03-14T09:00:00Z",
          updated_at: "2026-03-14T11:00:00Z",
          source_count: 1,
          approved_source_count: 0,
          blocked_source_count: 1,
          average_stability_score: 0.78,
          last_seen_at: "2026-03-14T10:00:00Z",
        })
      )
      .mockResolvedValueOnce(jsonResponse(wavePayload()))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([blockedSource]))
      .mockResolvedValueOnce(
        jsonResponse([
          {
            id: 1,
            domain: "policy.example.gov",
            trust_level: "blocked",
            approval_policy: "auto_reject",
            notes: null,
            created_at: "2026-03-14T09:00:00Z",
            updated_at: "2026-03-14T11:00:00Z",
            source_count: 1,
            approved_source_count: 0,
            blocked_source_count: 1,
            average_stability_score: 0.78,
            last_seen_at: "2026-03-14T10:00:00Z",
          },
        ])
      );

    render(
      <MemoryRouter initialEntries={["/waves/1"]}>
        <Routes>
          <Route element={<WaveDetailPage />} path="/waves/:waveId" />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText(/Policy: manual_review/)).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "Edit" }));
    fireEvent.change(screen.getByDisplayValue("neutral"), {
      target: { value: "blocked" },
    });
    fireEvent.change(screen.getByDisplayValue("manual_review"), {
      target: { value: "auto_reject" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Update Domain Trust" }));

    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some(
          (call) =>
            typeof call[0] === "string" &&
            call[0].includes("/api/domain-trust/1") &&
            typeof call[1] === "object" &&
            call[1] !== null &&
            "method" in call[1] &&
            (call[1] as RequestInit).method === "PATCH"
        )
      ).toBe(true);
    });
  });
});
