import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity, ActivityIndicator, FlatList } from "react-native";
import client from "../api/client";

export default function ScreenerScreen() {
  const [symbol, setSymbol] = useState("SPY");
  const [results, setResults] = useState([]);
  const [spot, setSpot] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expiryMax, setExpiryMax] = useState("60");

  const runScreener = async () => {
    setLoading(true);
    try {
      const response = await client.post("/screener/run", {
        symbol: symbol.toUpperCase(),
        expiry_days_min: 0,
        expiry_days_max: parseInt(expiryMax) || 60,
        min_volume: 0,
        min_open_interest: 0,
        limit: 20,
      });
      setResults(response.data.results || []);
      setSpot(response.data.spot);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.filterRow}>
        <TextInput style={[styles.input, { flex: 1, marginRight: 8 }]} placeholder="Symbol" placeholderTextColor="#9ca3af" value={symbol} onChangeText={setSymbol} autoCapitalize="characters" />
        <TextInput style={[styles.input, { width: 80 }]} placeholder="Days" placeholderTextColor="#9ca3af" value={expiryMax} onChangeText={setExpiryMax} keyboardType="numeric" />
      </View>
      <TouchableOpacity style={styles.button} onPress={runScreener} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Run Screener</Text>}
      </TouchableOpacity>

      {spot && <Text style={styles.spotText}>Spot: ${spot.toFixed(2)}</Text>}

      {results.length > 0 && (
        <View>
          <Text style={styles.sectionTitle}>Results ({results.length})</Text>
          {results.map((row, i) => (
            <View key={i} style={styles.resultRow}>
              <View style={styles.resultHeader}>
                <Text style={styles.symbol}>{row.symbol}</Text>
                <Text style={[styles.optionType, { color: row.option_type === "call" ? "#16a34a" : "#dc2626" }]}>
                  {row.option_type.toUpperCase()}
                </Text>
              </View>
              <Text style={styles.detail}>Strike: ${row.strike} | Exp: {row.expiry}</Text>
              <Text style={styles.detail}>IV: {(row.implied_vol * 100).toFixed(1)}% | Δ: {row.delta.toFixed(3)} | Θ: {row.theta.toFixed(3)}</Text>
              <Text style={styles.detail}>Vol: {row.volume.toLocaleString()} | OI: {row.open_interest.toLocaleString()}</Text>
            </View>
          ))}
        </View>
      )}

      {!loading && results.length === 0 && (
        <Text style={styles.emptyText}>Enter a symbol and tap "Run Screener"</Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f3f4f6" },
  content: { padding: 16 },
  filterRow: { flexDirection: "row", marginBottom: 12 },
  input: { backgroundColor: "#fff", borderRadius: 10, padding: 14, fontSize: 16, borderWidth: 1, borderColor: "#e5e7eb", color: "#1f2937" },
  button: { backgroundColor: "#4f46e5", borderRadius: 10, padding: 14, alignItems: "center", marginBottom: 16 },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  spotText: { fontSize: 16, fontWeight: "700", color: "#1f2937", marginBottom: 12, textAlign: "center" },
  sectionTitle: { fontSize: 18, fontWeight: "700", color: "#1f2937", marginBottom: 12 },
  resultRow: { backgroundColor: "#fff", borderRadius: 10, padding: 14, marginBottom: 10, shadowColor: "#000", shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 3, elevation: 1 },
  resultHeader: { flexDirection: "row", justifyContent: "space-between", marginBottom: 4 },
  symbol: { fontSize: 16, fontWeight: "700", color: "#1f2937" },
  optionType: { fontSize: 14, fontWeight: "700" },
  detail: { fontSize: 13, color: "#6b7280", marginTop: 2 },
  emptyText: { textAlign: "center", color: "#9ca3af", fontSize: 16, marginTop: 40 },
});