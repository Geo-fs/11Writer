export function toApiDateTime(value: string): string | null {
  if (!value) {
    return null;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }

  return parsed.toISOString();
}

export function normalizeStatusFilter(value: string | undefined): "all" | "airborne" | "on-ground" {
  if (value === "airborne" || value === "on-ground") {
    return value;
  }
  return "all";
}
