import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
  ScrollView,
} from "react-native";
import * as SecureStore from "expo-secure-store";
import { useNavigation } from "@react-navigation/native";
import client from "../api/client";

export default function LoginScreen() {
  const navigation = useNavigation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSignup, setIsSignup] = useState(false);
  const [fullName, setFullName] = useState("");

  const handleSubmit = async () => {
    if (!email || !password) {
      Alert.alert("Error", "Please fill in all fields");
      return;
    }
    setLoading(true);
    try {
      const endpoint = isSignup ? "/auth/signup" : "/auth/login";
      const payload = isSignup ? { email, password, full_name: fullName || undefined } : { email, password };
      const response = await client.post(endpoint, payload);
      const data = response.data;
      await SecureStore.setItemAsync("stride_token", data.access_token);
      navigation.reset({ index: 0, routes: [{ name: "Home" }] });
    } catch (err) {
      const message = err?.response?.data?.detail || err?.message || "Authentication failed";
      Alert.alert("Error", message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <Text style={styles.logo}>📊</Text>
          <Text style={styles.title}>StrideAlytics</Text>
          <Text style={styles.subtitle}>Options Trading Analytics</Text>
        </View>

        <View style={styles.form}>
          {isSignup && (
            <TextInput
              style={styles.input}
              placeholder="Full name"
              placeholderTextColor="#9ca3af"
              value={fullName}
              onChangeText={setFullName}
              autoCapitalize="words"
            />
          )}
          <TextInput
            style={styles.input}
            placeholder="Email"
            placeholderTextColor="#9ca3af"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
          />
          <TextInput
            style={styles.input}
            placeholder="Password"
            placeholderTextColor="#9ca3af"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />

          <TouchableOpacity style={styles.button} onPress={handleSubmit} disabled={loading}>
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>{isSignup ? "Create Account" : "Sign In"}</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity onPress={() => setIsSignup(!isSignup)} style={styles.switchButton}>
            <Text style={styles.switchText}>
              {isSignup ? "Already have an account? Sign In" : "No account? Create one"}
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f3f4f6" },
  scrollContent: { flexGrow: 1, justifyContent: "center", padding: 24 },
  header: { alignItems: "center", marginBottom: 40 },
  logo: { fontSize: 64, marginBottom: 8 },
  title: { fontSize: 32, fontWeight: "800", color: "#1f2937" },
  subtitle: { fontSize: 16, color: "#6b7280", marginTop: 4 },
  form: { backgroundColor: "#fff", borderRadius: 16, padding: 24, shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8, elevation: 4 },
  input: { backgroundColor: "#f9fafb", borderRadius: 12, padding: 16, fontSize: 16, marginBottom: 12, borderWidth: 1, borderColor: "#e5e7eb", color: "#1f2937" },
  button: { backgroundColor: "#4f46e5", borderRadius: 12, padding: 16, alignItems: "center", marginTop: 8 },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  switchButton: { marginTop: 16, alignItems: "center" },
  switchText: { color: "#4f46e5", fontSize: 14 },
});