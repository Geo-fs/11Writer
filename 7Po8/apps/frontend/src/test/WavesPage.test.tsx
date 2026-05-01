import { render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { vi } from "vitest";

import { WavesPage } from "../pages/WavesPage";

describe("WavesPage", () => {
  it("renders waves list and create form", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify([]), { status: 200, headers: { "Content-Type": "application/json" } })
    );

    render(
      <BrowserRouter>
        <WavesPage />
      </BrowserRouter>
    );

    expect(screen.getByRole("heading", { name: "Create Wave" })).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("No waves created yet.")).toBeInTheDocument());
    vi.restoreAllMocks();
  });
});
