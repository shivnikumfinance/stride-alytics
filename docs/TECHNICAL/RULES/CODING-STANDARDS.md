# StrideAlytics — Rules & Standards

**Comprehensive coding standards, conventions, and best practices**

---

## 1. Naming Conventions

### JavaScript/TypeScript

```javascript
// ✅ Component names (PascalCase)
ScreenerTable.jsx
PortfolioCard.jsx
GreeksCalculator.jsx

// ✅ Function & variable names (camelCase)
const calculateGreeks = () => {}
const userPortfolio = {}
let isLoading = false

// ✅ Constants (UPPER_SNAKE_CASE)
const API_BASE_URL = 'https://api.stridealytics.com'
const MAX_RETRIES = 3
const DEFAULT_TIMEOUT = 30000

// ✅ Private variables (underscore prefix)
const _internalHelper = () => {}

// ✅ Boolean variables (is/has/can prefix)
const isActive = true
const hasError = false
const canAccess = true

// ✅ Event handlers (on prefix)
const onButtonClick = () => {}
const onFormSubmit = () => {}
```

### Python

```python
# ✅ Class names (PascalCase)
class ScreenerService:
    pass

class GreeksCalculator:
    pass

# ✅ Function & variable names (snake_case)
def calculate_greeks(spot_price, strike, time_to_expiry):
    pass

user_portfolio = {}
is_loading = False

# ✅ Constants (UPPER_SNAKE_CASE)
API_BASE_URL = 'https://api.stridealytics.com'
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# ✅ Private variables (underscore prefix)
def _internal_helper():
    pass
```

### CSS Classes (TailwindCSS)

```html
<!-- ✅ Descriptive, semantic class names -->
<div class="screener-container">
  <div class="filter-panel">
    <input class="search-input" />
  </div>
  <div class="results-grid">
    <div class="result-card">Result</div>
  </div>
</div>

<!-- ✅ Use Tailwind utility classes -->
<button class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
  Calculate
</button>
```

---

## 2. Folder Structure Rules

### Frontend

```
src/
├── components/           # Grouped by feature
│   ├── screener/
│   │   ├── ScreenerFilters.jsx
│   │   ├── ScreenerResults.jsx
│   │   └── screener.module.css
│   │
│   ├── ui/               # Reusable UI components
│   │   ├── Button.jsx
│   │   ├── Card.jsx
│   │   └── ...
│   │
│   └── layout/
│       ├── Sidebar.jsx
│       └── Navbar.jsx
│
├── pages/                # Page-level components
│   ├── Dashboard.jsx
│   ├── Screener.jsx
│   └── ...
│
├── hooks/                # Custom hooks
│   ├── useAuth.js
│   ├── useScreener.js
│   └── ...
│
├── store/                # Zustand stores
│   ├── auth.store.js
│   ├── screener.store.js
│   └── ...
│
├── api/                  # API-related
│   ├── client.js
│   ├── endpoints.js
│   └── queries/
│       ├── screener.queries.js
│       └── ...
│
├── utils/                # Utilities
│   ├── formatters.js
│   ├── helpers.js
│   └── ...
│
└── types/                # TypeScript types
    └── index.ts
```

### Backend

```
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── screener.py
│   │   │   ├── greeks.py
│   │   │   └── ...
│   │   └── schemas/
│   │       ├── screener.py
│   │       └── ...
│   │
│   └── middleware/
│       ├── auth.py
│       └── error_handler.py
│
├── services/             # Business logic (organized by feature)
│   ├── screener.py
│   ├── greeks.py
│   └── ...
│
├── database/
│   ├── client.py
│   ├── queries/
│   │   ├── screener.py
│   │   └── ...
│   └── migrations/
│       ├── 001_initial.sql
│       └── ...
│
└── utils/
    ├── logger.py
    ├── validators.py
    └── ...
```

---

## 3. File Naming Rules

### Components & Pages

```
✅ GOOD:
- ScreenerTable.jsx
- UserProfilePage.jsx
- ErrorBoundary.jsx
- NotFoundPage.jsx

❌ BAD:
- screenerTable.jsx
- user-profile-page.jsx
- error_boundary.jsx
- 404Page.jsx
```

### Utilities & Services

```
✅ GOOD:
- formatters.js
- dateHelpers.js
- apiClient.js
- authService.py

❌ BAD:
- Formatters.js
- date-helpers.js
- API_client.js
- auth_service.py
```

### Test Files

```
✅ GOOD:
- Button.test.jsx
- screener.spec.js
- test_greeks.py
- conftest.py

❌ BAD:
- ButtonTest.jsx
- screenerTest.js
- greeks_test.py
- test.py
```

---

## 4. Code Organization

### Component Structure (React)

```javascript
// ✅ GOOD
import React, { useState, useEffect } from 'react'
import { Button } from './Button'
import styles from './Screener.module.css'

// Props interface (if TypeScript)
interface ScreenerProps {
  onSelect: (id: string) => void
  loading?: boolean
}

// Component definition
export function Screener({ onSelect, loading }: ScreenerProps) {
  // Hooks first
  const [filters, setFilters] = useState({})
  const { data } = useScreenerData(filters)
  
  // Effects
  useEffect(() => {
    // Side effects
  }, [])
  
  // Handlers
  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
  }
  
  // Render
  return (
    <div className={styles.container}>
      {/* JSX */}
    </div>
  )
}

// Exports
export default Screener
```

### Service Structure (Python)

```python
# ✅ GOOD
from datetime import datetime
from typing import List, Optional
import structlog
from app.database.client import supabase

logger = structlog.get_logger()

class ScreenerService:
    """Service for options screening operations."""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def filter_options(self, filters: dict) -> List[dict]:
        """
        Filter options based on criteria.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List of matching options
            
        Raises:
            ValueError: If filters are invalid
        """
        logger.info("Filtering options", filters=filters)
        
        try:
            results = await self._build_query(filters).execute()
            logger.info("Filter complete", count=len(results.data))
            return results.data
        except Exception as e:
            logger.error("Filter failed", error=str(e))
            raise
    
    async def _build_query(self, filters: dict):
        """Build database query from filters."""
        # Implementation
        pass
```

---

## 5. Import/Export Rules

### Frontend

```javascript
// ✅ GOOD - Organized imports
import React, { useState } from 'react'

// Third-party
import { useQuery } from '@tanstack/react-query'
import classNames from 'classnames'

// Local components
import { Button } from '../ui/Button'
import { ScreenerTable } from './ScreenerTable'

// Utils & hooks
import { formatPrice } from '../../utils/formatters'
import { useScreener } from '../../hooks/useScreener'

// Exports
export { Screener as default }
export type ScreenerProps = { ... }

// ❌ BAD - Mixed order
import { useQuery } from '@tanstack/react-query'
import { Button } from '../ui/Button'
import React from 'react'
import { formatPrice } from '../../utils/formatters'
```

### Backend

```python
# ✅ GOOD - Organized imports
import asyncio
from datetime import datetime
from typing import List, Optional

# Third-party
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog

# Local
from app.database.client import supabase
from app.services.screener import ScreenerService
from app.api.v1.schemas.screener import ScreenerFilter

logger = structlog.get_logger()

# Exports
__all__ = ['router', 'get_screener_results']
```

---

## 6. Comment Guidelines

### Comment Rules

```javascript
// ✅ GOOD - Clear, concise comments
// Fetch screener data with applied filters
const handleFilterSubmit = async (filters) => {
  // Validate filters before API call
  if (!filters.symbol) {
    setError('Symbol is required')
    return
  }
  
  // Query returns paginated results
  const results = await apiClient.get('/screener', { params: filters })
}

// ✅ GOOD - Explain WHY, not WHAT
// Use debounce to avoid excessive API calls during typing
const debouncedSearch = useCallback(
  debounce((term) => search(term), 300),
  []
)

// ❌ BAD - Obvious comments
const name = 'John' // Set name to John
const count = 0 // Initialize count

// ❌ BAD - Outdated comments
// TODO: Fix this bug (from 2 years ago)
// HACK: This is temporary (permanent solution missing)
```

### Documentation Comments

```javascript
/**
 * Calculate option Greeks using Black-Scholes model.
 * 
 * @param {number} spotPrice - Current stock price
 * @param {number} strike - Strike price
 * @param {number} timeToExpiry - Time to expiry in years
 * @returns {Object} Greeks values (delta, gamma, theta, vega)
 * 
 * @example
 * const greeks = calculateGreeks(100, 100, 0.25)
 * console.log(greeks.delta) // 0.5
 */
function calculateGreeks(spotPrice, strike, timeToExpiry) {
  // Implementation
}
```

```python
def calculate_greeks(spot_price: float, strike: float, time_to_expiry: float) -> dict:
    """
    Calculate option Greeks using Black-Scholes model.
    
    Args:
        spot_price: Current stock price
        strike: Strike price
        time_to_expiry: Time to expiry in years
    
    Returns:
        Dictionary containing Greeks (delta, gamma, theta, vega)
    
    Raises:
        ValueError: If parameters are invalid
    
    Example:
        >>> greeks = calculate_greeks(100, 100, 0.25)
        >>> greeks['delta']
        0.5
    """
    # Implementation
    pass
```

---

## 7. Error Handling

### Frontend

```javascript
// ✅ GOOD
try {
  const response = await apiClient.get('/screener')
  setData(response.data)
} catch (error) {
  if (error.response?.status === 401) {
    // Unauthorized - redirect to login
    handleLogout()
  } else if (error.response?.status === 404) {
    setError('Resource not found')
  } else {
    setError('An error occurred. Please try again.')
  }
  logger.error('Failed to fetch screener', { error })
}

// ❌ BAD
try {
  const response = await apiClient.get('/screener')
  setData(response.data)
} catch (error) {
  console.log(error)
  alert('Error')
}
```

### Backend

```python
# ✅ GOOD
from fastapi import HTTPException

@router.get('/screener')
async def get_screener(filters: ScreenerFilter):
    try:
        results = await screener_service.filter_options(filters.dict())
        return {'data': results, 'total': len(results)}
    except ValueError as e:
        logger.error('Invalid filters', error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error('Screener fetch failed', error=str(e))
        raise HTTPException(status_code=500, detail='Internal server error')

# ❌ BAD
@router.get('/screener')
async def get_screener(filters: ScreenerFilter):
    results = screener_service.filter_options(filters)
    return results
```

---

## 8. Validation Rules

### Frontend

```javascript
// ✅ GOOD - Validate before submission
const handleSubmit = async (formData) => {
  // Validate
  if (!formData.email || !formData.email.includes('@')) {
    setError('Invalid email address')
    return
  }
  
  if (formData.password.length < 8) {
    setError('Password must be at least 8 characters')
    return
  }
  
  // Submit
  await apiClient.post('/auth/login', formData)
}

// ❌ BAD - No validation
const handleSubmit = async (formData) => {
  await apiClient.post('/auth/login', formData)
}
```

### Backend

```python
# ✅ GOOD - Pydantic validation
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

@router.post('/login')
async def login(request: LoginRequest):
    # Pydantic validates automatically
    user = await auth_service.authenticate(request.email, request.password)
    return {'token': user.token}

# ❌ BAD - Manual validation
@router.post('/login')
async def login(request: dict):
    if 'email' not in request:
        raise HTTPException(400, 'Email required')
    # More manual checks...
```

---

## 9. Testing Requirements

### Unit Test Rules

```javascript
// ✅ GOOD - Clear test structure
describe('ScreenerTable', () => {
  it('should render data correctly', () => {
    const data = [{ id: 1, symbol: 'AAPL' }]
    render(<ScreenerTable data={data} />)
    expect(screen.getByText('AAPL')).toBeInTheDocument()
  })
  
  it('should handle row click', () => {
    const onSelect = vi.fn()
    const data = [{ id: 1, symbol: 'AAPL' }]
    render(<ScreenerTable data={data} onSelect={onSelect} />)
    screen.getByText('AAPL').click()
    expect(onSelect).toHaveBeenCalledWith(1)
  })
})

// ✅ Test coverage minimum: 80%
```

### Backend Tests

```python
# ✅ GOOD - Clear async test
@pytest.mark.asyncio
async def test_filter_options():
    service = ScreenerService(mock_db)
    filters = {'symbol': 'AAPL'}
    results = await service.filter_options(filters)
    assert len(results) > 0
    assert results[0]['symbol'] == 'AAPL'

# ✅ Test coverage minimum: 80%
```

---

## 10. Performance Rules

### Frontend

```javascript
// ✅ GOOD - Memoize expensive components
const ScreenerTable = React.memo(({ data, onSelect }) => {
  return <table>{/* Render */}</table>
})

// ✅ GOOD - Use React Query for caching
const useScreenerData = (filters) => {
  return useQuery({
    queryKey: ['screener', filters],
    queryFn: () => apiClient.get('/screener', { params: filters }),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  })
}

// ❌ BAD - Fetch data in every render
function ScreenerTable() {
  const [data, setData] = useState([])
  
  useEffect(() => {
    apiClient.get('/screener').then(setData) // Runs every render
  })
}
```

### Backend

```python
# ✅ GOOD - Use connection pooling
# Configured in app/config.py
DB_POOL_SIZE = 15
DB_MAX_OVERFLOW = 5

# ✅ GOOD - Cache frequent queries
@cache.cached(timeout=300)
async def get_market_regime():
    # Cached for 5 minutes
    return await db.get_regime()

# ❌ BAD - No connection pooling
async def query():
    conn = create_connection()  # New connection every time
```

---

## 11. Security Rules

### Frontend

```javascript
// ✅ GOOD - Secure token handling
const token = localStorage.getItem('auth_token')
// Clear token on logout
localStorage.removeItem('auth_token')

// ✅ GOOD - Validate URLs
const isInternalUrl = (url) => {
  return url.startsWith('/') || url.includes(window.location.origin)
}

// ❌ BAD - Store secrets in code
const API_KEY = 'sk-1234567890'

// ❌ BAD - Open redirects
window.location.href = userProvidedUrl
```

### Backend

```python
# ✅ GOOD - Validate & sanitize input
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    symbol: str
    
    @validator('symbol')
    def symbol_must_be_valid(cls, v):
        if not v.isalpha() or len(v) > 10:
            raise ValueError('Invalid symbol')
        return v.upper()

# ✅ GOOD - Use environment variables
api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError('API_KEY not set')

# ❌ BAD - Hardcoded secrets
SUPABASE_KEY = 'your-key-here'

# ❌ BAD - Unsanitized SQL
query = f"SELECT * FROM users WHERE id = {user_id}"
```

---

## 12. Documentation Rules

- Every public function/component must have documentation
- README files required in major directories
- Inline comments for complex logic
- Update docs when changing behavior
- Keep examples current

---

## Next Steps

- **Review Folder Structure?** → [FOLDER-CONVENTIONS](./FOLDER-CONVENTIONS.md)
- **See Data Flows?** → [DATA-FLOW-RULES](./DATA-FLOW-RULES.md)
- **Check Architecture?** → [00-ARCHITECTURE-INDEX](../00-ARCHITECTURE-INDEX.md)

---

**Version:** A | **Last Updated:** 2026-06-15
