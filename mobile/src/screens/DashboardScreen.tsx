import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, RefreshControl, ActivityIndicator } from "react-native";
import client from "../api/client";

function Card({ title, subtitle, children, color = "#4f46e5" }) {
  return (
    <View style={styles.card}>
      <View style={[styles.cardHeader, { borderLeftColor: color, borderLeftWidth: 4 }]}>
        <Text style={styles.cardTitle}>{title}</Text>
        {subtitle && <Text style={styles.cardSubtitle}>{subtitle}</Text>}
      </View>
      <View style={styles.cardBody}>{children}</View>
    </View>
  );
}

export default function DashboardScreen() {
  const [regime, setRegime] = useState(null);
  const [limits, setLimits] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      const [regimeRes, limitsRes] = await Promise.all([
        client.get("/regime/SPY?lookback_days=30"),
        client.get("/screener/limits"),
      ]);
      setRegime(regimeRes.data);
      setLimits(limitsRes.data);
    } catch (err) {} finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4f46e5" />
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => fetchData(true)} tintColor="#4f46e5" />}
    >
      <Card title="Market Regime (SPY)" subtitle="Last 30 trading days" color={regime?.regime === "bull" ? "#16a34a" : regime?.regime === "bear" ? "#dc2626" : "#6b7280"}>
        <View style={styles.row}>
          <Text style={styles.label}>Regime</Text>
          <Text style={[styles.value, { color: regime?.regime === "bull" ? "#16a34a" : regime?.regime === "bear" ? "#dc2626" : "#6b7280" }]}>
            {regime?.regime?.toUpperCase() || "—"}
          </Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Confidence</Text>
          <Text style={styles.value}>{regime ? `${(regime.confidence * 100).toFixed(0)}%` : "—"}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Return</Text>
          <Text style={[styles.value, { color: (regime?.price_return || 0) >= 0 ? "#16a34a" : "#dc2626" }]}>
            {regime ? `${(regime.price_return * 100).toFixed(2)}%` : "—"}
          </Text>
        </View>
      </Card>

      <Card title="Account" subtitle="Current plan & limits">
        <View style={styles.row}>
          <Text style={styles.label}>Plan</Text>
          <Text style={[styles.value, { color: "#4f46e5", textTransform: "capitalize" }]}>
            {limits?.data?.plan || "free"}
          </Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Max results</Text>
          <Text style={styles.value}>{limits?.data?.max_results_per_call?.toLocaleString() || "—"}</Text>
        </View>
      </Card>

      <Card title="Quick Actions" color="#0891b2">
        {[
          { label: "🔍  Run Screener", route: "Screener" },
          { label: "📐  Calculate Greeks", route: "Greeks" },
          { label: "💼  View Portfolio", route: "Portfolio" },
          { label: "🎯  See Weekly Picks", route: "Picks" },
        ].map((item) => (
          <Text key={item.route} style={styles.actionItem}>{item.label}</Text>
        ))}
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f3f4f6" },
  content: { padding: 16, paddingBottom: 32 },
  loadingContainer: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#f3f4f6" },
  loadingText: { marginTop: 12, fontSize: 16, color: "#6b7280" },
  card: { backgroundColor: "#fff", borderRadius: 12, marginBottom: 16, shadowColor: "#000", shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 2 },
  cardHeader: { padding: 16, paddingBottom: 8 },
  cardTitle: { fontSize: 18, fontWeight: "700", color: "#1f2937" },
  cardSubtitle: { fontSize: 13, color: "#9ca3af", marginTop: 2 },
  cardBody: { padding: 16, paddingTop: 8 },
  row: { flexDirection: "row", justifyContent: "space-between", paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: "#f3f4f6" },
  label: { fontSize: 15, color: "#6b7280" },
  value: { fontSize: 15, fontWeight: "600", color: "#1f2937" },
  actionItem: { fontSize: 16, paddingVertical: 10, color: "#1f2937" },
});