# StrideAlytics — Frontend Layer

**React + Vite + Tremor web application architecture**

---

## Overview

The **Frontend Layer** is the primary user interface for StrideAlytics, built with modern React patterns and visual design libraries optimized for financial analytics dashboards.

**Key Characteristics:**
- ✅ Modern React 18 with hooks and functional components
- ✅ Server-side rendering ready (optional)
- ✅ Type-safe with TypeScript (optional)
- ✅ Component-driven architecture
- ✅ Responsive design with TailwindCSS
- ✅ Advanced charting with Tremor
- ✅ Client-side state management (Zustand)
- ✅ Data fetching with React Query
- ✅ Fast build tool (Vite)

---

## 1. Technology Stack

| Tool | Purpose | Version |
|------|---------|---------|
| **React** | UI library | 18+ |
| **Vite** | Build tool | 4+ |
| **Tremor** | Dashboard charts | Latest |
| **TailwindCSS** | Styling | 3+ |
| **shadcn/ui** | UI components | Latest |
| **Zustand** | State management | Latest |
| **React Query** | Data fetching & caching | Latest |
| **Axios** | HTTP client | Latest |
| **React Router** | Routing | 6+ |
| **Vitest** | Unit testing | Latest |
| **React Testing Library** | Component testing | Latest |

---

## 2. Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable components
│   ├── pages/            # Full-page components
│   ├── hooks/            # Custom React hooks
│   ├── store/            # Zustand stores
│   ├── api/              # API client & queries
│   ├── utils/            # Utility functions
│   ├── theme/            # Styling & design tokens
│   ├── types/            # TypeScript types
│   ├── App.jsx           # Root component
│   └── main.jsx          # Entry point
├── public/               # Static assets
├── package.json
├── vite.config.js
├── tailwind.config.js
└── tsconfig.json
```

---

## 3. Component Architecture

### 3.1 Component Hierarchy

```
App
├── Layout (Sidebar, Navbar)
│   └── Shell
│       ├── Dashboard Page
│       │   ├── KPI Cards
│       │   ├── Chart Widgets
│       │   └── Summary Tables
│       │
│       ├── Screener Page
│       │   ├── Filters Panel
│       │   └── Results Table
│       │
│       ├── Greeks Page
│       │   ├── Input Form
│       │   └── Results Display
│       │
│       ├── Regime Page
│       │   ├── Regime Chart
│       │   └── Indicators
│       │
│       ├── Weekly Picks Page
│       │   └── Pick Cards
│       │
│       └── Trade Log Page
│           ├── Trade Table
│           └── Trade Stats
│
└── Auth Pages (Login, SignUp, Forgot Password)
```

### 3.2 Component Types

**Presentational (UI) Components:**
- Small, reusable UI elements
- No data fetching
- Props-driven
- Example: `Button`, `Card`, `Modal`, `Badge`

**Container Components:**
- Fetch and manage data
- Connect to stores
- Handle business logic
- Example: `ScreenerContainer`, `GreeksCalculator`

**Page Components:**
- Full-page layouts
- Route handlers
- Example: `Dashboard`, `Screener`, `TradeLog`

---

## 4. State Management with Zustand

### Store Structure

```javascript
// stores/auth.store.js
export const useAuthStore = create((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  
  login: async (email, password) => { ... },
  logout: () => { ... },
  setUser: (user) => set({ user }),
}));

// stores/screener.store.js
export const useScreenerStore = create((set) => ({
  filters: { /* filter state */ },
  results: [],
  loading: false,
  
  setFilters: (filters) => set({ filters }),
  setResults: (results) => set({ results }),
  reset: () => set({ /* initial state */ }),
}));
```

### Store Usage in Components

```javascript
function ScreenerPage() {
  const { filters, results, setFilters } = useScreenerStore();
  
  return (
    <div>
      <ScreenerFilters onFilter={setFilters} />
      <ScreenerResults data={results} />
    </div>
  );
}
```

---

## 5. Data Fetching with React Query

### Query Hooks

```javascript
// api/queries/screener.queries.js
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../client';

export const useScreenerData = (filters) => {
  return useQuery({
    queryKey: ['screener', filters],
    queryFn: () => apiClient.get('/screener', { params: filters }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useGreeksData = (params) => {
  return useQuery({
    queryKey: ['greeks', params],
    queryFn: () => apiClient.get('/greeks', { params }),
  });
};
```

### Mutation Hooks

```javascript
export const useCreateTrade = () => {
  return useMutation({
    mutationFn: (trade) => apiClient.post('/trades', trade),
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['trades'] });
    },
  });
};
```

---

## 6. API Client Setup

### Axios Configuration

```javascript
// api/client.js
import axios from 'axios';
import { useAuthStore } from '../store/auth.store';

export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to requests
apiClient.interceptors.request.use((config) => {
  const { token } = useAuthStore.getState();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);
```

---

## 7. Routing Structure

### React Router Configuration

```javascript
// App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Screener from './pages/Screener';
import Greeks from './pages/Greeks';
import Login from './pages/auth/Login';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/screener" element={<Screener />} />
          <Route path="/greeks" element={<Greeks />} />
          <Route path="/regime" element={<Regime />} />
          <Route path="/picks" element={<WeeklyPicks />} />
          <Route path="/trade-log" element={<TradeLog />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 8. Styling & Theme

### TailwindCSS Configuration

```javascript
// tailwind.config.js
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#8b5cf6',
        success: '#10b981',
        danger: '#ef4444',
      },
    },
  },
  plugins: [],
};
```

### Design Tokens

```javascript
// theme/tokens.js
export const colors = {
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  background: '#ffffff',
  surface: '#f9fafb',
};

export const spacing = {
  xs: '0.25rem',
  sm: '0.5rem',
  md: '1rem',
  lg: '1.5rem',
  xl: '2rem',
};

export const typography = {
  h1: 'font-size: 2rem; font-weight: 700;',
  h2: 'font-size: 1.5rem; font-weight: 600;',
  body: 'font-size: 1rem; font-weight: 400;',
};
```

---

## 9. Key Pages & Features

### Dashboard
- **Purpose:** Main overview with KPIs and widgets
- **Components:** KPI Cards, Charts, Market Summary, Portfolio Widget
- **Data Sources:** Real-time market data, portfolio stats
- **Refresh Rate:** 1-5 minutes

### Screener
- **Purpose:** Filter and find trading opportunities
- **Components:** Filter Panel, Results Table, Detail Modal
- **Features:** Sort, paginate, export, watch list
- **API:** `/api/v1/screener`

### Greeks Calculator
- **Purpose:** Options analysis and Greeks calculation
- **Components:** Input Form, Results Display, Charts
- **Features:** Real-time calculation, IV surface
- **API:** `/api/v1/greeks`

### Regime Analysis
- **Purpose:** Market condition assessment
- **Components:** Regime Chart, Indicators, Signals
- **Data:** Technical indicators, market regime
- **API:** `/api/v1/regime`

### Weekly Picks
- **Purpose:** Trading recommendations
- **Components:** Pick Cards, Detail Analysis, Stats
- **Data:** Algorithm-generated picks, historical performance
- **API:** `/api/v1/picks`

### Trade Log
- **Purpose:** Track trades and P&L
- **Components:** Trade Table, Stats Dashboard, Forms
- **Features:** Add, edit, delete, export trades
- **API:** `/api/v1/trades`

---

## 10. Performance Optimization

### Code Splitting
```javascript
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Screener = lazy(() => import('./pages/Screener'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Dashboard />
    </Suspense>
  );
}
```

### Memoization
```javascript
import { memo } from 'react';

const ScreenerTable = memo(({ data, onSelect }) => {
  return <table>{/* render data */}</table>;
});

export default ScreenerTable;
```

### Image Optimization
- Use modern formats (WebP)
- Lazy load images
- Responsive images with srcset

---

## 11. Testing Strategy

### Unit Tests
```javascript
// components/__tests__/Button.test.jsx
import { render, screen } from '@testing-library/react';
import Button from '../Button';

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click</Button>);
    screen.getByText('Click').click();
    expect(onClick).toHaveBeenCalled();
  });
});
```

### Integration Tests
```javascript
// pages/__tests__/Screener.test.jsx
describe('Screener Page', () => {
  it('displays screener results', async () => {
    render(<Screener />);
    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });
  });
});
```

---

## 12. Environment Variables

```bash
# .env.example
VITE_API_URL=http://localhost:8000
VITE_AUTH_DOMAIN=your-domain.supabase.co
VITE_AUTH_KEY=your-supabase-anon-key
VITE_APP_NAME=StrideAlytics
VITE_LOG_LEVEL=info
```

---

## 13. Build & Deployment

### Development
```bash
npm install
npm run dev          # Start dev server (http://localhost:5173)
npm run lint         # Run ESLint
npm run format       # Format code with Prettier
```

### Production
```bash
npm run build        # Build for production
npm run preview      # Preview production build
npm run test         # Run tests
npm run test:ui      # Run tests with UI
```

### Deployment to Vercel
```bash
vercel deploy        # Deploy to staging
vercel --prod        # Deploy to production
```

---

## 14. Best Practices

✅ **DO:**
- Keep components small and focused
- Use TypeScript for type safety
- Implement error boundaries
- Cache API responses appropriately
- Use React DevTools for debugging
- Write tests for critical paths
- Use semantic HTML
- Optimize images and assets

❌ **DON'T:**
- Fetch data in useEffect without dependencies
- Use `any` type in TypeScript
- Create components in render methods
- Use inline styles (use TailwindCSS)
- Store sensitive data in localStorage
- Forget to validate user input

---

## Next Steps

- **View Diagrams?** → [02-SYSTEM-DIAGRAMS](../02-SYSTEM-DIAGRAMS.md)
- **Check Libraries?** → [LIBRARIES-BY-LAYER](../REFERENCES/LIBRARIES-BY-LAYER.md)
- **Coding Standards?** → [CODING-STANDARDS](../RULES/CODING-STANDARDS.md)
- **See Other Layers?** → [LAYERS/](../)

---

**Version:** A | **Last Updated:** 2026-06-15
