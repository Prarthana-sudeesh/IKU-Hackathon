// The ONLY file that imports a map library. Swap the provider here later.
import { useEffect, useRef } from "react";
import { StyleSheet } from "react-native";
import MapView, { Marker, Polyline } from "react-native-maps";
import { Hotspot, LatLng } from "../types";
import { HOTSPOT_TYPES } from "../constants/hotspotTypes";
import { colors } from "../constants/theme";

type Props = {
  userLocation: LatLng | null;
  routeCoords: LatLng[];
  hotspots: Hotspot[];
  onLongPress?: (coord: LatLng) => void;
};

const LONDON = { latitude: 51.5074, longitude: -0.1278, latitudeDelta: 0.08, longitudeDelta: 0.08 };

export default function AppMap({ userLocation, routeCoords, hotspots, onLongPress }: Props) {
  const ref = useRef<MapView>(null);

  useEffect(() => {
    if (userLocation) {
      ref.current?.animateToRegion({ ...userLocation, latitudeDelta: 0.02, longitudeDelta: 0.02 });
    }
  }, [userLocation]);

  useEffect(() => {
    if (routeCoords.length > 1) {
      ref.current?.fitToCoordinates(routeCoords, {
        edgePadding: { top: 80, right: 60, bottom: 160, left: 60 },
        animated: true,
      });
    }
  }, [routeCoords]);

  return (
    <MapView
      ref={ref}
      style={StyleSheet.absoluteFill}
      initialRegion={LONDON}
      showsUserLocation
      onLongPress={(e) => onLongPress?.(e.nativeEvent.coordinate)}
    >
      {routeCoords.length > 1 && (
        <Polyline coordinates={routeCoords} strokeWidth={6} strokeColor={colors.primary} />
      )}
      {hotspots.map((h) => {
        const t = HOTSPOT_TYPES[h.kind];
        return (
          <Marker
            key={h.id}
            coordinate={{ latitude: h.latitude, longitude: h.longitude }}
            title={`${t.emoji} ${h.title}`}
            description={h.description}
            pinColor={t.isHazard ? "red" : "green"}
          />
        );
      })}
    </MapView>
  );
}
