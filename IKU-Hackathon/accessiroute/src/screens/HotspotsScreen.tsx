import { FlatList, Text, View, StyleSheet } from "react-native";
import { MOCK_HOTSPOTS } from "../data/mockHotspots";
import { HOTSPOT_TYPES } from "../constants/hotspotTypes";
import { colors, fontSizes, spacing } from "../constants/theme";

export default function HotspotsScreen() {
  return (
    <FlatList
      data={MOCK_HOTSPOTS}
      keyExtractor={(h) => h.id}
      contentContainerStyle={{ padding: spacing.md, gap: spacing.md }}
      renderItem={({ item }) => {
        const t = HOTSPOT_TYPES[item.kind];
        return (
          <View
            style={[styles.card, { borderLeftColor: t.color }]}
            accessible
            accessibilityLabel={`${t.label}. ${item.title}. ${item.description}`}
          >
            <Text style={styles.title}>
              {t.emoji} {item.title}
            </Text>
            <Text style={styles.kind}>{t.label}</Text>
            <Text style={styles.desc}>{item.description}</Text>
          </View>
        );
      }}
    />
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.background,
    borderWidth: 2,
    borderColor: colors.border,
    borderLeftWidth: 8,
    borderRadius: 10,
    padding: spacing.md,
    gap: 4,
  },
  title: { fontSize: fontSizes.large, fontWeight: "700", color: colors.text },
  kind: { fontSize: 16, color: colors.muted },
  desc: { fontSize: fontSizes.body, color: colors.text },
});
