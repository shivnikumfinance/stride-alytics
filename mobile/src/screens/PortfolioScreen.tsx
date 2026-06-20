import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, RefreshControl, TouchableOpacity } from "react-native";
import client from "../api/client";

export default function PortfolioScreen() {
  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchPortfolios = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    try {
      const response = await client.get("/portfolio");
      setPortfolios(response.data?.data || []);
    } catch (err) {} finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { fetchPortfolios(); }, []);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4f46e5" />
        <Text style={styles.loadingText}>Loading portfolios...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => fetchPortfolios(true)} tintColor="#4f46e5" />}
    >
      {portfolios.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyIcon}>📁</Text>
          <Text style={styles.emptyTitle}>No Portfolios Yet</Text>
          <Text style={styles.emptyText}>Create a portfolio through the web app to start tracking trades and P&L.</Text>
        </View>
      ) : (
        portfolios.map((p) => (
          <View key={p.id} style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.portfolioName}>{p.name}</Text>
            </View>
            {p.description && <Text style={styles.description}>{p.description}</Text>}
            <Text style={styles.idText}>ID: {p.id.substring(0, 8)}...</Text>
          </View>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f3f4f6" },
  content: { padding: 16, flexGrow: 1 },
  loadingContainer: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#f3f4f6" },
  loadingText: { marginTop: 12, fontSize: 16, color: "#6b7280" },
  emptyState: { flex: 1, justifyContent: "center", alignItems: "center", paddingHorizontal: 32 },
  emptyIcon: { fontSize: 64, marginBottom: 16 },
  emptyTitle: { fontSize: 22, fontWeight: "700", color: "#1f2937", marginBottom: 8 },
  emptyText: { fontSize: 15, color: "#6b7280", textAlign: "center", lineHeight: 22 },
  card: { backgroundColor: "#fff", borderRadius: 12, padding: 16, marginBottom: 12, shadowColor: "#000", shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 2 },
  cardHeader: { marginBottom: 4 },
  portfolioName: { fontSize: 18, fontWeight: "700", color: "#1f2937" },
  description: { fontSize: 14, color: "#6b7280", marginBottom: 8 },
  idText: { fontSize: 12, color: "#9ca3af" },
});