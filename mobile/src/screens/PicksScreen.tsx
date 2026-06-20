import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, RefreshControl, TouchableOpacity } from "react-native";
import client from "../api/client";

const samplePicks = [
  { symbol: "AAPL", strike: 200, expiry: "2026-07-17", side: "call", rationale: "Bullish momentum + low IV", confidence: 0.65 },
  { symbol: "MSFT", strike: 410, expiry: "2026-07-17", side: "put", rationale: "Mean reversion near ATH", confidence: 0.55 },
  { symbol: "SPY", strike: 555, expiry: "2026-06-20", side: "call", rationale: "Weekly trend continuation", confidence: 0.70 },
];

export default function PicksScreen() {
  const [picks, setPicks] = useState(samplePicks);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchPicks = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    try {
      const response = await client.get("/weekly-picks");
      if (response.data?.results?.length) {
        setPicks(response.data.results);
      }
    } catch {} finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { fetchPicks(); }, []);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => fetchPicks(true)} tintColor="#4f46e5" />}
    >
      <Text style={styles.description}>Auto-generated ideas refreshed every Sunday at 6 PM ET.</Text>

      {picks.map((pick, i) => (
        <View key={i} style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.symbol}>{pick.symbol}</Text>
            <View style={[styles.sideBadge, { backgroundColor: pick.side === "call" ? "#dcfce7" : "#fee2e2" }]}>
              <Text style={[styles.sideText, { color: pick.side === "call" ? "#16a34a" : "#dc2626" }]}>
                {pick.side.toUpperCase()}
              </Text>
            </View>
          </View>
          <Text style={styles.strike}>${pick.strike} @ {pick.expiry}</Text>
          <Text style={styles.rationale}>{pick.rationale}</Text>
          <View style={styles.confidenceBar}>
            <View style={[styles.confidenceFill, { width: `${(pick.confidence * 100).toFixed(0)}%` }]} />
          </View>
          <Text style={styles.confidenceText}>Confidence: {(pick.confidence * 100).toFixed(0)}%</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f3f4f6" },
  content: { padding: 16 },
  description: { fontSize: 14, color: "#6b7280", marginBottom: 16, textAlign: "center" },
  card: { backgroundColor: "#fff", borderRadius: 12, padding: 16, marginBottom: 12, shadowColor: "#000", shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 2 },
  cardHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 8 },
  symbol: { fontSize: 20, fontWeight: "800", color: "#1f2937" },
  sideBadge: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12 },
  sideText: { fontSize: 13, fontWeight: "700" },
  strike: { fontSize: 16, color: "#4b5563", marginBottom: 8 },
  rationale: { fontSize: 14, color: "#6b7280", marginBottom: 12, lineHeight: 20 },
  confidenceBar: { height: 6, backgroundColor: "#e5e7eb", borderRadius: 3, marginBottom: 4 },
  confidenceFill: { height: "100%", backgroundColor: "#4f46e5", borderRadius: 3 },
  confidenceText: { fontSize: 12, color: "#9ca3af", textAlign: "right" },
});