import { chromium } from "playwright";

const baseUrl = process.argv[2] ?? "http://127.0.0.1:8000";
const phase = process.argv[3] ?? "full";

async function waitForDebugReady(page) {
  await page.waitForFunction(() => Boolean(window.__worldviewDebug), null, { timeout: 30_000 });
  await page.waitForFunction(() => Boolean(window.__worldviewDebug?.isViewerReady?.()), null, {
    timeout: 60_000
  });
}

async function waitForEntityData(page) {
  await page.waitForFunction(() => {
    const state = window.__worldviewDebug?.getState?.();
    return Boolean(state && state.aircraftEntities.length > 0 && state.satelliteEntities.length > 0);
  }, null, { timeout: 60_000 });
}

async function waitForCameraData(page) {
  await page.waitForFunction(() => {
    const state = window.__worldviewDebug?.getState?.();
    return Boolean(state && state.cameraEntities.length > 0);
  }, null, { timeout: 60_000 });
}

async function installCaptureHooks(page) {
  await page.evaluate(() => {
    window.__clipboardWrites = [];
    Object.defineProperty(navigator, "clipboard", {
      value: {
        writeText: async (value) => {
          window.__clipboardWrites.push(String(value));
        }
      },
      configurable: true
    });

    window.__downloadCapture = { count: 0, latest: null };
    if (!window.__worldviewOriginalAnchorClick) {
      window.__worldviewOriginalAnchorClick = HTMLAnchorElement.prototype.click;
      HTMLAnchorElement.prototype.click = function click() {
        if (this.download) {
          window.__downloadCapture = {
            count: (window.__downloadCapture?.count ?? 0) + 1,
            latest: {
              href: this.href,
              download: this.download
            }
          };
        }
        return window.__worldviewOriginalAnchorClick.call(this);
      };
    }
  });
}

function assertIncludes(text, fragments, label) {
  for (const fragment of fragments) {
    if (!text.includes(fragment)) {
      throw new Error(`${label} missing fragment: ${fragment}`);
    }
  }
}

async function collectDiagnostics(page, label, consoleMessages, pageErrors) {
  let state = null;
  try {
      state = await page.evaluate(() => ({
        href: window.location.href,
        hasDebug: Boolean(window.__worldviewDebug),
        viewerReady: Boolean(window.__worldviewDebug?.isViewerReady?.()),
        selectedEntityId: window.__worldviewDebug?.getState?.().selectedEntity?.id ?? null,
        selectedEntityStoreId: window.__worldviewDebug?.getState?.().selectedEntityId ?? null,
        filters: window.__worldviewDebug?.getState?.().filters ?? null,
        aircraftCount: window.__worldviewDebug?.getState?.().aircraftEntities?.length ?? 0,
        satelliteCount: window.__worldviewDebug?.getState?.().satelliteEntities?.length ?? 0,
        rootText: document.querySelector("#root")?.textContent?.slice(0, 600) ?? null,
      viewportHealth: document.querySelector(".viewport__health")?.textContent ?? null
    }));
  } catch (error) {
    state = { stateError: String(error) };
  }

  return {
    label,
    state,
    console: consoleMessages.slice(-20),
    pageErrors: pageErrors.slice(-10)
  };
}

async function createPhasePage(browser) {
  const context = await browser.newContext();
  const page = await context.newPage();
  const consoleMessages = [];
  const pageErrors = [];
  page.on("console", (message) => {
    consoleMessages.push(`[${message.type()}] ${message.text()}`);
  });
  page.on("pageerror", (error) => {
    pageErrors.push(String(error));
  });
  return { context, page, consoleMessages, pageErrors };
}

async function clickCanvasAt(page, point) {
  await page.mouse.click(point.clientX, point.clientY);
}

async function setLayerEnabled(page, label, enabled) {
  const layerRow = page.locator(".panel--left .toggle-row", { hasText: label }).first();
  const checkbox = layerRow.locator('input[type="checkbox"]');
  const isChecked = await checkbox.isChecked();
  if (isChecked !== enabled) {
    if (enabled) {
      await checkbox.check();
    } else {
      await checkbox.uncheck();
    }
  }
}

async function runCanvasAircraftPhase(browser) {
  const { context, page, consoleMessages, pageErrors } = await createPhasePage(browser);
  try {
    await page.goto(baseUrl, { waitUntil: "networkidle" });
    await waitForDebugReady(page);
    await waitForEntityData(page);
    await setLayerEnabled(page, "Satellites", false);
    await setLayerEnabled(page, "Debug", true);

    const preAustinProbe = await page.evaluate(() => ({
      clickPoint: window.__worldviewDebug.findEntityClickPoint("aircraft:test-def456"),
      projectedPoint: window.__worldviewDebug.getEntityScreenPosition("aircraft:test-def456")
    }));

    await page.getByRole("button", { name: "Austin" }).click();
    await page.waitForTimeout(900);

    const postAustinProbe = await page.evaluate(() => ({
      clickPoint: window.__worldviewDebug.findEntityClickPoint("aircraft:test-def456"),
      projectedPoint: window.__worldviewDebug.getEntityScreenPosition("aircraft:test-def456")
    }));
    if (!postAustinProbe.clickPoint) {
      throw new Error(
        `Aircraft click point was unavailable after Austin preset. preAustin=${JSON.stringify(preAustinProbe)} postAustin=${JSON.stringify(postAustinProbe)}`
      );
    }

    await clickCanvasAt(page, postAustinProbe.clickPoint);
    await page.waitForFunction(
      () => window.__worldviewDebug.getState().selectedEntity?.id === "aircraft:test-def456",
      null,
      { timeout: 30_000 }
    );

    const inspectorText = await page.locator(".panel--right").textContent();
    assertIncludes(
      inspectorText ?? "",
      ["UAL456", "OpenSky Network state vectors", "Observed", "Fetched"],
      "canvas aircraft inspector"
    );

    await setLayerEnabled(page, "Satellites", true);

    return {
      selected: "aircraft:test-def456",
      preAustinProbe,
      postAustinProbe
    };
  } catch (error) {
    return {
      errors: [String(error)],
      diagnostics: await collectDiagnostics(page, "canvas-aircraft", consoleMessages, pageErrors)
    };
  } finally {
    await context.close();
  }
}

async function runCanvasSatellitePhase(browser) {
  const { context, page, consoleMessages, pageErrors } = await createPhasePage(browser);
  try {
    await page.goto(baseUrl, { waitUntil: "networkidle" });
    await waitForDebugReady(page);
    await waitForEntityData(page);
    await setLayerEnabled(page, "Aircraft", false);
    await page.waitForTimeout(400);

    let point = await page.evaluate(() =>
      window.__worldviewDebug.findEntityClickPoint("satellite:25544")
    );
    if (!point) {
      throw new Error("Satellite click point was unavailable.");
    }

    let selected = false;
    for (let attempt = 0; attempt < 2 && !selected; attempt += 1) {
      await clickCanvasAt(page, point);
      try {
        await page.waitForFunction(
          () => window.__worldviewDebug.getState().selectedEntity?.id === "satellite:25544",
          null,
          { timeout: 10_000 }
        );
        selected = true;
      } catch {
        point = await page.evaluate(() =>
          window.__worldviewDebug.findEntityClickPoint("satellite:25544")
        );
        if (!point) {
          break;
        }
      }
    }
    if (!selected) {
      throw new Error("Satellite did not settle into selected state after direct canvas clicks.");
    }

    const inspectorText = await page.locator(".panel--right").textContent();
    assertIncludes(
      inspectorText ?? "",
      ["ISS (ZARYA)", "CelesTrak active catalog via GP data", "Pass Window (Derived)"],
      "canvas satellite inspector"
    );

    return {
      selected: "satellite:25544"
    };
  } catch (error) {
    return {
      errors: [String(error)],
      diagnostics: await collectDiagnostics(page, "canvas-satellite", consoleMessages, pageErrors)
    };
  } finally {
    await context.close();
  }
}

async function runAircraftPhase(browser) {
  const { context, page, consoleMessages, pageErrors } = await createPhasePage(browser);
  try {
    await page.goto(`${baseUrl}/?selected=aircraft%3Atest-abc123`, { waitUntil: "networkidle" });
    await waitForDebugReady(page);
    await installCaptureHooks(page);

    await page.waitForFunction(
      () => window.__worldviewDebug.getState().selectedEntity?.id === "aircraft:test-abc123",
      null,
      { timeout: 60_000 }
    );
    await page.waitForFunction(() => {
      const text = document.querySelector(".panel--right")?.textContent ?? "";
      return text.includes("Aviation Context (Derived)") && text.includes("Nearest airport");
    }, null, { timeout: 30_000 });

    const inspectorText = await page.locator(".panel--right").textContent();
    assertIncludes(
      inspectorText ?? "",
      [
        "DAL123",
        "OpenSky Network state vectors",
        "Observed",
        "Fetched",
        "icao24",
        "origin_country raw",
        "Quality Metadata",
        "History",
        "Recent Activity",
        "Observed session history / live-polled",
        "Altitude trend",
        "Speed trend",
        "Heading behavior",
        "Snapshot Evidence",
        "Recent Movement",
        "Aviation Context (Derived)",
        "Nearest airport",
        "Nearest runway threshold",
        "Link Targets",
        "Replay note:"
      ],
      "aircraft inspector"
    );
    if (!(inspectorText?.includes("Austin-Bergstrom International Airport") || inspectorText?.includes("KAUS"))) {
      throw new Error("Aircraft aviation context did not include the expected airport reference.");
    }
    if (
      !(
        inspectorText?.includes("Observed session trail") ||
        inspectorText?.includes("No recent movement track.")
      )
    ) {
      throw new Error("Aircraft recent-movement state was missing both trail and empty-state labels.");
    }

    await page.getByRole("button", { name: "Copy Permalink" }).click();
    const copiedPermalink = await page.evaluate(() => window.__clipboardWrites.at(-1) ?? "");
    if (!copiedPermalink.includes("selected=aircraft%3Atest-abc123")) {
      throw new Error(`Aircraft permalink missing selected target: ${copiedPermalink}`);
    }

    await page.getByRole("button", { name: "Export Snapshot" }).click();
    const snapshotCapture = await page.evaluate(() => window.__downloadCapture);
    if (!snapshotCapture?.count || !snapshotCapture?.latest?.download?.includes("worldview-observation-")) {
      throw new Error("Snapshot export did not trigger a download capture.");
    }
    const snapshotMetadata = await page.evaluate(() => window.__worldviewLastSnapshotMetadata ?? null);
    if (!snapshotMetadata?.selectedTargetSummary || snapshotMetadata.selectedTargetSummary.type !== "aircraft") {
      throw new Error("Aircraft snapshot metadata did not preserve the selected-target aircraft summary.");
    }
    if (!String(snapshotMetadata.imageryDisclosure ?? "").length) {
      throw new Error("Aircraft snapshot metadata did not preserve imagery disclosure.");
    }

    const beforeHeight = await page.evaluate(
      () => window.__worldviewDebug.getViewer().camera.positionCartographic.height
    );
    await page.getByRole("button", { name: "Follow Target" }).click();
    await page.waitForFunction(
      () => window.__worldviewDebug.getState().followedEntityId === "aircraft:test-abc123",
      null,
      { timeout: 30_000 }
    );
    await page.waitForTimeout(500);
    const afterHeight = await page.evaluate(
      () => window.__worldviewDebug.getViewer().camera.positionCartographic.height
    );
    if (Math.abs(beforeHeight - afterHeight) <= 1000) {
      throw new Error("Aircraft follow target did not move the camera enough to validate.");
    }

    const aircraftRequests = [];
    page.on("request", (request) => {
      if (request.url().includes("/api/aircraft?")) {
        aircraftRequests.push(request.url());
      }
    });

    await page.getByLabel("Observed After (local)").fill("2026-04-04T05:30");
    await page.getByLabel("Max Altitude (m)").fill("5000");
    await page.getByRole("textbox", { name: "Source", exact: true }).fill("opensky-network");
    await page.waitForFunction(
      () => {
        const state = window.__worldviewDebug.getState();
        return (
          state.filters.observedAfter === "2026-04-04T05:30" &&
          state.filters.maxAltitude === 5000 &&
          state.filters.source === "opensky-network"
        );
      },
      null,
      { timeout: 30_000 }
    );
    await page.waitForTimeout(1500);
    const latestAircraftUrl = aircraftRequests.at(-1) ?? "";
    if (!latestAircraftUrl.includes("observed_after=2026-04-04T10%3A30%3A00.000Z")) {
      throw new Error(`Observed-after filter did not normalize to ISO: ${latestAircraftUrl}`);
    }
    if (!latestAircraftUrl.includes("max_altitude=5000") || !latestAircraftUrl.includes("source=opensky-network")) {
      throw new Error(`Aircraft filter mismatch: ${latestAircraftUrl}`);
    }

    const leftPanelText = await page.locator(".panel--left").textContent();
    if (!(leftPanelText ?? "").includes("History Window (session only)")) {
      throw new Error("Session-only history labeling is missing.");
    }
    return {
      selected: "aircraft:test-abc123",
      copiedPermalink,
      latestAircraftUrl
    };
  } catch (error) {
    return {
      errors: [String(error)],
      diagnostics: await collectDiagnostics(page, "aircraft", consoleMessages, pageErrors)
    };
  } finally {
    await context.close();
  }
}

async function runSatellitePhase(browser) {
  const { context, page, consoleMessages, pageErrors } = await createPhasePage(browser);
  try {
    await page.goto(`${baseUrl}/?selected=satellite%3A25544`, { waitUntil: "networkidle" });
    await waitForDebugReady(page);
    await installCaptureHooks(page);

    await page.waitForFunction(
      () => window.__worldviewDebug.getState().selectedEntity?.id === "satellite:25544",
      null,
      { timeout: 60_000 }
    );

    const inspectorText = await page.locator(".panel--right").textContent();
    assertIncludes(
      inspectorText ?? "",
      [
        "ISS (ZARYA)",
        "CelesTrak active catalog via GP data",
        "norad_id",
        "object_id",
        "Derived Fields",
        "Recent Activity",
        "Derived propagated track",
        "Replay relation",
        "Snapshot Evidence",
        "Pass Window (Derived)",
        "Nearby Context",
        "Recent Movement",
        "Derived propagation trail",
        "Replay Cursor",
        "Replay note:"
      ],
      "satellite inspector"
    );

    const orbitVisible = await page.evaluate(() => {
      const viewer = window.__worldviewDebug.getViewer();
      const sources = viewer.dataSources._dataSources ?? viewer.dataSources.values ?? [];
      return sources
        .flatMap((source) => source.entities.values)
        .some((entity) => entity.id === "satellite:25544" && entity.polyline != null);
    });
    if (!orbitVisible) {
      throw new Error("Satellite orbit path was not present on the selected satellite.");
    }

    const beforeHeight = await page.evaluate(
      () => window.__worldviewDebug.getViewer().camera.positionCartographic.height
    );
    await page.getByRole("button", { name: "Follow Target" }).click();
    await page.waitForFunction(
      () => window.__worldviewDebug.getState().followedEntityId === "satellite:25544",
      null,
      { timeout: 30_000 }
    );
    await page.waitForTimeout(1800);
    const afterHeight = await page.evaluate(
      () => window.__worldviewDebug.getViewer().camera.positionCartographic.height
    );
    if (Math.abs(beforeHeight - afterHeight) <= 1000) {
      throw new Error("Satellite follow target did not move the camera enough to validate.");
    }

    await page.getByRole("button", { name: "Export Snapshot" }).click();
    const snapshotCapture = await page.evaluate(() => window.__downloadCapture);
    if (!snapshotCapture?.count || !snapshotCapture?.latest?.download?.includes("worldview-observation-")) {
      throw new Error("Satellite snapshot export did not trigger a download capture.");
    }
    const snapshotMetadata = await page.evaluate(() => window.__worldviewLastSnapshotMetadata ?? null);
    if (!snapshotMetadata?.selectedTargetSummary || snapshotMetadata.selectedTargetSummary.type !== "satellite") {
      throw new Error("Satellite snapshot metadata did not preserve the selected-target satellite summary.");
    }
    if (!String(snapshotMetadata.imageryDisclosure ?? "").length) {
      throw new Error("Satellite snapshot metadata did not preserve imagery disclosure.");
    }

    return {
      selected: "satellite:25544",
      orbitVisible
    };
  } catch (error) {
    return {
      errors: [String(error)],
      diagnostics: await collectDiagnostics(page, "satellite", consoleMessages, pageErrors)
    };
  } finally {
    await context.close();
  }
}

async function runRestorePhase(browser) {
  const { context, page, consoleMessages, pageErrors } = await createPhasePage(browser);
  try {
    await page.goto(
      `${baseUrl}/?selected=aircraft%3Atest-abc123&source=opensky-network&maxAltitude=5000&observedAfter=2026-04-04T05%3A30`,
      { waitUntil: "networkidle" }
    );
    await waitForDebugReady(page);
    await installCaptureHooks(page);

    await page.waitForFunction(() => {
      const state = window.__worldviewDebug.getState();
      return (
        state.filters.source === "opensky-network" &&
        state.filters.maxAltitude === 5000 &&
        state.filters.observedAfter === "2026-04-04T05:30"
      );
    }, null, { timeout: 60_000 });
    await page.waitForFunction(
      () => window.__worldviewDebug.getState().selectedEntityId === "aircraft:test-abc123",
      null,
      { timeout: 60_000 }
    );

    return await page.evaluate(() => {
      const state = window.__worldviewDebug.getState();
      return {
        selectedEntityId: state.selectedEntity?.id ?? null,
        source: state.filters.source,
        maxAltitude: state.filters.maxAltitude,
        observedAfter: state.filters.observedAfter
      };
    });
  } catch (error) {
    return {
      errors: [String(error)],
      diagnostics: await collectDiagnostics(page, "restore", consoleMessages, pageErrors)
    };
  } finally {
    await context.close();
  }
}

async function runWebcamPhase(browser) {
  const { context, page, consoleMessages, pageErrors } = await createPhasePage(browser);
  try {
    const selectedCameraId = encodeURIComponent("camera:usgs-ashcam:akutan-north");
    await page.goto(`${baseUrl}/?selected=${selectedCameraId}`, { waitUntil: "networkidle" });
    await waitForDebugReady(page);
    await waitForCameraData(page);

    const sourceCard = page.getByTestId("webcam-source-card-usgs-ashcam");
    await sourceCard.waitFor({ timeout: 30_000 });
    const sourceText = await sourceCard.textContent();
    assertIncludes(
      sourceText ?? "",
      ["USGS AshCam", "Validated", "Discovered 425", "Usable 356", "Direct-image 268", "Viewer-only 88"],
      "webcam source card"
    );

    const candidateCard = page.getByTestId("webcam-source-card-faa-weather-cameras-page");
    const candidateText = await candidateCard.textContent();
    assertIncludes(
      candidateText ?? "",
      ["Candidate only", "interactive-map-html", "Likely camera count 299", "Compliance risk medium"],
      "faa candidate card"
    );

    const reviewPanelText = await page.getByTestId("webcam-review-queue-panel").textContent();
    assertIncludes(
      reviewPanelText ?? "",
      ["Webcam Review Queue", "Spurr Overlook", "Viewer-only"],
      "webcam review queue"
    );

    const inspectorText = await page.locator(".panel--right").textContent();
    assertIncludes(
      inspectorText ?? "",
      ["Akutan North", "Source ID", "usgs-ashcam", "Direct-image", "Reference Hint", "Facility Code Hint", "Validated"],
      "direct-image webcam inspector"
    );

    await page.getByTestId("webcam-filter-direct-image").check();
    await page.waitForFunction(
      () => window.__worldviewDebug.getState().cameraEntities.length === 1,
      null,
      { timeout: 30_000 }
    );

    await page.getByTestId("webcam-filter-direct-image").uncheck();
    await page.getByTestId("webcam-filter-viewer-only").check();
    await page.waitForFunction(
      () =>
        window.__worldviewDebug.getState().cameraEntities.length === 1 &&
        window.__worldviewDebug.getState().cameraEntities[0]?.id === "camera:usgs-ashcam:spurr-overlook",
      null,
      { timeout: 30_000 }
    );
    await page.evaluate(() =>
      window.__worldviewDebug.setSelectedEntityId("camera:usgs-ashcam:spurr-overlook")
    );
    await page.waitForFunction(
      () => window.__worldviewDebug.getState().selectedEntity?.id === "camera:usgs-ashcam:spurr-overlook",
      null,
      { timeout: 30_000 }
    );

    const viewerInspectorText = await page.locator(".panel--right").textContent();
    assertIncludes(
      viewerInspectorText ?? "",
      ["Spurr Overlook", "Viewer fallback only.", "Viewer-only", "needs-review", "Reference Hint", "Facility Code Hint"],
      "viewer-only webcam inspector"
    );

    return {
      selected: "camera:usgs-ashcam:spurr-overlook",
      sourceCard: sourceText,
      candidateCard: candidateText
    };
  } catch (error) {
    return {
      errors: [String(error)],
      diagnostics: await collectDiagnostics(page, "webcam", consoleMessages, pageErrors)
    };
  } finally {
    await context.close();
  }
}

async function runMarinePhase(browser) {
  const { context, page, consoleMessages, pageErrors } = await createPhasePage(browser);
  try {
    await page.goto(baseUrl, { waitUntil: "networkidle" });
    await waitForDebugReady(page);

    await page.waitForSelector('[data-testid="marine-anomaly-section"]', { timeout: 60_000 });
    await page.waitForSelector('[data-testid="marine-anomaly-panel"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-chokepoint-priority"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-attention-queue"]', { timeout: 30_000 });

    const sectionText = await page.locator('[data-testid="marine-anomaly-section"]').textContent();
    assertIncludes(
      sectionText ?? "",
      ["Marine Attention Priority", "Observed signals", "Inferred signals", "Scored signals", "Attention priority is a review signal"],
      "marine anomaly section"
    );

    const initialRanks = await page.locator('[data-testid="marine-chokepoint-slice-item"] strong').allTextContents();
    if (initialRanks.length >= 2 && !(initialRanks[0].includes("#1") && initialRanks[1].includes("#2"))) {
      throw new Error(`Unexpected marine slice rank ordering: ${JSON.stringify(initialRanks)}`);
    }

    await page.locator('[data-testid="marine-chokepoint-filter"] select').selectOption("high");
    await page.waitForTimeout(300);
    const highCount = await page.locator('[data-testid="marine-chokepoint-slice-item"]').count();
    if (highCount < 1) {
      throw new Error("High-only filter produced zero marine chokepoint slices unexpectedly.");
    }

    await page.locator('[data-testid="marine-chokepoint-filter"] select').selectOption("all");
    await page.locator('[data-testid="marine-chokepoint-sort"] select').selectOption("score");
    await page.waitForTimeout(300);

    const queueText = await page.locator('[data-testid="marine-attention-queue"]').textContent();
    assertIncludes(queueText ?? "", ["vessel", "viewport", "chokepoint"], "marine attention queue");

    return {
      initialRanks,
      highCount
    };
  } catch (error) {
    return {
      errors: [String(error)],
      diagnostics: await collectDiagnostics(page, "marine", consoleMessages, pageErrors)
    };
  } finally {
    await context.close();
  }
}

async function runEarthquakePhase(browser) {
  const { context, page, consoleMessages, pageErrors } = await createPhasePage(browser);
  try {
    await page.goto(baseUrl, { waitUntil: "networkidle" });
    await waitForDebugReady(page);
    await installCaptureHooks(page);

    const earthquakeRow = page.locator(".panel--left .toggle-row", { hasText: "Earthquakes" }).first();
    await earthquakeRow.waitFor({ timeout: 30_000 });
    await earthquakeRow.locator('input[type="checkbox"]').check();

    await page.waitForFunction(
      () => (window.__worldviewDebug.getState().earthquakeEntities?.length ?? 0) > 0,
      null,
      { timeout: 30_000 }
    );

    await page.getByText("Earthquake Window").waitFor({ timeout: 30_000 });
    await page.getByText("Min Magnitude").waitFor({ timeout: 30_000 });
    await page.getByText("Event Limit").waitFor({ timeout: 30_000 });

    const initialCount = await page.evaluate(
      () => window.__worldviewDebug.getState().earthquakeEntities?.length ?? 0
    );

    const minMagnitudeInput = page.locator(".panel--left label", { hasText: "Min Magnitude" }).locator("input");
    await minMagnitudeInput.fill("5.5");
    await page.waitForFunction(
      (expectedMax) => {
        const count = window.__worldviewDebug.getState().earthquakeEntities?.length ?? 0;
        return count >= 0 && count <= expectedMax;
      },
      initialCount,
      { timeout: 30_000 }
    );

    const firstItem = page.locator('[data-testid^="earthquake-item-"]').first();
    await firstItem.waitFor({ timeout: 30_000 });
    await firstItem.click();

    await page.waitForFunction(
      () => window.__worldviewDebug.getState().selectedEntity?.type === "environmental-event",
      null,
      { timeout: 30_000 }
    );

    const inspectorText = await page.getByTestId("earthquake-inspector").textContent();
    assertIncludes(
      inspectorText ?? "",
      ["Environmental Event (USGS)", "Magnitude", "Event Time", "Depth", "Source", "Caveat"],
      "earthquake inspector"
    );

    await page.getByRole("button", { name: "Export Snapshot" }).click();
    const snapshotMetadata = await page.evaluate(() => window.__worldviewLastSnapshotMetadata ?? null);
    if (!snapshotMetadata?.earthquakeLayerSummary) {
      throw new Error("Earthquake snapshot metadata did not include earthquake layer summary.");
    }
    if (!snapshotMetadata?.selectedTargetSummary || snapshotMetadata.selectedTargetSummary.type !== "environmental-event") {
      throw new Error("Earthquake snapshot metadata did not preserve selected earthquake summary.");
    }

    return {
      initialCount,
      filteredCount: await page.evaluate(
        () => window.__worldviewDebug.getState().earthquakeEntities?.length ?? 0
      ),
      selectedType: await page.evaluate(() => window.__worldviewDebug.getState().selectedEntity?.type ?? null)
    };
  } catch (error) {
    return {
      errors: [String(error)],
      diagnostics: await collectDiagnostics(page, "earthquake", consoleMessages, pageErrors)
    };
  } finally {
    await context.close();
  }
}

const browser = await chromium.launch({ headless: true });

try {
  if (phase === "marine") {
    const marine = await runMarinePhase(browser);
    console.log(JSON.stringify({ marine }, null, 2));
  } else if (phase === "earthquake") {
    const earthquake = await runEarthquakePhase(browser);
    console.log(JSON.stringify({ earthquake }, null, 2));
  } else if (phase === "aerospace") {
    const canvasAircraft = await runCanvasAircraftPhase(browser);
    const canvasSatellite = await runCanvasSatellitePhase(browser);
    const aircraft = await runAircraftPhase(browser);
    const satellite = await runSatellitePhase(browser);
    const restore = await runRestorePhase(browser);
    console.log(JSON.stringify({ canvasAircraft, canvasSatellite, aircraft, satellite, restore }, null, 2));
  } else {
    const canvasAircraft = await runCanvasAircraftPhase(browser);
    const canvasSatellite = await runCanvasSatellitePhase(browser);
    const aircraft = await runAircraftPhase(browser);
    const satellite = await runSatellitePhase(browser);
    const restore = await runRestorePhase(browser);
    const webcam = await runWebcamPhase(browser);
    const earthquake = await runEarthquakePhase(browser);
    console.log(JSON.stringify({ canvasAircraft, canvasSatellite, aircraft, satellite, restore, webcam, earthquake }, null, 2));
  }
} finally {
  await browser.close();
}
