import React, { useState, useEffect } from "react";
import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View } from "react-native";
import Constants from "expo-constants";

const API_URL =
  Constants.expoConfig?.extra?.apiUrl || "http://localhost:8000";

export default function App() {
  const [connected, setConnected] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/health`)
      .then((res) => res.json())
      .then((data) => setConnected(data.status === "healthy"))
      .catch(() => setConnected(false));
  }, []);

  const statusText =
    connected === null
      ? "Checking…"
      : connected
      ? "Backend Connected: Yes"
      : "Backend Connected: No";

  const statusColor = connected === null ? "#eab308" : connected ? "#16a34a" : "#dc2626";

  return (
    <View style={styles.container}>
      <Text style={styles.title}>StrideAlytics</Text>
      <Text style={styles.subtitle}>Hello from StrideAlytics</Text>
      <View style={[styles.badge, { backgroundColor: statusColor }]}>
        <Text style={styles.badgeText}>{statusText}</Text>
      </View>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f3f4f6",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: "700",
    color: "#1f2937",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: "#6b7280",
    marginBottom: 24,
  },
  badge: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 999,
  },
  badgeText: {
    color: "#fff",
    fontWeight: "600",
    fontSize: 16,
  },
});