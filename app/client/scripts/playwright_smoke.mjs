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
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
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
    await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
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
        "Replay note:",
        "Aerospace Context Review",
        "Aerospace Export Readiness",
        "Aerospace Source Readiness",
        "Aerospace Context Report",
        "Aerospace Review Queue",
        "Geomagnetism (USGS)",
        "Space Weather Archive Context",
        "Volcanic Ash Advisory Context"
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
    if (!snapshotMetadata?.aviationWeatherContext?.airportCode) {
      throw new Error("Aircraft snapshot metadata missing AWC aviation weather context.");
    }
    if (snapshotMetadata.aviationWeatherContext?.sourceHealthState !== "healthy") {
      throw new Error(
        `Aircraft AWC metadata expected healthy source state. Received ${snapshotMetadata.aviationWeatherContext?.sourceHealthState}`
      );
    }
    if (!snapshotMetadata?.faaNasAirportStatus?.airportCode) {
      throw new Error("Aircraft snapshot metadata missing FAA NAS airport-status context.");
    }
    if (!snapshotMetadata?.geomagnetismContext?.observatoryId) {
      throw new Error("Aircraft snapshot metadata missing geomagnetism context.");
    }
    if (!snapshotMetadata?.nceiSpaceWeatherArchiveContext?.collectionId) {
      throw new Error("Aircraft snapshot metadata missing NCEI archive context.");
    }
    if (!snapshotMetadata?.vaacContext?.sourceCount && snapshotMetadata?.vaacContext?.sourceCount !== 0) {
      throw new Error("Aircraft snapshot metadata missing VAAC context.");
    }
    if (!snapshotMetadata?.aerospaceContextIssues?.issueCount && snapshotMetadata?.aerospaceContextIssues?.issueCount !== 0) {
      throw new Error("Aircraft snapshot metadata missing aerospace context issue summary.");
    }
    if (!snapshotMetadata?.openskyAnonymousContext?.selectedTargetComparison) {
      throw new Error("Aircraft snapshot metadata missing OpenSky selected-target comparison.");
    }
    const openSkyComparisonStatus =
      snapshotMetadata.openskyAnonymousContext.selectedTargetComparison.matchStatus;
    if (!["exact-icao", "exact-callsign", "possible-callsign", "ambiguous", "no-match", "unavailable"].includes(openSkyComparisonStatus)) {
      throw new Error(`Aircraft OpenSky comparison status was not recognized: ${openSkyComparisonStatus}`);
    }
    if (!snapshotMetadata?.aerospaceOperationalContext?.sourceCount) {
      throw new Error("Aircraft snapshot metadata missing aerospace operational context.");
    }
    if (!snapshotMetadata?.aerospaceContextAvailability?.rows?.length) {
      throw new Error("Aircraft snapshot metadata missing aerospace context availability.");
    }
    if (!snapshotMetadata?.aerospaceExportReadiness?.category) {
      throw new Error("Aircraft snapshot metadata missing aerospace export readiness.");
    }
    if (!snapshotMetadata?.aerospaceSourceReadiness?.familyCount && snapshotMetadata?.aerospaceSourceReadiness?.familyCount !== 0) {
      throw new Error("Aircraft snapshot metadata missing aerospace source readiness.");
    }
    if (!snapshotMetadata?.aerospaceContextReport?.sourceCount && snapshotMetadata?.aerospaceContextReport?.sourceCount !== 0) {
      throw new Error("Aircraft snapshot metadata missing aerospace context report.");
    }
    if (!snapshotMetadata?.aerospaceReviewQueue?.itemCount && snapshotMetadata?.aerospaceReviewQueue?.itemCount !== 0) {
      throw new Error("Aircraft snapshot metadata missing aerospace review queue.");
    }
    if (!snapshotMetadata?.aerospaceExportProfile?.profileId) {
      throw new Error("Aircraft snapshot metadata missing aerospace export profile.");
    }
    if (!Array.isArray(snapshotMetadata?.geomagnetismContext?.displayLines)) {
      throw new Error("Aircraft geomagnetism metadata missing display lines.");
    }
    if (!Array.isArray(snapshotMetadata?.nceiSpaceWeatherArchiveContext?.displayLines)) {
      throw new Error("Aircraft NCEI archive metadata missing display lines.");
    }
    if (!Array.isArray(snapshotMetadata?.vaacContext?.sources)) {
      throw new Error("Aircraft VAAC metadata missing sources.");
    }
    if (!Array.isArray(snapshotMetadata?.aerospaceContextIssues?.topIssues)) {
      throw new Error("Aircraft aerospace context issue metadata missing top issues.");
    }
    if (!Array.isArray(snapshotMetadata?.aerospaceContextReport?.topCaveats)) {
      throw new Error("Aircraft aerospace context report metadata missing top caveats.");
    }
    if (!Array.isArray(snapshotMetadata?.aerospaceReviewQueue?.topItems)) {
      throw new Error("Aircraft aerospace review queue metadata missing top items.");
    }
    if (!Array.isArray(snapshotMetadata?.aerospaceSourceReadiness?.families)) {
      throw new Error("Aircraft aerospace source readiness metadata missing families.");
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
        "Replay note:",
        "Aerospace Context Review",
        "Aerospace Export Readiness",
        "Aerospace Source Readiness",
        "Aerospace Context Report",
        "Aerospace Review Queue",
        "Geomagnetism (USGS)",
        "Space Weather Archive Context",
        "Volcanic Ash Advisory Context"
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
    if (!snapshotMetadata?.cneosSpaceContext?.source) {
      throw new Error("Satellite snapshot metadata missing CNEOS space context.");
    }
    if (!snapshotMetadata?.swpcSpaceWeatherContext?.source) {
      throw new Error("Satellite snapshot metadata missing SWPC space-weather context.");
    }
    if (!snapshotMetadata?.geomagnetismContext?.observatoryId) {
      throw new Error("Satellite snapshot metadata missing geomagnetism context.");
    }
    if (!snapshotMetadata?.nceiSpaceWeatherArchiveContext?.collectionId) {
      throw new Error("Satellite snapshot metadata missing NCEI archive context.");
    }
    if (!snapshotMetadata?.vaacContext?.sourceCount && snapshotMetadata?.vaacContext?.sourceCount !== 0) {
      throw new Error("Satellite snapshot metadata missing VAAC context.");
    }
    if (!snapshotMetadata?.aerospaceContextIssues?.issueCount && snapshotMetadata?.aerospaceContextIssues?.issueCount !== 0) {
      throw new Error("Satellite snapshot metadata missing aerospace context issue summary.");
    }
    if (!snapshotMetadata?.aerospaceOperationalContext?.sourceCount) {
      throw new Error("Satellite snapshot metadata missing aerospace operational context.");
    }
    if (!snapshotMetadata?.aerospaceContextAvailability?.rows?.length) {
      throw new Error("Satellite snapshot metadata missing aerospace context availability.");
    }
    if (!snapshotMetadata?.aerospaceExportReadiness?.category) {
      throw new Error("Satellite snapshot metadata missing aerospace export readiness.");
    }
    if (!snapshotMetadata?.aerospaceSourceReadiness?.familyCount && snapshotMetadata?.aerospaceSourceReadiness?.familyCount !== 0) {
      throw new Error("Satellite snapshot metadata missing aerospace source readiness.");
    }
    if (!snapshotMetadata?.aerospaceContextReport?.sourceCount && snapshotMetadata?.aerospaceContextReport?.sourceCount !== 0) {
      throw new Error("Satellite snapshot metadata missing aerospace context report.");
    }
    if (!snapshotMetadata?.aerospaceReviewQueue?.itemCount && snapshotMetadata?.aerospaceReviewQueue?.itemCount !== 0) {
      throw new Error("Satellite snapshot metadata missing aerospace review queue.");
    }
    if (!snapshotMetadata?.aerospaceExportProfile?.profileId) {
      throw new Error("Satellite snapshot metadata missing aerospace export profile.");
    }
    if (!Array.isArray(snapshotMetadata?.geomagnetismContext?.displayLines)) {
      throw new Error("Satellite geomagnetism metadata missing display lines.");
    }
    if (!Array.isArray(snapshotMetadata?.nceiSpaceWeatherArchiveContext?.displayLines)) {
      throw new Error("Satellite NCEI archive metadata missing display lines.");
    }
    if (!Array.isArray(snapshotMetadata?.vaacContext?.sources)) {
      throw new Error("Satellite VAAC metadata missing sources.");
    }
    if (!Array.isArray(snapshotMetadata?.aerospaceContextIssues?.topIssues)) {
      throw new Error("Satellite aerospace context issue metadata missing top issues.");
    }
    if (!Array.isArray(snapshotMetadata?.aerospaceContextReport?.topCaveats)) {
      throw new Error("Satellite aerospace context report metadata missing top caveats.");
    }
    if (!Array.isArray(snapshotMetadata?.aerospaceReviewQueue?.topItems)) {
      throw new Error("Satellite aerospace review queue metadata missing top items.");
    }
    if (!Array.isArray(snapshotMetadata?.aerospaceSourceReadiness?.families)) {
      throw new Error("Satellite aerospace source readiness metadata missing families.");
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
      [
        "Candidate only",
        "interactive-map-html",
        "Likely camera count 299",
        "Compliance risk medium",
        "Endpoint verification needs-review",
        "Candidate endpoint https://weathercams.faa.gov/"
      ],
      "faa candidate card"
    );

    const minnesotaCard = page.getByTestId("webcam-source-card-minnesota-511-public-arcgis");
    const minnesotaText = await minnesotaCard.textContent();
    assertIncludes(
      minnesotaText ?? "",
      [
        "Candidate only",
        "Endpoint verification needs-review",
        "Candidate endpoint https://511mn.org/",
        "Do not scrape the interactive web app."
      ],
      "minnesota candidate card"
    );

    const finlandCard = page.getByTestId("webcam-source-card-finland-digitraffic-road-cameras");
    const finlandText = await finlandCard.textContent();
    assertIncludes(
      finlandText ?? "",
      [
        "Candidate only",
        "official-dot-api via json-api",
        "Endpoint verification machine-readable-confirmed",
        "Machine-readable endpoint https://tie.digitraffic.fi/api/weathercam/v1/stations",
        "Sandbox connector available",
        "Mode fixture",
        "Connector FinlandDigitrafficWeatherCamConnector",
        "Latest sandbox result needs-review",
        "Sandbox discovered 2",
        "Sandbox usable 1",
        "Sandbox review queue 2",
        "Sandbox import is not validation or activation. Source remains candidate-only."
      ],
      "finland sandbox candidate card"
    );

    const reviewPanelText = await page.getByTestId("webcam-review-queue-panel").textContent();
    assertIncludes(
      reviewPanelText ?? "",
      ["Webcam Review Queue", "Viewer-only", "Facility hint"],
      "webcam review queue"
    );

    const inspectorText = await page.locator(".panel--right").textContent();
    assertIncludes(
      inspectorText ?? "",
      ["Akutan North", "Source ID", "usgs-ashcam", "Direct-image", "Connector hint", "Facility hint", "Reviewed link: volcano:akutan", "Validated"],
      "direct-image webcam inspector"
    );

    const coverageSummaryText = await page.getByTestId("webcam-visible-summary").textContent();
    assertIncludes(
      coverageSummaryText ?? "",
      ["Visible Webcam Subset", "clusters", "direct-image", "viewer-only", "sources represented"],
      "webcam coverage summary"
    );

    const lifecycleSummaryText = await page.getByTestId("webcam-source-lifecycle-summary").textContent();
    assertIncludes(
      lifecycleSummaryText ?? "",
      [
        "Source Lifecycle Summary",
        "5 total sources",
        "1 validated",
        "3 candidate-only",
        "2 endpoint-verified",
        "1 sandbox-importable",
        "1 credential-blocked",
        "2 blocked / do-not-scrape",
        "3 needs review",
        "Validated active: usgs-ashcam",
        "Candidate sandbox-importable: finland-digitraffic-road-cameras",
        "Blocked / do not scrape: minnesota-511-public-arcgis",
        "Credential blocked: wsdot-cameras"
      ],
      "webcam source lifecycle summary"
    );

    await page.waitForFunction(
      () => window.__worldviewDebug.getState().webcamClusters.length > 0,
      null,
      { timeout: 30_000 }
    );
    await page.evaluate(() => {
      const clusters = window.__worldviewDebug.getState().webcamClusters;
      const firstCluster = clusters[0];
      if (firstCluster) {
        window.__worldviewDebug.setSelectedWebcamClusterId(
          `camera-cluster:${firstCluster.clusterId.replace("cluster:", "")}`
        );
      }
    });
    const clusterDetailText = await page.getByTestId("webcam-cluster-detail").textContent();
    assertIncludes(
      clusterDetailText ?? "",
      ["Selected Cluster", "Akutan Volcano", "direct-image", "viewer-only", "needs review"],
      "webcam cluster detail"
    );
    const clusterReferenceText = await page.getByTestId("webcam-cluster-reference-context").textContent();
    assertIncludes(
      clusterReferenceText ?? "",
      ["Reference Context", "Reviewed links available", "Machine suggestions", "Hint-only", "Reference caveat"],
      "webcam cluster reference context"
    );

    const clusterCameraRows = page.getByTestId("webcam-cluster-camera-row");
    await clusterCameraRows.first().waitFor({ timeout: 30_000 });
    await page.evaluate(() => {
      const firstCluster = window.__worldviewDebug.getState().webcamClusters[0];
      const firstCameraId = firstCluster?.cameras?.[0]?.id;
      if (firstCameraId) {
        window.__worldviewDebug.setSelectedEntityId(firstCameraId);
      }
    });
    await page.waitForFunction(
      () => {
        const selectedId = window.__worldviewDebug.getState().selectedEntity?.id ?? "";
        return selectedId.startsWith("camera:usgs-ashcam:akutan-");
      },
      null,
      { timeout: 30_000 }
    );
    const clusterSelectedInspectorText = await page.locator(".panel--right").textContent();
    assertIncludes(
      clusterSelectedInspectorText ?? "",
      ["Akutan", "Direct-image", "Source Readiness", "Validated", "Reviewed link"],
      "cluster camera selection inspector"
    );

    await page.evaluate(() =>
      window.__worldviewDebug.setSelectedEntityId("camera:usgs-ashcam:akutan-ridge")
    );
    await page.waitForFunction(
      () => window.__worldviewDebug.getState().selectedEntity?.id === "camera:usgs-ashcam:akutan-ridge",
      null,
      { timeout: 30_000 }
    );
    const machineInspectorText = await page.locator(".panel--right").textContent();
    assertIncludes(
      machineInspectorText ?? "",
      ["Akutan Ridge", "Machine suggestion: suggested (2 candidates)", "Connector hint", "Facility hint"],
      "machine-suggestion webcam inspector"
    );

    await page.getByRole("button", { name: "Export Snapshot" }).click();
    const webcamSnapshotMetadata = await page.evaluate(() => window.__worldviewLastSnapshotMetadata?.webcamCoverageSummary ?? null);
    if (!webcamSnapshotMetadata?.referenceSummary) {
      throw new Error("Webcam snapshot metadata did not include reference summary.");
    }
    if ((webcamSnapshotMetadata.referenceSummary.reviewedLinkCount ?? 0) < 1) {
      throw new Error("Webcam snapshot metadata did not preserve reviewed-link counts.");
    }
    if (!Array.isArray(webcamSnapshotMetadata.referenceSummary.topReferenceHints) || webcamSnapshotMetadata.referenceSummary.topReferenceHints.length < 1) {
      throw new Error("Webcam snapshot metadata did not preserve top reference hints.");
    }
    const webcamLifecycleMetadata = await page.evaluate(
      () => window.__worldviewLastSnapshotMetadata?.webcamSourceLifecycleSummary ?? null
    );
    if (!webcamLifecycleMetadata) {
      throw new Error("Webcam snapshot metadata did not include source lifecycle summary.");
    }
    if (webcamLifecycleMetadata.validatedCount !== 1 || webcamLifecycleMetadata.candidateCount !== 3) {
      throw new Error(`Unexpected webcam lifecycle counts: ${JSON.stringify(webcamLifecycleMetadata)}`);
    }
    if (webcamLifecycleMetadata.endpointVerifiedCount !== 2 || webcamLifecycleMetadata.sandboxImportableCount !== 1) {
      throw new Error(`Unexpected webcam lifecycle endpoint/sandbox counts: ${JSON.stringify(webcamLifecycleMetadata)}`);
    }
    const sandboxRow = webcamLifecycleMetadata.rows.find((row) => row.bucket === "candidate-sandbox-importable");
    if (!sandboxRow?.sourceKeys?.includes("finland-digitraffic-road-cameras")) {
      throw new Error("Webcam lifecycle metadata did not preserve Finland sandbox candidate state.");
    }
    const blockedRow = webcamLifecycleMetadata.rows.find((row) => row.bucket === "blocked-do-not-scrape");
    if (!blockedRow?.sourceKeys?.includes("minnesota-511-public-arcgis")) {
      throw new Error("Webcam lifecycle metadata did not preserve Minnesota blocked/do-not-scrape state.");
    }
    const validatedRow = webcamLifecycleMetadata.rows.find((row) => row.bucket === "validated-active");
    if (!validatedRow?.sourceKeys?.includes("usgs-ashcam")) {
      throw new Error("Webcam lifecycle metadata did not preserve Ashcam validated state.");
    }
    if (!Array.isArray(webcamLifecycleMetadata.exportLines) || webcamLifecycleMetadata.exportLines.length < 2) {
      throw new Error("Webcam lifecycle metadata did not preserve compact export lines.");
    }

    await page.getByTestId("webcam-filter-direct-image").check();
    await page.waitForFunction(
      () => window.__worldviewDebug.getState().cameraEntities.length === 2,
      null,
      { timeout: 30_000 }
    );
    const directFilterSummaryText = await page.getByTestId("webcam-visible-summary").textContent();
    assertIncludes(
      directFilterSummaryText ?? "",
      ["2 cameras", "1 clusters"],
      "direct-image coverage summary"
    );

    await page.getByTestId("webcam-filter-direct-image").uncheck();
    await page.getByTestId("webcam-filter-viewer-only").check();
    await page.waitForFunction(
      () => window.__worldviewDebug.getState().cameraEntities.length === 2,
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
      ["Spurr Overlook", "Viewer fallback only.", "Viewer-only", "needs-review", "No reference hint, machine suggestion, or reviewed link is available for this camera."],
      "viewer-only webcam inspector"
    );
    const viewerFilterSummaryText = await page.getByTestId("webcam-visible-summary").textContent();
    assertIncludes(
      viewerFilterSummaryText ?? "",
      ["2 cameras", "0 clusters"],
      "viewer-only coverage summary"
    );

    return {
      selected: "camera:usgs-ashcam:spurr-overlook",
      sourceCard: sourceText,
      candidateCard: candidateText,
      minnesotaCard: minnesotaText,
      finlandCard: finlandText,
      clusterDetail: clusterDetailText
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
    await page.waitForSelector('[data-testid="marine-context-sources"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-context-timeline"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-context-issues"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-environmental-context"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-noaa-context"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-ndbc-context"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-scottish-water-context"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-environmental-anchor"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-environmental-radius"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-environmental-preset"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-environmental-source-coops"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-environmental-source-ndbc"]', { timeout: 30_000 });

    const sectionText = await page.locator('[data-testid="marine-anomaly-section"]').textContent();
    assertIncludes(
      sectionText ?? "",
      ["Marine Attention Priority", "Attention priority is a review signal", "Marine Context Sources", "Marine Environmental Context", "NOAA CO-OPS", "NOAA NDBC"],
      "marine anomaly section"
    );
    const contextSourcesText = await page.locator('[data-testid="marine-context-sources"]').textContent();
    assertIncludes(
      contextSourcesText ?? "",
      [
        "NOAA CO-OPS",
        "NOAA NDBC",
        "Scottish Water Overflows",
        "France Vigicrues Hydrometry",
        "Ireland OPW Water Level",
        "degraded",
        "unavailable"
      ],
      "marine context source summary"
    );
    const contextTimelineText = await page.locator('[data-testid="marine-context-timeline"]').textContent();
    assertIncludes(
      contextTimelineText ?? "",
      ["Marine Context Timeline", "snapshot"],
      "marine context timeline"
    );
    const contextIssuesText = await page.locator('[data-testid="marine-context-issues"]').textContent();
    assertIncludes(
      contextIssuesText ?? "",
      ["Marine Context Issues", "fixture/local mode", "degraded", "unavailable"],
      "marine context issues"
    );
    const environmentalText = await page.locator('[data-testid="marine-environmental-context"]').textContent();
    assertIncludes(
      environmentalText ?? "",
      ["Marine environmental context", "nearby station"],
      "marine environmental context"
    );
    const presetSummaryText = await page.locator('[data-testid="marine-environmental-preset-summary"]').textContent();
    assertIncludes(
      presetSummaryText ?? "",
      ["Preset", "Chokepoint review"],
      "marine environmental preset summary"
    );
    const environmentalCaveatText = await page.locator('[data-testid="marine-environmental-context-caveat"]').textContent();
    assertIncludes(
      environmentalCaveatText ?? "",
      ["Environmental context", "proof of vessel intent"],
      "marine environmental context caveat"
    );
    const noaaText = await page.locator('[data-testid="marine-noaa-context"]').textContent();
    assertIncludes(noaaText ?? "", ["NOAA CO-OPS", "fixture/local"], "marine NOAA CO-OPS context");
    const ndbcText = await page.locator('[data-testid="marine-ndbc-context"]').textContent();
    assertIncludes(ndbcText ?? "", ["NOAA NDBC", "fixture/local"], "marine NOAA NDBC context");
    const scottishWaterText = await page.locator('[data-testid="marine-scottish-water-context"]').textContent();
    assertIncludes(
      scottishWaterText ?? "",
      ["Scottish Water Overflows", "fixture/local", "degraded", "active"],
      "marine Scottish Water overflow context"
    );
    const vigicruesText = await page.locator('[data-testid="marine-vigicrues-context"]').textContent();
    assertIncludes(
      vigicruesText ?? "",
      ["France Vigicrues Hydrometry", "fixture/local", "unavailable"],
      "marine Vigicrues hydrometry context"
    );
    const irelandOpwText = await page.locator('[data-testid="marine-ireland-opw-context"]').textContent();
    assertIncludes(
      irelandOpwText ?? "",
      ["Ireland OPW Water Level", "fixture/local"],
      "marine Ireland OPW water-level context"
    );
    const hydrologyText = await page.locator('[data-testid="marine-hydrology-context"]').textContent();
    assertIncludes(
      hydrologyText ?? "",
      ["Marine Hydrology Context", "Vigicrues", "Ireland OPW"],
      "marine hydrology context"
    );
    const fusionText = await page.locator('[data-testid="marine-context-fusion"]').textContent();
    assertIncludes(
      fusionText ?? "",
      ["Marine Context Fusion", "Ocean/met context", "Hydrology context", "Infrastructure context", "Export readiness"],
      "marine context fusion"
    );
    const reviewReportText = await page.locator('[data-testid="marine-context-review-report"]').textContent();
    assertIncludes(
      reviewReportText ?? "",
      ["Marine Context Review Report", "Context families", "Review next:", "Does not prove:"],
      "marine context review report"
    );
    await page.locator('[data-testid="marine-environmental-source-ndbc"] input').uncheck();
    await page.waitForTimeout(300);
    const ndbcCardCountAfterDisable = await page.locator('[data-testid="marine-ndbc-context"]').count();
    if (ndbcCardCountAfterDisable !== 0) {
      throw new Error("Marine NDBC context card remained visible after disabling NDBC source.");
    }
    const environmentalAfterDisable = await page.locator('[data-testid="marine-environmental-context"]').textContent();
    assertIncludes(
      environmentalAfterDisable ?? "",
      ["Sources coops"],
      "marine environmental context after source toggle"
    );
    await page.locator('[data-testid="marine-environmental-source-ndbc"] input').check();
    await page.waitForSelector('[data-testid="marine-ndbc-context"]', { timeout: 30_000 });
    await page.locator('[data-testid="marine-environmental-preset"] select').selectOption("buoy-weather-focus");
    await page.waitForTimeout(300);
    const timelineAfterPreset = await page.locator('[data-testid="marine-context-timeline"]').textContent();
    assertIncludes(
      timelineAfterPreset ?? "",
      ["Buoy/weather focus"],
      "marine context timeline after preset change"
    );
    const coopsCardCountAfterPreset = await page.locator('[data-testid="marine-noaa-context"]').count();
    if (coopsCardCountAfterPreset !== 0) {
      throw new Error("Marine NOAA CO-OPS context card remained visible after selecting buoy-weather-focus preset.");
    }
    const presetAfterSwitch = await page.locator('[data-testid="marine-environmental-preset-summary"]').textContent();
    assertIncludes(
      presetAfterSwitch ?? "",
      ["Buoy/weather focus"],
      "marine environmental preset switch"
    );
    await page.locator('[data-testid="marine-environmental-preset"] select').selectOption("chokepoint-review");
    await page.waitForSelector('[data-testid="marine-noaa-context"]', { timeout: 30_000 });
    await page.waitForSelector('[data-testid="marine-ndbc-context"]', { timeout: 30_000 });

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
    const queueItemCount = await page.locator('[data-testid="marine-attention-queue-item"]').count();
    if (queueItemCount > 0) {
      await page.locator('[data-testid="marine-attention-queue-item"]').first().click();
      const focusedTargetCount = await page.locator('[data-testid="marine-focused-target"]').count();
      if (focusedTargetCount < 1) {
        const vesselFocusCount = await page.locator('[data-testid="marine-focus-vessel-event"]').count();
        if (vesselFocusCount > 0) {
          await page.locator('[data-testid="marine-focus-vessel-event"]').first().click();
        } else {
          await page.locator('[data-testid="marine-focus-viewport-window"]').first().click();
        }
      }
      await page.waitForSelector('[data-testid="marine-focused-target"]', { timeout: 30_000 });
      const focusedText = await page.locator('[data-testid="marine-focused-target"]').textContent();
      assertIncludes(focusedText ?? "", ["Focused replay target"], "marine focused target");
      const focusedEvidencePanelCount = await page.locator('[data-testid="marine-focused-evidence"]').count();
      if (focusedEvidencePanelCount < 1) {
        throw new Error("Marine focused replay evidence panel was not rendered.");
      }
      const focusedEvidenceText = await page.locator('[data-testid="marine-focused-evidence"]').first().textContent();
      assertIncludes(focusedEvidenceText ?? "", ["Focused Replay Evidence"], "marine focused evidence panel");
      const focusedRows = await page.locator('[data-testid="marine-evidence-row"]').count();
      if (focusedRows < 1) {
        throw new Error("Marine focused replay evidence did not render any rows after focus action.");
      }
      const interpretationText = await page.locator('[data-testid="marine-focused-evidence"]').textContent();
      assertIncludes(
        interpretationText ?? "",
        ["Evidence Interpretation", "Why this was prioritized", "Trust/caveat"],
        "marine evidence interpretation panel"
      );
      const focusedEnvironmentalCaveat = await page.locator('[data-testid="marine-focused-environmental-caveat"]').textContent();
      assertIncludes(
        focusedEnvironmentalCaveat ?? "",
        ["Environmental context"],
        "marine focused environmental caveat"
      );
      const modeSelector = page.locator('[data-testid="marine-evidence-interpretation-mode"] select');
      await modeSelector.selectOption("compact");
      await page.waitForTimeout(150);
      const compactCount = await page.locator('[data-testid="marine-interpretation-card"]').count();
      await modeSelector.selectOption("detailed");
      await page.waitForTimeout(150);
      const detailedCount = await page.locator('[data-testid="marine-interpretation-card"]').count();
      if (detailedCount < compactCount) {
        throw new Error(`Marine interpretation mode did not expand card visibility: compact=${compactCount} detailed=${detailedCount}`);
      }
      await modeSelector.selectOption("caveats-first");
      await page.waitForTimeout(150);
      const caveatsFirstText = await page.locator('[data-testid="marine-interpretation-card"]').first().textContent();
      if (!(caveatsFirstText ?? "").toLowerCase().includes("trust") &&
          !(caveatsFirstText ?? "").toLowerCase().includes("source health") &&
          !(caveatsFirstText ?? "").toLowerCase().includes("evidence limits")) {
        throw new Error(`Marine caveats-first mode did not reprioritize caveat cards: ${caveatsFirstText}`);
      }
    }

    const sliceFocusCount = await page.locator('[data-testid="marine-focus-slice"]').count();
    if (sliceFocusCount > 0) {
      const targetIndex = sliceFocusCount > 1 ? 1 : 0;
      await page.locator('[data-testid="marine-focus-slice"]').nth(targetIndex).click();
    } else {
      await page.locator('[data-testid="marine-focus-viewport-window"]').click();
    }
    await page.waitForSelector('[data-testid="marine-focused-target"]', { timeout: 30_000 });
    await page.locator('[data-testid="marine-chokepoint-filter"] select').selectOption("high");
    await page.waitForTimeout(250);
    if (sliceFocusCount > 1) {
      const focusedKindText = await page.locator('[data-testid="marine-focused-target"]').textContent();
      if ((focusedKindText ?? "").includes("chokepoint-slice")) {
        const staleCount = await page.locator('[data-testid="marine-focused-target-stale"]').count();
        if (staleCount > 0) {
          const staleText = await page.locator('[data-testid="marine-focused-target-stale"]').textContent();
          assertIncludes(staleText ?? "", ["Focused target not visible under current filters"], "marine stale focus state");
        }
      }
    }

    await page.getByRole("button", { name: "Export Snapshot" }).click();
    const metadata = await page.evaluate(() => window.__worldviewLastSnapshotMetadata ?? null);
    if (!metadata?.marineAnomalySummary) {
      throw new Error("Marine anomaly snapshot metadata missing after export.");
    }
    const marineCaveats = metadata.marineAnomalySummary.caveats ?? [];
    if (!marineCaveats.some((item) => String(item).toLowerCase().includes("attention prioritization"))) {
      throw new Error("Marine snapshot metadata caveat text missing.");
    }
    if (!metadata.marineAnomalySummary.activeNavigationTarget) {
      throw new Error("Marine snapshot metadata missing active navigation target.");
    }
    const focusedReplayEvidence = metadata.marineAnomalySummary.focusedReplayEvidence ?? null;
    if (!focusedReplayEvidence || Number(focusedReplayEvidence.rowCount ?? 0) < 1) {
      throw new Error("Marine snapshot metadata missing focused replay evidence summary.");
    }
    const focusedEvidenceInterpretation = metadata.marineAnomalySummary.focusedEvidenceInterpretation ?? null;
    if (!focusedEvidenceInterpretation || Number(focusedEvidenceInterpretation.cardCount ?? 0) < 1) {
      throw new Error("Marine snapshot metadata missing focused evidence interpretation summary.");
    }
    if (focusedEvidenceInterpretation.mode !== "caveats-first") {
      throw new Error(`Marine snapshot metadata did not preserve interpretation mode. Received ${focusedEvidenceInterpretation.mode}`);
    }
    if (Number(focusedEvidenceInterpretation.visibleCardCount ?? 0) < 1) {
      throw new Error("Marine snapshot metadata missing visible interpretation card count.");
    }
    const noaaCoopsContext = metadata.marineAnomalySummary.noaaCoopsContext ?? null;
    if (!noaaCoopsContext) {
      throw new Error("Marine snapshot metadata missing NOAA CO-OPS context summary.");
    }
    if (noaaCoopsContext.sourceMode !== "fixture") {
      throw new Error(`Marine NOAA CO-OPS context expected fixture mode. Received ${noaaCoopsContext.sourceMode}`);
    }
    const ndbcContext = metadata.marineAnomalySummary.ndbcContext ?? null;
    if (!ndbcContext) {
      throw new Error("Marine snapshot metadata missing NOAA NDBC context summary.");
    }
    if (ndbcContext.sourceMode !== "fixture") {
      throw new Error(`Marine NOAA NDBC context expected fixture mode. Received ${ndbcContext.sourceMode}`);
    }
    const scottishWaterContext = metadata.marineAnomalySummary.scottishWaterOverflowContext ?? null;
    if (!scottishWaterContext) {
      throw new Error("Marine snapshot metadata missing Scottish Water overflow context summary.");
    }
    if (scottishWaterContext.sourceMode !== "fixture") {
      throw new Error(`Marine Scottish Water context expected fixture mode. Received ${scottishWaterContext.sourceMode}`);
    }
    if (Number(scottishWaterContext.activeMonitorCount ?? 0) < 1) {
      throw new Error("Marine Scottish Water context expected at least one active monitor in fixture metadata.");
    }
    const contextSourceSummary = metadata.marineAnomalySummary.contextSourceSummary ?? null;
    if (!contextSourceSummary) {
      throw new Error("Marine snapshot metadata missing context source summary.");
    }
    if (Number(contextSourceSummary.sourceCount ?? 0) < 5) {
      throw new Error(`Marine context source summary expected at least 5 rows. Received ${contextSourceSummary.sourceCount}`);
    }
    if (!Array.isArray(contextSourceSummary.rows) || contextSourceSummary.rows.length < 5) {
      throw new Error("Marine context source summary rows missing from snapshot metadata.");
    }
    const contextSourceLabels = contextSourceSummary.rows.map((row) => row.label);
    for (const expectedLabel of ["NOAA CO-OPS", "NOAA NDBC", "Scottish Water Overflows", "France Vigicrues Hydrometry", "Ireland OPW Water Level"]) {
      if (!contextSourceLabels.includes(expectedLabel)) {
        throw new Error(`Marine context source summary metadata missing row label: ${expectedLabel}`);
      }
    }
    const scottishWaterRow = contextSourceSummary.rows.find((row) => row.label === "Scottish Water Overflows");
    if (!scottishWaterRow || scottishWaterRow.health !== "degraded") {
      throw new Error(`Marine context source summary expected Scottish Water degraded state. Received ${JSON.stringify(scottishWaterRow)}`);
    }
    const vigicruesRow = contextSourceSummary.rows.find((row) => row.label === "France Vigicrues Hydrometry");
    if (!vigicruesRow || vigicruesRow.health !== "unavailable") {
      throw new Error(`Marine context source summary expected Vigicrues unavailable state. Received ${JSON.stringify(vigicruesRow)}`);
    }
    if (Number(contextSourceSummary.degradedSourceCount ?? 0) < 1) {
      throw new Error("Marine context source summary expected at least one degraded source.");
    }
    const vigicruesContext = metadata.marineAnomalySummary.vigicruesHydrometryContext ?? null;
    if (!vigicruesContext) {
      throw new Error("Marine snapshot metadata missing Vigicrues hydrometry context summary.");
    }
    if (vigicruesContext.sourceMode !== "fixture") {
      throw new Error(`Marine Vigicrues context expected fixture mode. Received ${vigicruesContext.sourceMode}`);
    }
    if (vigicruesContext.health !== "unavailable") {
      throw new Error(`Marine Vigicrues context expected unavailable state. Received ${vigicruesContext.health}`);
    }
    const irelandOpwContext = metadata.marineAnomalySummary.irelandOpwWaterLevelContext ?? null;
    if (!irelandOpwContext) {
      throw new Error("Marine snapshot metadata missing Ireland OPW water-level context summary.");
    }
    if (irelandOpwContext.sourceMode !== "fixture") {
      throw new Error(`Marine Ireland OPW context expected fixture mode. Received ${irelandOpwContext.sourceMode}`);
    }
    const hydrologyContext = metadata.marineAnomalySummary.hydrologyContext ?? null;
    if (!hydrologyContext) {
      throw new Error("Marine snapshot metadata missing hydrology context summary.");
    }
    if (Number(hydrologyContext.sourceCount ?? 0) < 2) {
      throw new Error(`Marine hydrology context expected 2 sources. Received ${hydrologyContext.sourceCount}`);
    }
    if (Number(hydrologyContext.fixtureSourceCount ?? 0) < 2) {
      throw new Error(`Marine hydrology context expected fixture/local source count >= 2. Received ${hydrologyContext.fixtureSourceCount}`);
    }
    if (!Array.isArray(hydrologyContext.caveats) || hydrologyContext.caveats.length < 1) {
      throw new Error("Marine hydrology context metadata missing caveats.");
    }
    if (!["loaded", "empty", "stale", "degraded", "disabled", "unavailable", "error", "unknown"].includes(hydrologyContext.vigicrues?.health ?? "")) {
      throw new Error("Marine hydrology context metadata missing recognized Vigicrues health state.");
    }
    const contextFusionSummary = metadata.marineAnomalySummary.contextFusionSummary ?? null;
    if (!contextFusionSummary) {
      throw new Error("Marine snapshot metadata missing context fusion summary.");
    }
    if (Number(contextFusionSummary.familyCount ?? 0) < 3) {
      throw new Error(`Marine context fusion summary expected 3 families. Received ${contextFusionSummary.familyCount}`);
    }
    if (!Array.isArray(contextFusionSummary.familyLines) || contextFusionSummary.familyLines.length < 3) {
      throw new Error("Marine context fusion summary missing family lines.");
    }
    const fusionFamilyLabels = contextFusionSummary.familyLines.map((line) => line.label);
    for (const expectedLabel of ["Ocean/met context", "Hydrology context", "Infrastructure context"]) {
      if (!fusionFamilyLabels.includes(expectedLabel)) {
        throw new Error(`Marine context fusion summary missing family label: ${expectedLabel}`);
      }
    }
    if (!["ready-with-caveats", "limited-context", "unavailable"].includes(contextFusionSummary.exportReadiness)) {
      throw new Error(`Marine context fusion summary export readiness was not recognized: ${contextFusionSummary.exportReadiness}`);
    }
    if (!Array.isArray(contextFusionSummary.highestPriorityCaveats) || contextFusionSummary.highestPriorityCaveats.length < 1) {
      throw new Error("Marine context fusion summary missing priority caveats.");
    }
    const contextReviewReport = metadata.marineAnomalySummary.contextReviewReport ?? null;
    if (!contextReviewReport) {
      throw new Error("Marine snapshot metadata missing context review report.");
    }
    if (!Array.isArray(contextReviewReport.contextFamiliesIncluded) || contextReviewReport.contextFamiliesIncluded.length < 3) {
      throw new Error("Marine context review report missing included context families.");
    }
    if (!Array.isArray(contextReviewReport.reviewNeededItems) || contextReviewReport.reviewNeededItems.length < 1) {
      throw new Error("Marine context review report missing review-needed items.");
    }
    if (!Array.isArray(contextReviewReport.doesNotProveLines) || contextReviewReport.doesNotProveLines.length < 1) {
      throw new Error("Marine context review report missing does-not-prove lines.");
    }
    if (!["ready-with-caveats", "limited-context", "unavailable"].includes(contextReviewReport.exportReadiness)) {
      throw new Error(`Marine context review report export readiness was not recognized: ${contextReviewReport.exportReadiness}`);
    }
    const contextTimeline = metadata.marineAnomalySummary.contextTimeline ?? null;
    if (!contextTimeline) {
      throw new Error("Marine snapshot metadata missing context timeline summary.");
    }
    if (Number(contextTimeline.snapshotCount ?? 0) < 2) {
      throw new Error(`Marine context timeline expected at least 2 snapshots after preset changes. Received ${contextTimeline.snapshotCount}`);
    }
    if (!contextTimeline.currentSnapshot) {
      throw new Error("Marine context timeline missing current snapshot.");
    }
    if (!("previousSnapshot" in contextTimeline)) {
      throw new Error("Marine context timeline metadata missing previousSnapshot field.");
    }
    await page.locator('[data-testid="marine-context-timeline-clear"]').click();
    await page.waitForTimeout(150);
    const timelineAfterClear = await page.locator('[data-testid="marine-context-timeline"]').textContent();
    assertIncludes(
      timelineAfterClear ?? "",
      ["0 snapshots", "No marine context snapshots recorded yet."],
      "marine context timeline clear action"
    );
    const environmentalContext = metadata.marineAnomalySummary.environmentalContext ?? null;
    if (!environmentalContext) {
      throw new Error("Marine snapshot metadata missing combined environmental context summary.");
    }
    if (Number(environmentalContext.sourceCount ?? 0) < 2) {
      throw new Error(`Marine environmental context expected 2 sources. Received ${environmentalContext.sourceCount}`);
    }
    if (!Array.isArray(environmentalContext.enabledSources) || environmentalContext.enabledSources.length < 1) {
      throw new Error("Marine environmental context metadata missing enabledSources.");
    }
    if (environmentalContext.presetId !== "chokepoint-review") {
      throw new Error(`Marine environmental context expected chokepoint-review preset. Received ${environmentalContext.presetId}`);
    }
    if (!environmentalContext.presetLabel) {
      throw new Error("Marine environmental context metadata missing presetLabel.");
    }
    if (environmentalContext.isCustomPreset !== false) {
      throw new Error("Marine environmental context expected predefined preset state in exported metadata.");
    }
    if (environmentalContext.radiusKm !== 400) {
      throw new Error(`Marine environmental context expected default radius 400 km. Received ${environmentalContext.radiusKm}`);
    }
    if (!environmentalContext.effectiveAnchor) {
      throw new Error("Marine environmental context metadata missing effectiveAnchor.");
    }
    const interpretationEnvironmentalAvailability =
      focusedEvidenceInterpretation.environmentalContextAvailability ?? null;
    if (!interpretationEnvironmentalAvailability) {
      throw new Error("Marine snapshot metadata missing environmental interpretation availability.");
    }
    const interpretationEnvironmentalCaveats =
      focusedEvidenceInterpretation.environmentalCaveats ?? [];
    if (
      !interpretationEnvironmentalCaveats.some(
        (item) =>
          String(item).toLowerCase().includes("environmental context") &&
          String(item).toLowerCase().includes("proof of vessel intent")
      )
    ) {
      throw new Error("Marine snapshot metadata missing environmental caveat summary.");
    }
    const contextIssueQueue = metadata.marineAnomalySummary.contextIssueQueue ?? null;
    if (!contextIssueQueue) {
      throw new Error("Marine snapshot metadata missing context issue queue.");
    }
    if (Number(contextIssueQueue.issueCount ?? 0) < 1) {
      throw new Error("Marine context issue queue expected at least one issue in fixture mode.");
    }
    if (Number(contextIssueQueue.warningCount ?? 0) < 1) {
      throw new Error("Marine context issue queue expected at least one warning for degraded or unavailable source health.");
    }
    if (Number(contextIssueQueue.infoCount ?? 0) < 1) {
      throw new Error("Marine context issue queue expected at least one informational fixture-mode issue.");
    }
    if (!Array.isArray(contextIssueQueue.topIssues) || contextIssueQueue.topIssues.length < 1) {
      throw new Error("Marine context issue queue topIssues missing from snapshot metadata.");
    }
    if (!contextIssueQueue.topIssues.some((issue) => issue.issueType === "fixture-mode")) {
      throw new Error("Marine context issue queue expected a fixture-mode issue in snapshot metadata.");
    }
    if (!contextIssueQueue.topIssues.some((issue) => issue.issueType === "degraded" || issue.issueType === "unavailable")) {
      throw new Error("Marine context issue queue expected degraded or unavailable source-health coverage in snapshot metadata.");
    }

    return {
      initialRanks,
      highCount,
      exportedMarineMetadata: true
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
    await page.getByTestId("environmental-events-overview").waitFor({ timeout: 30_000 });

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
    const overviewText = await page.getByTestId("environmental-events-overview").textContent();
    assertIncludes(
      overviewText ?? "",
      ["Environmental Events Overview", "Earthquakes", "Source health", "fixture", "View relevance", "Event context", "Selected earthquakes"],
      "environmental overview after earthquake selection"
    );
    const nearestOtherText = await page.getByTestId("environmental-overview-nearest-other").textContent();
    assertIncludes(
      nearestOtherText ?? "",
      ["Nearest other loaded environmental event", "No relationship implied"],
      "environmental nearest other summary"
    );
    const crossSourceText = await page.getByTestId("environmental-overview-cross-source").textContent();
    assertIncludes(
      crossSourceText ?? "",
      ["No relationship implied"],
      "environmental cross-source context"
    );
    await page.getByRole("button", { name: "Pin Event" }).click();
    const pinnedOverviewText = await page.getByTestId("environmental-events-overview").textContent();
    assertIncludes(
      pinnedOverviewText ?? "",
      ["Pinned environmental events", "Comparison only; no relationship implied"],
      "environmental pinned event overview"
    );

    await page.getByRole("button", { name: "Export Snapshot" }).click();
    const snapshotMetadata = await page.evaluate(() => window.__worldviewLastSnapshotMetadata ?? null);
    if (!snapshotMetadata?.earthquakeLayerSummary) {
      throw new Error("Earthquake snapshot metadata did not include earthquake layer summary.");
    }
      if (!snapshotMetadata?.environmentalOverview) {
        throw new Error("Earthquake snapshot metadata did not include environmental overview.");
      }
      if ((snapshotMetadata.environmentalOverview.pinnedComparison?.pinnedCount ?? 0) < 1) {
        throw new Error("Earthquake snapshot metadata did not preserve pinned environmental events.");
      }
    if (!Array.isArray(snapshotMetadata.environmentalOverview.exportLines) || snapshotMetadata.environmentalOverview.exportLines.length === 0) {
      throw new Error("Earthquake snapshot metadata did not preserve environmental relevance export lines.");
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

async function runEonetPhase(browser) {
  const { context, page, consoleMessages, pageErrors } = await createPhasePage(browser);
  try {
    await page.goto(baseUrl, { waitUntil: "networkidle" });
    await waitForDebugReady(page);
    await installCaptureHooks(page);

    const row = page.locator(".panel--left .toggle-row", { hasText: "Natural Events (EONET)" }).first();
    await row.waitFor({ timeout: 30_000 });
    await row.locator('input[type="checkbox"]').check();

    await page.waitForFunction(
      () => (window.__worldviewDebug.getState().eonetEntities?.length ?? 0) > 0,
      null,
      { timeout: 30_000 }
    );

    await page.getByText("EONET Category").waitFor({ timeout: 30_000 });
    await page.getByText("EONET Status").waitFor({ timeout: 30_000 });
    await page.getByText("EONET Limit").waitFor({ timeout: 30_000 });
    await page.getByTestId("environmental-events-overview").waitFor({ timeout: 30_000 });

    const firstItem = page.locator('[data-testid^="eonet-item-"]').first();
    await firstItem.waitFor({ timeout: 30_000 });
    await firstItem.click();

    await page.waitForFunction(
      () => window.__worldviewDebug.getState().selectedEntity?.type === "environmental-event",
      null,
      { timeout: 30_000 }
    );
    const inspectorText = await page.getByTestId("eonet-inspector").textContent();
    assertIncludes(
      inspectorText ?? "",
      ["Environmental Event (NASA EONET)", "Categories", "Event Date", "Source", "Caveat"],
      "eonet inspector"
    );
    const overviewText = await page.getByTestId("environmental-events-overview").textContent();
    assertIncludes(
      overviewText ?? "",
      ["Environmental Events Overview", "EONET", "Source health", "fixture", "View relevance", "Event context", "Selected eonet"],
      "environmental overview after eonet selection"
    );
    await page.getByRole("button", { name: "Pin Event" }).click();
    await page.getByRole("button", { name: "Export Snapshot" }).click();
    const metadata = await page.evaluate(() => window.__worldviewLastSnapshotMetadata ?? null);
    if (!metadata?.eonetLayerSummary) {
      throw new Error("EONET snapshot metadata missing.");
    }
      if (!metadata?.environmentalOverview) {
        throw new Error("EONET snapshot metadata missing environmental overview.");
      }
      if ((metadata.environmentalOverview.pinnedComparison?.pinnedCount ?? 0) < 1) {
        throw new Error("EONET snapshot metadata missing pinned environmental event summary.");
      }
    if (!Array.isArray(metadata.environmentalOverview.exportLines) || metadata.environmentalOverview.exportLines.length === 0) {
      throw new Error("EONET snapshot metadata missing environmental relevance export lines.");
    }
    return {
      loadedCount: await page.evaluate(() => window.__worldviewDebug.getState().eonetEntities?.length ?? 0)
    };
  } catch (error) {
    return {
      errors: [String(error)],
      diagnostics: await collectDiagnostics(page, "eonet", consoleMessages, pageErrors)
    };
  } finally {
    await context.close();
  }
}

async function launchBrowser() {
  return chromium.launch({ headless: true });
}

async function runCanvasProbeSafely(runner) {
  const browser = await launchBrowser();
  try {
    return await runner(browser);
  } catch (error) {
    return {
      errors: [String(error)]
    };
  } finally {
    await browser.close();
  }
}

const browser = await launchBrowser();

try {
  if (phase === "marine") {
    const marine = await runMarinePhase(browser);
    console.log(JSON.stringify({ marine }, null, 2));
  } else if (phase === "earthquake") {
    const earthquake = await runEarthquakePhase(browser);
    console.log(JSON.stringify({ earthquake }, null, 2));
  } else if (phase === "eonet") {
    const eonet = await runEonetPhase(browser);
    console.log(JSON.stringify({ eonet }, null, 2));
  } else if (phase === "aerospace") {
    const aircraft = await runAircraftPhase(browser);
    const satellite = await runSatellitePhase(browser);
    const restore = await runRestorePhase(browser);
    await browser.close();

    const canvasAircraft = await runCanvasProbeSafely(runCanvasAircraftPhase);
    const canvasSatellite = await runCanvasProbeSafely(runCanvasSatellitePhase);
    console.log(JSON.stringify({ canvasAircraft, canvasSatellite, aircraft, satellite, restore }, null, 2));
  } else if (phase === "webcam") {
    const webcam = await runWebcamPhase(browser);
    console.log(JSON.stringify({ webcam }, null, 2));
  } else {
    const aircraft = await runAircraftPhase(browser);
    const satellite = await runSatellitePhase(browser);
    const restore = await runRestorePhase(browser);
    const webcam = await runWebcamPhase(browser);
    const earthquake = await runEarthquakePhase(browser);
    const eonet = await runEonetPhase(browser);
    await browser.close();

    const canvasAircraft = await runCanvasProbeSafely(runCanvasAircraftPhase);
    const canvasSatellite = await runCanvasProbeSafely(runCanvasSatellitePhase);
    console.log(JSON.stringify({ canvasAircraft, canvasSatellite, aircraft, satellite, restore, webcam, earthquake, eonet }, null, 2));
  }
} finally {
  if (browser.isConnected()) {
    await browser.close();
  }
}
