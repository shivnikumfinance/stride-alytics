import React, { useEffect, useState } from "react";
import { StatusBar } from "expo-status-bar";
import * as SecureStore from "expo-secure-store";
import Constants from "expo-constants";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { ActivityIndicator, View, Text, StyleSheet } from "react-native";

import { useAuthStore } from "./src/store/auth.store";
import LoginScreen from "./src/screens/LoginScreen";
import DashboardScreen from "./src/screens/DashboardScreen";
import ScreenerScreen from "./src/screens/ScreenerScreen";
import GreeksScreen from "./src/screens/GreeksScreen";
import RegimeScreen from "./src/screens/RegimeScreen";
import PicksScreen from "./src/screens/PicksScreen";
import PortfolioScreen from "./src/screens/PortfolioScreen";
import SettingsScreen from "./src/screens/SettingsScreen";

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const API_URL =
  Constants.expoConfig?.extra?.apiUrl || "http://localhost:8000";

function TabIcon({ label, focused }) {
  const icons = {
    Dashboard: focused ? "📊" : "📈",
    Screener: focused ? "🔍" : "🔎",
    Greeks: focused ? "📐" : "📏",
    Regime: focused ? "🌡️" : "🌤️",
    Picks: focused ? "🎯" : "⭐",
    Portfolio: focused ? "💼" : "📁",
    Settings: focused ? "⚙️" : "🔧",
  };
  return (
    <View style={{ alignItems: "center" }}>
      <Text style={{ fontSize: 20 }}>{icons[label] || "📋"}</Text>
    </View>
  );
}

function HomeTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused }) => <TabIcon label={route.name} focused={focused} />,
        tabBarActiveTintColor: "#4f46e5",
        tabBarInactiveTintColor: "#9ca3af",
        tabBarStyle: {
          backgroundColor: "#ffffff",
          borderTopWidth: 1,
          borderTopColor: "#e5e7eb",
          paddingBottom: 4,
          paddingTop: 4,
          height: 60,
        },
        tabBarLabelStyle: { fontSize: 11, fontWeight: "600" },
        headerStyle: { backgroundColor: "#4f46e5" },
        headerTintColor: "#ffffff",
        headerTitleStyle: { fontWeight: "700" },
      })}
    >
      <Tab.Screen name="Dashboard" component={DashboardScreen} />
      <Tab.Screen name="Screener" component={ScreenerScreen} />
      <Tab.Screen name="Greeks" component={GreeksScreen} />
      <Tab.Screen name="Regime" component={RegimeScreen} />
      <Tab.Screen name="Picks" component={PicksScreen} />
      <Tab.Screen name="Portfolio" component={PortfolioScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

function LoadingScreen() {
  return (
    <View style={styles.loadingContainer}>
      <ActivityIndicator size="large" color="#4f46e5" />
      <Text style={styles.loadingText}>StrideAlytics</Text>
    </View>
  );
}

export default function App() {
  const [ready, setReady] = useState(false);
  const [initialRoute, setInitialRoute] = useState("Login");
  const { hydrate } = useAuthStore();

  useEffect(() => {
    async function init() {
      await hydrate();
      const token = await SecureStore.getItemAsync("stride_token");
      setInitialRoute(token ? "Home" : "Login");
      setReady(true);
    }
    init();
  }, []);

  if (!ready) return <LoadingScreen />;

  return (
    <>
      <StatusBar style="light" />
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName={initialRoute}
          screenOptions={{ headerShown: false }}
        >
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Home" component={HomeTabs} />
        </Stack.Navigator>
      </NavigationContainer>
    </>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#f3f4f6",
  },
  loadingText: {
    marginTop: 16,
    fontSize: 22,
    fontWeight: "700",
    color: "#4f46e5",
  },
});