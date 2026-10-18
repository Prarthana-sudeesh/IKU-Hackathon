import { LatLng, Preferences, Hotspot } from "../types";

const BASE = "https://api.openrouteservice.org";
const KEY = process.env.EXPO_PUBLIC_ORS_KEY!;

// ORS uses [lng, lat]; map libraries usually use { latitude, longitude }.
export const toORS = (p: LatLng): [number, number] => [p.longitude, p.latitude];
export const fromORS = ([lng, lat]: number[]): LatLng => ({ latitude: lat, longitude: lng });

// Small square (~metres) around each hazard, as a GeoJSON MultiPolygon.
export function hazardsToAvoidPolygons(hazards: Hotspot[], metres = 25) {
  const dLat = metres / 111_320;
  return {
    type: "MultiPolygon" as const,
    coordinates: hazards.map((h) => {
      const dLng = metres / (111_320 * Math.cos((h.latitude * Math.PI) / 180));
      const { latitude: la, longitude: lo } = h;
      return [[
        [lo - dLng, la - dLat],
        [lo + dLng, la - dLat],
        [lo + dLng, la + dLat],
        [lo - dLng, la + dLat],
        [lo - dLng, la - dLat],
      ]];
    }),
  };
}

export type RouteResult = {
  coords: LatLng[];
  distanceM: number;
  durationS: number;
};

export async function getAccessibleRoute(
  start: LatLng,
  end: LatLng,
  prefs: Preferences,
  avoidPolygons?: object
): Promise<RouteResult> {
  const res = await fetch(`${BASE}/v2/directions/wheelchair/geojson`, {
    method: "POST",
    headers: { Authorization: KEY, "Content-Type": "application/json" },
    body: JSON.stringify({
      coordinates: [toORS(start), toORS(end)],
      instructions: true,
      options: {
        profile_params: {
          restrictions: {
            maximum_incline: prefs.maxIncline,
            maximum_sloped_kerb: prefs.maxKerb,
            minimum_width: prefs.minWidth,
            surface_type: "cobblestone:flattened",
            smoothness_type: "good",
          },
        },
        ...(avoidPolygons && { avoid_polygons: avoidPolygons }),
      },
    }),
  });
  if (!res.ok) throw new Error(`ORS error ${res.status}: ${await res.text()}`);
  const data = await res.json();
  const feature = data.features[0];
  return {
    coords: feature.geometry.coordinates.map(fromORS),
    distanceM: feature.properties.summary.distance,
    durationS: feature.properties.summary.duration,
  };
}

// Biased to London. Returns up to 5 matches.
export async function geocode(query: string): Promise<{ label: string; coord: LatLng }[]> {
  const url =
    `${BASE}/geocode/search?api_key=${KEY}&text=${encodeURIComponent(query)}` +
    `&boundary.country=GB&focus.point.lat=51.5074&focus.point.lon=-0.1278&size=5`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Geocode error ${res.status}`);
  const data = await res.json();
  return data.features.map((f: any) => ({
    label: f.properties.label,
    coord: fromORS(f.geometry.coordinates),
  }));
}
