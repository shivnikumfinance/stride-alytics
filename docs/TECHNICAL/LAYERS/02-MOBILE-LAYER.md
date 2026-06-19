# StrideAlytics — Mobile Layer

**React Native + Expo mobile application architecture**

---

## Overview

The **Mobile Layer** provides iOS and Android access to StrideAlytics using React Native and Expo, enabling a native-like experience with cross-platform code sharing.

**Key Characteristics:**
- ✅ Cross-platform (iOS + Android from single codebase)
- ✅ Expo-managed workflow
- ✅ Native performance and feel
- ✅ Offline capabilities
- ✅ Push notifications
- ✅ Biometric authentication
- ✅ Mobile-optimized UI
- ✅ Code sharing with web (types, utils, constants)

---

## 1. Technology Stack

| Tool | Purpose | Notes |
|------|---------|-------|
| **React Native** | Mobile framework | 0.73+ |
| **Expo** | Development platform | SDK 50+ |
| **Expo Router** | File-based routing | Latest |
| **NativeWind** | Tailwind for React Native | Latest |
| **Zustand** | State management | Latest |
| **React Query** | Data fetching | Latest |
| **Axios** | HTTP client | Latest |
| **Expo SecureStore** | Secure storage | Built-in |
| **React Navigation** | Navigation | 6+ |
| **Expo EAS** | CI/CD & building | Latest |

---

## 2. Project Structure

```
mobile/
├── app/                              # Expo Router screens
│   ├── _layout.tsx                   # Root layout
│   ├── index.tsx                     # Home/splash
│   ├── login.tsx                     # Auth screens
│   ├── signup.tsx
│   ├── (tabs)/                       # Tabbed navigation
│   │   ├── _layout.tsx
│   │   ├── dashboard.tsx
│   │   ├── screener.tsx
│   │   ├── greeks.tsx
│   │   ├── regime.tsx
│   │   └── profile.tsx
│   │
│   ├── [stack]/                      # Stack navigation
│   └── _error.tsx
│
├── components/                       # Reusable components
│   ├── ui/                          # UI primitives
│   ├── charts/                      # Chart components
│   ├── layout/                      # Layout components
│   └── tables/                      # Data tables
│
├── hooks/                           # Custom hooks
├── store/                           # Zustand stores
├── api/                             # API client
├── utils/                           # Utilities
├── types/                           # TypeScript types
├── assets/                          # Images, fonts
├── app.json                         # Expo config
├── eas.json                         # EAS config
└── tsconfig.json
```

---

## 3. Routing Structure (Expo Router)

### File-Based Routing

```
app/
├── _layout.tsx                    # Root stack layout
├── index.tsx                      # / route (splash screen)
├── login.tsx                      # /login route
├── signup.tsx                     # /signup route
│
├── (tabs)/                        # Grouped routes (no URL segment)
│   ├── _layout.tsx               # Tabs layout
│   ├── dashboard.tsx             # /dashboard
│   ├── screener.tsx              # /screener
│   ├── greeks.tsx                # /greeks
│   ├── regime.tsx                # /regime
│   └── profile.tsx               # /profile
│
├── screener/
│   ├── _layout.tsx
│   ├── index.tsx                 # /screener (list)
│   └── [id].tsx                  # /screener/[id] (detail)
│
└── _error.tsx                    # Error boundary
```

### Navigation Example

```typescript
// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';

export default function TabsLayout() {
  return (
    <Tabs>
      <Tabs.Screen
        name="dashboard"
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ color }) => <DashboardIcon color={color} />,
        }}
      />
      <Tabs.Screen
        name="screener"
        options={{
          title: 'Screener',
          tabBarIcon: ({ color }) => <ScreenerIcon color={color} />,
        }}
      />
      {/* More tabs */}
    </Tabs>
  );
}
```

---

## 4. UI Component Architecture

### NativeWind for Styling

```typescript
// components/ui/Button.tsx
import { Text, TouchableOpacity } from 'react-native';
import { className } from 'nativewind';

export default function Button({ children, onPress, variant = 'primary' }) {
  return (
    <TouchableOpacity
      onPress={onPress}
      className={`py-3 px-4 rounded-lg ${
        variant === 'primary' ? 'bg-blue-500' : 'bg-gray-500'
      }`}
    >
      <Text className="text-white font-semibold text-center">
        {children}
      </Text>
    </TouchableOpacity>
  );
}
```

### Custom Component Example

```typescript
// components/ScreenerTable.tsx
import { View, ScrollView, Text } from 'react-native';

export default function ScreenerTable({ data }) {
  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false}>
      <View className="p-4">
        {data.map((item) => (
          <View key={item.id} className="flex-row py-2 border-b border-gray-200">
            <Text className="w-20 font-semibold">{item.symbol}</Text>
            <Text className="w-20">${item.price}</Text>
            <Text className={item.change > 0 ? 'text-green-500' : 'text-red-500'}>
              {item.change}%
            </Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}
```

---

## 5. State Management

### Store Setup

```typescript
// store/auth.store.ts
import { create } from 'zustand';
import { supabaseClient } from '../api/supabase';

export const useAuthStore = create((set) => ({
  user: null,
  token: null,
  loading: false,

  login: async (email: string, password: string) => {
    set({ loading: true });
    try {
      const { user, session } = await supabaseClient.auth.signInWithPassword({
        email,
        password,
      });
      set({
        user,
        token: session.access_token,
        loading: false,
      });
      // Store token securely
      await SecureStore.setItemAsync('auth_token', session.access_token);
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },

  logout: async () => {
    await SecureStore.deleteItemAsync('auth_token');
    set({ user: null, token: null });
  },
}));
```

### Using Stores in Screens

```typescript
// app/(tabs)/profile.tsx
import { useAuthStore } from '../../store/auth.store';

export default function ProfileScreen() {
  const { user, logout } = useAuthStore();

  return (
    <View className="flex-1 p-4">
      <Text className="text-2xl font-bold">{user?.email}</Text>
      <Button onPress={logout}>Logout</Button>
    </View>
  );
}
```

---

## 6. API Client & Data Fetching

### Supabase Client Setup

```typescript
// api/supabase.ts
import { createClient } from '@supabase/supabase-js';
import * as SecureStore from 'expo-secure-store';

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;

export const supabaseClient = createClient(supabaseUrl, supabaseKey, {
  auth: {
    storage: SecureStore,
    autoRefreshToken: true,
    persistSession: true,
  },
});
```

### React Query Integration

```typescript
// api/queries/screener.ts
import { useQuery } from '@tanstack/react-query';
import { supabaseClient } from '../supabase';

export const useScreenerData = (filters: any) => {
  return useQuery({
    queryKey: ['screener', filters],
    queryFn: async () => {
      const { data, error } = await supabaseClient
        .from('options')
        .select('*')
        .match(filters);
      
      if (error) throw error;
      return data;
    },
  });
};
```

---

## 7. Screens & Features

### Dashboard Screen
```typescript
// app/(tabs)/dashboard.tsx
import { View, ScrollView } from 'react-native';
import { useDashboardData } from '../../hooks/useDashboardData';

export default function DashboardScreen() {
  const { data, isLoading } = useDashboardData();

  return (
    <ScrollView className="flex-1 bg-white">
      <KPICards data={data?.kpis} />
      <RecentTrades trades={data?.trades} />
      <PortfolioChart portfolio={data?.portfolio} />
    </ScrollView>
  );
}
```

### Screener Screen
```typescript
// app/(tabs)/screener.tsx
import { View, FlatList } from 'react-native';
import { useScreenerData } from '../../hooks/useScreenerData';

export default function ScreenerScreen() {
  const [filters, setFilters] = useState({});
  const { data } = useScreenerData(filters);

  return (
    <View className="flex-1">
      <ScreenerFilters onFilter={setFilters} />
      <FlatList
        data={data}
        renderItem={({ item }) => <ScreenerCard item={item} />}
        keyExtractor={(item) => item.id}
      />
    </View>
  );
}
```

### Greeks Calculator Screen
```typescript
// app/(tabs)/greeks.tsx
import { View, ScrollView } from 'react-native';
import { useState } from 'react';
import { useGreeksCalculation } from '../../hooks/useGreeksCalculation';

export default function GreeksScreen() {
  const [inputs, setInputs] = useState({});
  const { mutate, data } = useGreeksCalculation();

  const handleCalculate = () => mutate(inputs);

  return (
    <ScrollView className="flex-1 p-4">
      <GreeksForm onSubmit={handleCalculate} onChange={setInputs} />
      {data && <GreeksResults greeks={data} />}
    </ScrollView>
  );
}
```

---

## 8. Native Features

### Secure Storage

```typescript
// utils/secureStorage.ts
import * as SecureStore from 'expo-secure-store';

export const saveToken = async (token: string) => {
  await SecureStore.setItemAsync('auth_token', token);
};

export const getToken = async () => {
  return await SecureStore.getItemAsync('auth_token');
};

export const deleteToken = async () => {
  await SecureStore.deleteItemAsync('auth_token');
};
```

### Push Notifications

```typescript
// api/notifications.ts
import * as Notifications from 'expo-notifications';

export const setupNotifications = async () => {
  const { status } = await Notifications.requestPermissionsAsync();
  
  if (status === 'granted') {
    const token = (await Notifications.getExpoPushTokenAsync()).data;
    console.log('Push token:', token);
    // Send to backend
  }
};

Notifications.setNotificationHandler({
  handleNotification: async (notification) => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});
```

### Biometric Authentication

```typescript
// api/biometric.ts
import * as SecureStore from 'expo-secure-store';
import * as LocalAuthentication from 'expo-local-authentication';

export const biometricAuth = async () => {
  try {
    const available = await LocalAuthentication.hasHardwareAsync();
    if (!available) return false;

    const result = await LocalAuthentication.authenticateAsync({
      disableDeviceFallback: false,
    });

    return result.success;
  } catch (error) {
    console.error(error);
    return false;
  }
};
```

---

## 9. Offline Support

### Offline Data Caching

```typescript
// hooks/useOfflineData.ts
import { useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const useOfflineData = (queryKey: string) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const loadCachedData = async () => {
      const cached = await AsyncStorage.getItem(`cache_${queryKey}`);
      if (cached) {
        setData(JSON.parse(cached));
      }
    };
    loadCachedData();
  }, [queryKey]);

  const cacheData = async (newData: any) => {
    await AsyncStorage.setItem(`cache_${queryKey}`, JSON.stringify(newData));
  };

  return { data, cacheData };
};
```

---

## 10. Performance Optimization

### Image Optimization
```typescript
import { Image } from 'react-native';

<Image
  source={{ uri: 'https://example.com/image.jpg' }}
  style={{ width: 100, height: 100 }}
  resizeMode="contain"
  progressiveRenderingEnabled
/>
```

### Lazy Loading
```typescript
import { useLazyQuery } from '@tanstack/react-query';

const { data, fetchNextPage } = useLazyQuery({
  // ... query config
});

const loadMore = () => fetchNextPage();
```

---

## 11. Testing

### Unit Tests
```typescript
// __tests__/Button.test.tsx
import { render } from '@testing-library/react-native';
import Button from '../components/ui/Button';

describe('Button', () => {
  it('renders button', () => {
    const { getByText } = render(<Button>Press</Button>);
    expect(getByText('Press')).toBeTruthy();
  });
});
```

---

## 12. EAS Build Configuration

### eas.json Setup
```json
{
  "build": {
    "preview": {
      "android": {
        "buildType": "apk"
      },
      "ios": {
        "buildType": "simulator"
      }
    },
    "preview2": {
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "android": {
        "buildType": "aab"
      },
      "ios": {
        "buildType": "archive"
      }
    }
  }
}
```

### Build & Deploy
```bash
eas build --platform ios --profile preview
eas build --platform android --profile production
eas submit -p ios
eas submit -p android
```

---

## 13. Environment Variables

```bash
# app.config.js
export default {
  expo: {
    extra: {
      apiUrl: process.env.EXPO_PUBLIC_API_URL,
      supabaseUrl: process.env.EXPO_PUBLIC_SUPABASE_URL,
      supabaseKey: process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY,
    },
  },
};
```

---

## 14. Best Practices

✅ **DO:**
- Use file-based routing (Expo Router)
- Store auth tokens in SecureStore
- Implement proper error handling
- Use React Query for data sync
- Cache data for offline support
- Optimize images and assets
- Test on real devices

❌ **DON'T:**
- Store sensitive data in AsyncStorage
- Hardcode API URLs
- Ignore platform differences
- Skip error boundaries
- Use network requests on main thread

---

## Next Steps

- **View Diagrams?** → [02-SYSTEM-DIAGRAMS](../02-SYSTEM-DIAGRAMS.md)
- **Check Libraries?** → [LIBRARIES-BY-LAYER](../REFERENCES/LIBRARIES-BY-LAYER.md)
- **Backend Integration?** → [03-BACKEND-LAYER](./03-BACKEND-LAYER.md)

---

**Version:** A | **Last Updated:** 2026-06-15
