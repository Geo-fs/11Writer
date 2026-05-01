import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { vi } from "vitest";

import { WaveDetailPage } from "../pages/WaveDetailPage";

describe("WaveDetailPage", () => {
  it("renders connector and record sections", async () => {
    vi.spyOn(global, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      if (url.endsWith("/api/waves/1")) {
        return new Response(
          JSON.stringify({
            id: 1,
            name: "Test Wave",
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
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      return new Response(JSON.stringify([]), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    });

    render(
      <MemoryRouter initialEntries={["/waves/1"]}>
        <Routes>
          <Route element={<WaveDetailPage />} path="/waves/:waveId" />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByRole("heading", { name: "Test Wave" })).toBeInTheDocument());
    expect(screen.getByRole("heading", { name: "Connectors" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Source Discovery" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Domain Trust" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Wave Trust Overrides" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Policy Action History" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Records" })).toBeInTheDocument();
    vi.restoreAllMocks();
  });
});
