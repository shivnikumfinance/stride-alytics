import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity, ActivityIndicator } from "react-native";
import client from "../api/client";

export default function GreeksScreen() {
  const [spot, setSpot] = useState("100");
  const [strike, setStrike] = useState("100");
  const [vol, setVol] = useState("0.3");
  const [dte, setDte] = useState("30");
  const [type, setType] = useState("call");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const calculate = async () => {
    setLoading(true);
    try {
      const response = await client.post("/greeks/calculate", {
        spot: parseFloat(spot),
        strike: parseFloat(strike),
        time_to_expiry: (parseInt(dte) || 30) / 365,
        volatility: parseFloat(vol) || 0.3,
        risk_free_rate: 0.05,
        option_type: type,
      });
      setResult(response.data);
    } catch (err) {} finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.inputGroup}>
        <TextInput style={styles.input} placeholder="Spot" value={spot} onChangeText={setSpot} keyboardType="decimal-pad" />
        <TextInput style={styles.input} placeholder="Strike" value={strike} onChangeText={setStrike} keyboardType="decimal-pad" />
      </View>
      <View style={styles.inputGroup}>
        <TextInput style={styles.input} placeholder="IV (e.g. 0.30)" value={vol} onChangeText={setVol} keyboardType="decimal-pad" />
        <TextInput style={styles.input} placeholder="DTE" value={dte} onChangeText={setDte} keyboardType="number-pad" />
      </View>

      <View style={styles.typeRow}>
        <TouchableOpacity style={[styles.typeBtn, type === "call" && styles.typeBtnActive]} onPress={() => setType("call")}>
          <Text style={[styles.typeBtnText, type === "call" && styles.typeBtnTextActive]}>Call</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.typeBtn, type === "put" && styles.typeBtnActive]} onPress={() => setType("put")}>
          <Text style={[styles.typeBtnText, type === "put" && styles.typeBtnTextActive]}>Put</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.button} onPress={calculate} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Calculate</Text>}
      </TouchableOpacity>

      {result && (
        <View style={styles.resultCard}>
          <Text style={styles.resultTitle}>Greeks for {type.toUpperCase()}</Text>
          <View style={styles.row}><Text style={styles.label}>Delta</Text><Text style={styles.value}>{result.delta.toFixed(4)}</Text></View>
          <View style={styles.row}><Text style={styles.label}>Gamma</Text><Text style={styles.value}>{result.gamma.toFixed(6)}</Text></View>
          <View style={styles.row}><Text style={styles.label}>Theta</Text><Text style={styles.value}>{result.theta.toFixed(4)}</Text></View>
          <View style={styles.row}><Text style={styles.label}>Vega</Text><Text style={styles.value}>{result.vega.toFixed(4)}</Text></View>
          <View style={styles.row}><Text style={styles.label}>Rho</Text><Text style={styles.value}>{result.rho.toFixed(4)}</Text></View>
          <View style={styles.divider} />
          <View style={styles.row}><Text style={styles.label}>Call Price</Text><Text style={styles.value}>${result.price_call.toFixed(2)}</Text></View>
          <View style={styles.row}><Text style={styles.label}>Put Price</Text><Text style={styles.value}>${result.price_put.toFixed(2)}</Text></View>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f3f4f6" },
  content: { padding: 16 },
  inputGroup: { flexDirection: "row", marginBottom: 12 },
  input: { flex: 1, backgroundColor: "#fff", borderRadius: 10, padding: 14, fontSize: 16, marginHorizontal: 4, borderWidth: 1, borderColor: "#e5e7eb", color: "#1f2937" },
  typeRow: { flexDirection: "row", marginBottom: 16 },
  typeBtn: { flex: 1, padding: 12, borderRadius: 10, backgroundColor: "#fff", alignItems: "center", marginHorizontal: 4, borderWidth: 2, borderColor: "#e5e7eb" },
  typeBtnActive: { borderColor: "#4f46e5", backgroundColor: "#eef2ff" },
  typeBtnText: { fontSize: 16, fontWeight: "600", color: "#6b7280" },
  typeBtnTextActive: { color: "#4f46e5" },
  button: { backgroundColor: "#4f46e5", borderRadius: 10, padding: 14, alignItems: "center", marginBottom: 16 },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  resultCard: { backgroundColor: "#fff", borderRadius: 12, padding: 16, shadowColor: "#000", shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 2 },
  resultTitle: { fontSize: 18, fontWeight: "700", color: "#1f2937", marginBottom: 12, textAlign: "center" },
  row: { flexDirection: "row", justifyContent: "space-between", paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: "#f3f4f6" },
  label: { fontSize: 15, color: "#6b7280" },
  value: { fontSize: 15, fontWeight: "600", color: "#1f2937" },
  divider: { height: 1, backgroundColor: "#e5e7eb", marginVertical: 8 },
});