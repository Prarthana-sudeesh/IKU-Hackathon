import { useEffect, useState } from "react";
import * as Location from "expo-location";
import { LatLng } from "../types";

export function useUserLocation() {
  const [location, setLocation] = useState<LatLng | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        setError("Location permission denied");
        return;
      }
      const pos = await Location.getCurrentPositionAsync({});
      if (!cancelled) {
        setLocation({ latitude: pos.coords.latitude, longitude: pos.coords.longitude });
      }
    })().catch((e) => setError(String(e)));
    return () => {
      cancelled = true;
    };
  }, []);

  return { location, error };
}
