import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert, ActivityIndicator } from "react-native";
import * as SecureStore from "expo-secure-store";
import { useNavigation } from "@react-navigation/native";
import client from "../api/client";

export default function SettingsScreen() {
  const navigation = useNavigation();
  const [user, setUser] = useState(null);
  const [limits, setLimits] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [meRes, limitsRes] = await Promise.all([
          client.get("/auth/me"),
          client.get("/screener/limits"),
        ]);
        setUser(meRes.data?.data);
        setLimits(limitsRes.data);
      } catch {} finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleLogout = () => {
    Alert.alert("Sign Out", "Are you sure you want to sign out?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Sign Out",
        style: "destructive",
        onPress: async () => {
          await SecureStore.deleteItemAsync("stride_token");
          navigation.reset({ index: 0, routes: [{ name: "Login" }] });
        },
      },
    ]);
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4f46e5" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Account</Text>
        {user ? (
          <View>
            <View style={styles.row}>
              <Text style={styles.label}>User ID</Text>
              <Text style={styles.value}>{user.user_id?.substring(0, 12)}...</Text>
            </View>
            {user.email && (
              <View style={styles.row}>
                <Text style={styles.label}>Email</Text>
                <Text style={styles.value}>{user.email}</Text>
              </View>
            )}
            <View style={styles.row}>
              <Text style={styles.label}>Plan</Text>
              <View style={[styles.planBadge, { backgroundColor: user.subscription_plan === "pro" ? "#dcfce7" : "#eef2ff" }]}>
                <Text style={[styles.planText, { color: user.subscription_plan === "pro" ? "#16a34a" : "#4f46e5" }]}>
                  {user.subscription_plan?.toUpperCase() || "FREE"}
                </Text>
              </View>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Screener Limit</Text>
              <Text style={styles.value}>{limits?.data?.max_results_per_call?.toLocaleString() || "—"}</Text>
            </View>
          </View>
        ) : (
          <Text style={styles.notSignedIn}>Not signed in</Text>
        )}
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Subscription</Text>
        <Text style={styles.cardBody}>Upgrade to Pro for unlimited screener results, hourly regime updates, and trade P&L tracking.</Text>
        <TouchableOpacity style={[styles.button, styles.buttonDisabled]}>
          <Text style={styles.buttonDisabledText}>Upgrade to Pro — Coming Soon</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>About</Text>
        <View style={styles.row}><Text style={styles.label}>Version</Text><Text style={styles.value}>0.1.0</Text></View>
        <View style={styles.row}><Text style={styles.label}>Build</Text><Text style={styles.value}>Expo SDK 51</Text></View>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>Sign Out</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f3f4f6" },
  content: { padding: 16, paddingBottom: 32 },
  loadingContainer: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#f3f4f6" },
  card: { backgroundColor: "#fff", borderRadius: 12, padding: 16, marginBottom: 16, shadowColor: "#000", shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 2 },
  cardTitle: { fontSize: 18, fontWeight: "700", color: "#1f2937", marginBottom: 12 },
  cardBody: { fontSize: 14, color: "#6b7280", lineHeight: 20, marginBottom: 12 },
  row: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: "#f3f4f6" },
  label: { fontSize: 15, color: "#6b7280" },
  value: { fontSize: 15, fontWeight: "600", color: "#1f2937" },
  planBadge: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12 },
  planText: { fontSize: 13, fontWeight: "700" },
  notSignedIn: { fontSize: 15, color: "#9ca3af", fontStyle: "italic" },
  button: { borderRadius: 10, padding: 14, alignItems: "center" },
  buttonDisabled: { backgroundColor: "#f3f4f6" },
  buttonDisabledText: { fontSize: 14, fontWeight: "600", color: "#9ca3af" },
  logoutButton: { backgroundColor: "#fee2e2", borderRadius: 12, padding: 16, alignItems: "center", marginTop: 8 },
  logoutText: { color: "#dc2626", fontSize: 16, fontWeight: "700" },
});