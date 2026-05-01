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

describe("Wave detail filters", () => {
  it("renders filters and sends record search query", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      if (url.endsWith("/api/waves/1")) {
        return jsonResponse({
          id: 1,
          name: "Filter Wave",
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
        });
      }
      if (url.includes("/api/waves/1/connectors")) {
        return jsonResponse([]);
      }
      if (url.includes("/api/waves/1/records")) {
        return jsonResponse([]);
      }
      if (url.includes("/api/waves/1/runs")) {
        return jsonResponse([]);
      }
      if (url.includes("/api/waves/1/signals")) {
        return jsonResponse([]);
      }
      if (url.includes("/api/waves/1/discovered-sources")) {
        return jsonResponse([]);
      }
      return jsonResponse([]);
    });

    render(
      <MemoryRouter initialEntries={["/waves/1"]}>
        <Routes>
          <Route element={<WaveDetailPage />} path="/waves/:waveId" />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByRole("heading", { name: "Records" })).toBeInTheDocument());
    expect(screen.getByText("Clear Record Filters")).toBeInTheDocument();
    expect(screen.getByText("Clear Signal Filters")).toBeInTheDocument();
    expect(screen.getByText("Clear Source Filters")).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText("title/content/source..."), {
      target: { value: "airport" },
    });

    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some(
          (call) =>
            String(call[0]).includes("/api/waves/1/records") &&
            String(call[0]).includes("text_search=airport")
        )
      ).toBe(true);
    });
    vi.restoreAllMocks();
  });
});
