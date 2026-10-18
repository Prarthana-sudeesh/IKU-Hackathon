import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import MapScreen from "../screens/MapScreen";
import HotspotsScreen from "../screens/HotspotsScreen";
import ProfileScreen from "../screens/ProfileScreen";
import { colors } from "../constants/theme";

const Tab = createBottomTabNavigator();

export default function RootNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarLabelStyle: { fontSize: 14, fontWeight: "600" },
        tabBarStyle: { height: 64, paddingBottom: 8, paddingTop: 6 },
      }}
    >
      <Tab.Screen name="Map" component={MapScreen}
        options={{ tabBarAccessibilityLabel: "Map and route planner" }} />
      <Tab.Screen name="Hotspots" component={HotspotsScreen}
        options={{ tabBarAccessibilityLabel: "Reported hotspots" }} />
      <Tab.Screen name="Profile" component={ProfileScreen}
        options={{ tabBarAccessibilityLabel: "Accessibility preferences" }} />
    </Tab.Navigator>
  );
}
