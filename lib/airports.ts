/** Nearby airports used by the "include nearby airports" option (same metro area, practical to reach). */
const NEARBY: Record<string, string[]> = {
  LHR: ["LHR", "LGW", "STN", "LTN", "LCY"],
  LGW: ["LGW", "LHR", "STN", "LTN", "LCY"],
  DXB: ["DXB", "SHJ", "DWC"],
  SHJ: ["SHJ", "DXB", "DWC"],
  BKK: ["BKK", "DMK"],
  DMK: ["DMK", "BKK"],
  DEL: ["DEL"],
  KUL: ["KUL", "SZB"],
  SIN: ["SIN"],
  DAC: ["DAC"],
  JFK: ["JFK", "EWR", "LGA"],
};

export const withNearby = (code: string, include: boolean): string[] => (include ? NEARBY[code] ?? [code] : [code]);
