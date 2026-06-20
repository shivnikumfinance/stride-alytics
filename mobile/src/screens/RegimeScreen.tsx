import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity, ActivityIndicator } from "react-native";
import client from "../api/client";

export default function RegimeScreen() {
  const [symbol, setSymbol] = useState("SPY");
  const [regime, setRegime] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchRegime = async () => {
    setLoading(true);
    try {
      const response = await client.get(`/regime/${symbol.toUpperCase()}?lookback_days=30`);
      setRegime(response.data);
    } catch (err) {} finally {
      setLoading(false);
    }
  };

  const regimeColor = regime?.regime === "bull" ? "#16a34a" : regime?.regime === "bear" ? "#dc2626" : "#6b7280";

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.searchRow}>
        <TextInput style={styles.input} placeholder="Symbol" value={symbol} onChangeText={setSymbol} autoCapitalize="characters" />
        <TouchableOpacity style={styles.button} onPress={fetchRegime} disabled={loading}>
          {loading ? <ActivityIndicator color="#fff" size="small" /> : <Text style={styles.buttonText}>Go</Text>}
        </TouchableOpacity>
      </View>

      {regime && (
        <View style={styles.card}>
          <View style={[styles.banner, { backgroundColor: regimeColor }]}>
            <Text style={styles.bannerText}>{regime.regime.toUpperCase()}</Text>
          </View>

          <View style={styles.stats}>
            <View style={styles.statRow}>
              <Text style={styles.label}>Symbol</Text>
              <Text style={styles.value}>{regime.symbol}</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.label}>Confidence</Text>
              <Text style={styles.value}>{(regime.confidence * 100).toFixed(0)}%</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.label}>Return</Text>
              <Text style={[styles.value, { color: regime.price_return >= 0 ? "#16a34a" : "#dc2626" }]}>
                {(regime.price_return * 100).toFixed(2)}%
              </Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.label}>Lookback</Text>
              <Text style={styles.value}>{regime.lookback_days} days</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.label}>As of</Text>
              <Text style={styles.value}>{regime.as_of}</Text>
            </View>
            {regime.vix && (
              <View style={styles.statRow}>
                <Text style={styles.label}>VIX</Text>
                <Text style={[styles.value, { color: regime.vix > 25 ? "#dc2626" : "#16a34a" }]}>
                  {regime.vix.toFixed(2)}
                </Text>
              </View>
            )}
          </View>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f3f4f6" },
  content: { padding: 16 },
  searchRow: { flexDirection: "row", marginBottom: 16 },
  input: { flex: 1, backgroundColor: "#fff", borderRadius: 10, padding: 14, fontSize: 16, marginRight: 8, borderWidth: 1, borderColor: "#e5e7eb", color: "#1f2937" },
  button: { backgroundColor: "#4f46e5", borderRadius: 10, paddingHorizontal: 24, justifyContent: "center" },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  card: { backgroundColor: "#fff", borderRadius: 12, overflow: "hidden", shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8, elevation: 4 },
  banner: { padding: 20, alignItems: "center" },
  bannerText: { color: "#fff", fontSize: 28, fontWeight: "800", letterSpacing: 4 },
  stats: { padding: 16 },
  statRow: { flexDirection: "row", justifyContent: "space-between", paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: "#f3f4f6" },
  label: { fontSize: 15, color: "#6b7280" },
  value: { fontSize: 15, fontWeight: "600", color: "#1f2937" },
});