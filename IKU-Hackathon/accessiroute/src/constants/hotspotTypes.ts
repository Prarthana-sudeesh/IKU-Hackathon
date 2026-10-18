import { HotspotKind } from "../types";
import { colors } from "./theme";

export const HOTSPOT_TYPES: Record<
  HotspotKind,
  { label: string; emoji: string; isHazard: boolean; color: string }
> = {
  broken_lift: { label: "Broken lift", emoji: "🛗", isHazard: true, color: colors.hazard },
  steep_kerb: { label: "Steep / no dropped kerb", emoji: "⚠️", isHazard: true, color: colors.hazard },
  construction: { label: "Construction", emoji: "🚧", isHazard: true, color: colors.hazard },
  blocked_pavement: { label: "Blocked pavement", emoji: "⛔", isHazard: true, color: colors.hazard },
  accessible_toilet: { label: "Accessible toilet", emoji: "🚻", isHazard: false, color: colors.positive },
  quiet_space: { label: "Quiet space", emoji: "🤫", isHazard: false, color: colors.positive },
  ramp_entrance: { label: "Ramp entrance", emoji: "♿", isHazard: false, color: colors.positive },
};
