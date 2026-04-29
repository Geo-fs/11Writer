let manualClearRequested = false;

export function markManualSelectionClear() {
  manualClearRequested = true;
}

export function resetManualSelectionClear() {
  manualClearRequested = false;
}

export function consumeManualSelectionClear() {
  if (!manualClearRequested) {
    return false;
  }
  manualClearRequested = false;
  return true;
}
