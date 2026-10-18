import { Hotspot } from "../types";

export const MOCK_HOTSPOTS: Hotspot[] = [
  { id: "1", title: "Lift out of service", kind: "broken_lift", latitude: 51.5308, longitude: -0.1238, description: "King's Cross St Pancras: lift to Northern line platforms often out." },
  { id: "2", title: "Steep kerb", kind: "steep_kerb", latitude: 51.5246, longitude: -0.134, description: "No dropped kerb at crossing near UCL main entrance." },
  { id: "3", title: "Roadworks", kind: "construction", latitude: 51.5282, longitude: -0.1337, description: "Pavement narrowed to under 1m outside Euston." },
  { id: "4", title: "Bins blocking path", kind: "blocked_pavement", latitude: 51.523, longitude: -0.1244, description: "Bins regularly left on the pavement by Russell Square." },
  { id: "5", title: "Accessible toilet", kind: "accessible_toilet", latitude: 51.5165, longitude: -0.131, description: "Radar key toilet near Tottenham Court Road." },
  { id: "6", title: "Quiet room", kind: "quiet_space", latitude: 51.5115, longitude: -0.116, description: "Quiet study space near King's College Strand." },
  { id: "7", title: "Step-free ramp", kind: "ramp_entrance", latitude: 51.5031, longitude: -0.1132, description: "Ramped entrance at Waterloo main concourse." },
];
