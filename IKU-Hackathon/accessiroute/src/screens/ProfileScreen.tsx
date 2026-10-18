import { useState } from "react";
import { View, Text, Pressable, StyleSheet } from "react-native";
import { colors, fontSizes, MIN_TAP, spacing } from "../constants/theme";

// TODO: lift these into a shared store (zustand) so MapScreen uses them.
function Stepper({
  label, value, unit, step, onChange,
}: { label: string; value: number; unit: string; step: number; onChange: (v: number) => void }) {
  const round = (n: number) => Math.round(n * 100) / 100;
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.controls}>
        <Pressable
          style={styles.btn}
          onPress={() => onChange(Math.max(0, round(value - step)))}
          accessibilityRole="button"
          accessibilityLabel={`Decrease ${label}`}
        >
          <Text style={styles.btnText}>−</Text>
        </Pressable>
        <Text style={styles.value} accessibilityLiveRegion="polite">
          {value} {unit}
        </Text>
        <Pressable
          style={styles.btn}
          onPress={() => onChange(round(value + step))}
          accessibilityRole="button"
          accessibilityLabel={`Increase ${label}`}
        >
          <Text style={styles.btnText}>+</Text>
        </Pressable>
      </View>
    </View>
  );
}

export default function ProfileScreen() {
  const [incline, setIncline] = useState(6);
  const [kerb, setKerb] = useState(0.06);
  const [width, setWidth] = useState(1.2);

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Accessibility preferences</Text>
      <Stepper label="Max incline" value={incline} unit="%" step={1} onChange={setIncline} />
      <Stepper label="Max kerb height" value={kerb} unit="m" step={0.01} onChange={setKerb} />
      <Stepper label="Min path width" value={width} unit="m" step={0.1} onChange={setWidth} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: spacing.md, gap: spacing.lg, backgroundColor: colors.background },
  heading: { fontSize: fontSizes.title, fontWeight: "800", color: colors.text },
  row: { gap: spacing.sm },
  label: { fontSize: fontSizes.large, fontWeight: "600", color: colors.text },
  controls: { flexDirection: "row", alignItems: "center", gap: spacing.md },
  btn: {
    width: MIN_TAP, height: MIN_TAP, borderRadius: 8,
    backgroundColor: colors.primary, justifyContent: "center", alignItems: "center",
  },
  btnText: { color: colors.primaryText, fontSize: 28, fontWeight: "700" },
  value: { fontSize: fontSizes.large, minWidth: 100, textAlign: "center", color: colors.text },
});
