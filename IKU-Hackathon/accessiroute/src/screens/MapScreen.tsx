import { useState } from "react";
import { View, Text, Pressable, StyleSheet, Alert, ActivityIndicator } from "react-native";
import AppMap from "../components/AppMap";
import { useUserLocation } from "../hooks/useUserLocation";
import { MOCK_HOTSPOTS } from "../data/mockHotspots";
import { getAccessibleRoute, hazardsToAvoidPolygons, RouteResult } from "../services/ors";
import { HOTSPOT_TYPES } from "../constants/hotspotTypes";
import { colors, fontSizes, MIN_TAP, spacing } from "../constants/theme";
import { Hotspot, HotspotKind, LatLng, Preferences } from "../types";

const DEFAULT_PREFS: Preferences = { maxIncline: 6, maxKerb: 0.06, minWidth: 1.2 };

// Hardcoded demo journey: King's Cross -> UCL
const DEMO_START: LatLng = { latitude: 51.5308, longitude: -0.1238 };
const DEMO_END: LatLng = { latitude: 51.5246, longitude: -0.134 };

export default function MapScreen() {
  const { location } = useUserLocation();
  const [hotspots, setHotspots] = useState<Hotspot[]>(MOCK_HOTSPOTS);
  const [route, setRoute] = useState<RouteResult | null>(null);
  const [loading, setLoading] = useState(false);

  const findRoute = async () => {
    try {
      setLoading(true);
      const hazards = hotspots.filter((h) => HOTSPOT_TYPES[h.kind].isHazard);
      const avoid = hazards.length ? hazardsToAvoidPolygons(hazards) : undefined;
      setRoute(await getAccessibleRoute(DEMO_START, DEMO_END, DEFAULT_PREFS, avoid));
    } catch (e: any) {
      Alert.alert("Could not get route", e.message ?? String(e));
    } finally {
      setLoading(false);
    }
  };

  const addHotspot = (coord: LatLng, kind: HotspotKind) =>
    setHotspots((prev) => [
      ...prev,
      {
        id: String(Date.now()),
        title: HOTSPOT_TYPES[kind].label,
        kind,
        description: "Reported by you",
        ...coord,
      },
    ]);

  const onLongPress = (coord: LatLng) =>
    Alert.alert("Add a hotspot", "What would you like to report?", [
      { text: "Steep / no dropped kerb", onPress: () => addHotspot(coord, "steep_kerb") },
      { text: "Broken lift", onPress: () => addHotspot(coord, "broken_lift") },
      { text: "Ramp entrance", onPress: () => addHotspot(coord, "ramp_entrance") },
      { text: "Cancel", style: "cancel" },
    ]);

  return (
    <View style={styles.container}>
      <AppMap
        userLocation={location}
        routeCoords={route?.coords ?? []}
        hotspots={hotspots}
        onLongPress={onLongPress}
      />
      <View style={styles.panel}>
        {route && (
          <Text style={styles.summary} accessibilityLiveRegion="polite">
            {(route.distanceM / 1000).toFixed(1)} km · {Math.round(route.durationS / 60)} min
          </Text>
        )}
        <Pressable
          style={styles.button}
          onPress={findRoute}
          accessibilityRole="button"
          accessibilityLabel="Find accessible route to university"
        >
          {loading ? (
            <ActivityIndicator color={colors.primaryText} />
          ) : (
            <Text style={styles.buttonText}>Find accessible route (demo)</Text>
          )}
        </Pressable>
        <Text style={styles.hint}>Long-press the map to report a hotspot</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  panel: {
    position: "absolute",
    left: spacing.md,
    right: spacing.md,
    bottom: spacing.lg,
    backgroundColor: colors.background,
    borderColor: colors.border,
    borderWidth: 2,
    borderRadius: 12,
    padding: spacing.md,
    gap: spacing.sm,
  },
  summary: { fontSize: fontSizes.large, fontWeight: "700", color: colors.text },
  button: {
    minHeight: MIN_TAP,
    backgroundColor: colors.primary,
    borderRadius: 8,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: spacing.md,
  },
  buttonText: { color: colors.primaryText, fontSize: fontSizes.body, fontWeight: "700" },
  hint: { fontSize: 14, color: colors.muted, textAlign: "center" },
});
