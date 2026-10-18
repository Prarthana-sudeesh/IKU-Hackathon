export type LatLng = { latitude: number; longitude: number };

export type HotspotKind =
  | "broken_lift"
  | "steep_kerb"
  | "construction"
  | "blocked_pavement"
  | "accessible_toilet"
  | "quiet_space"
  | "ramp_entrance";

export type Hotspot = {
  id: string;
  title: string;
  kind: HotspotKind;
  latitude: number;
  longitude: number;
  description: string;
};

export type Preferences = {
  maxIncline: number; // percent, e.g. 6
  maxKerb: number; // metres, e.g. 0.06
  minWidth: number; // metres, e.g. 1.2
};
