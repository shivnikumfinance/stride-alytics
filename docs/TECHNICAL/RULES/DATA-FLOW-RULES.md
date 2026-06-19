# StrideAlytics — Data Flow Rules

**Request/response patterns, data contracts, and integration rules**

---

## 1. API Request/Response Format

### Standard REST Request

```javascript
// Frontend sends request
const response = await axios.get('/api/v1/screener', {
  params: {
    symbol: 'AAPL',
    min_price: 100,
    max_price: 150,
    limit: 50,
    offset: 0,
  },
  headers: {
    'Authorization': 'Bearer <jwt_token>',
    'Content-Type': 'application/json',
  },
})
```

### Standard Response Format

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "symbol": "AAPL",
      "price": 125.50,
      "change": 2.5,
      "timestamp": "2026-06-15T10:30:00Z"
    }
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "per_page": 50,
    "pages": 3
  },
  "metadata": {
    "cached": false,
    "request_id": "req-123456"
  }
}
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid parameters",
    "details": {
      "symbol": "Symbol is required"
    }
  },
  "metadata": {
    "request_id": "req-123456"
  }
}
```

---

## 2. HTTP Status Codes

| Code | Meaning | When to Use |
|------|---------|-----------|
| **200** | OK | Successful request |
| **201** | Created | Resource created successfully |
| **204** | No Content | Success with no response body |
| **400** | Bad Request | Invalid input/parameters |
| **401** | Unauthorized | Missing/invalid authentication |
| **403** | Forbidden | Authenticated but not authorized |
| **404** | Not Found | Resource doesn't exist |
| **409** | Conflict | Resource conflict (e.g., duplicate) |
| **429** | Too Many Requests | Rate limited |
| **500** | Internal Error | Server error |
| **503** | Service Unavailable | Maintenance/overloaded |

---

## 3. Authentication Flow

### Login Request/Response

```typescript
// Request
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure-password"
}

// Response (200 OK)
{
  "success": true,
  "data": {
    "user": {
      "id": "user-uuid",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "session": {
      "access_token": "eyJhbGciOiJIUzI1NiIs...",
      "token_type": "bearer",
      "expires_in": 3600
    }
  }
}
```

### Authenticated Requests

```javascript
// All subsequent requests must include JWT
headers: {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...'
}

// Backend verifies token:
1. Extract token from header
2. Verify signature
3. Check expiration
4. Extract user_id from 'sub' claim
5. Apply RLS policies based on user_id
```

### Token Refresh

```typescript
// When token expires
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "refresh-token-value"
}

// Response
{
  "success": true,
  "data": {
    "access_token": "new-jwt-token",
    "expires_in": 3600
  }
}
```

---

## 4. Common Data Types

### Option Data

```typescript
interface Option {
  id: string                // UUID
  symbol: string           // e.g., 'AAPL'
  strike: number          // e.g., 150.00
  expiry: string          // ISO date: '2026-12-31'
  option_type: 'call' | 'put'
  bid: number             // Bid price
  ask: number             // Ask price
  last_price: number      // Last traded price
  implied_vol: number     // IV as decimal (0.2 = 20%)
  delta: number           // Greeks
  gamma: number
  theta: number
  vega: number
  rho: number
  open_interest: number
  volume: number
  updated_at: string      // ISO timestamp
}
```

### Portfolio Data

```typescript
interface Portfolio {
  id: string
  user_id: string
  name: string
  description?: string
  created_at: string
  updated_at: string
  trades?: Trade[]
}
```

### Trade Data

```typescript
interface Trade {
  id: string
  user_id: string
  portfolio_id: string
  symbol: string
  trade_type: 'call' | 'put' | 'stock'
  direction: 'long' | 'short'
  entry_price: number
  exit_price?: number
  entry_date: string
  exit_date?: string
  quantity: number
  pnl?: number  // Calculated
  notes?: string
  created_at: string
  updated_at: string
}
```

---

## 5. Pagination Rules

### Paginated Request

```javascript
// Frontend request
GET /api/v1/screener?limit=50&offset=0

// Equivalent
GET /api/v1/screener?page=1&per_page=50
```

### Paginated Response

```json
{
  "success": true,
  "data": [ /* items */ ],
  "pagination": {
    "total": 1000,           // Total items
    "page": 1,               // Current page
    "per_page": 50,          // Items per page
    "pages": 20              // Total pages
  }
}
```

### Pagination Best Practices

```javascript
// ✅ GOOD - Always include pagination info
const handleNextPage = () => {
  const nextOffset = pagination.page * pagination.per_page
  fetchData({ offset: nextOffset })
}

// ❌ BAD - Fetch all data at once
const fetchAllData = async () => {
  const data = await fetch('/api/v1/screener?limit=100000')
}
```

---

## 6. Filtering & Sorting

### Filter Request Format

```javascript
// Complex filters
GET /api/v1/screener?symbol=AAPL&min_price=100&max_price=150&sort=-price

// Equivalent POST with JSON body
POST /api/v1/screener/search
Content-Type: application/json

{
  "filters": {
    "symbol": "AAPL",
    "min_price": 100,
    "max_price": 150
  },
  "sort": {
    "field": "price",
    "direction": "desc"
  },
  "limit": 50,
  "offset": 0
}
```

### Sort Parameters

```
// Format: field or -field (minus = descending)
sort=price              // Ascending
sort=-price             // Descending
sort=-price,symbol      // Primary sort, then secondary
```

---

## 7. Real-time Data Updates (Optional)

### WebSocket Connection

```javascript
// Connect to real-time updates
const ws = new WebSocket('wss://api.stridealytics.com/ws')

// Subscribe to updates
ws.send(JSON.stringify({
  action: 'subscribe',
  channel: 'options.AAPL'
}))

// Receive updates
ws.onmessage = (event) => {
  const update = JSON.parse(event.data)
  console.log('Price updated:', update.price)
}
```

---

## 8. Batch Operations

### Batch Request

```json
POST /api/v1/batch
Content-Type: application/json

{
  "requests": [
    {
      "id": "1",
      "method": "GET",
      "url": "/api/v1/screener/AAPL"
    },
    {
      "id": "2",
      "method": "GET",
      "url": "/api/v1/screener/MSFT"
    }
  ]
}
```

### Batch Response

```json
{
  "success": true,
  "responses": [
    {
      "id": "1",
      "status": 200,
      "data": { /* option data */ }
    },
    {
      "id": "2",
      "status": 200,
      "data": { /* option data */ }
    }
  ]
}
```

---

## 9. Caching Rules

### Cache Headers

```
// On Frontend
Cache-Control: max-age=300           // Cache for 5 minutes
Cache-Control: no-cache              // Revalidate every time
Cache-Control: no-store              // Never cache

// Example usage
useQuery({
  queryKey: ['screener'],
  queryFn: fetchScreener,
  staleTime: 5 * 60 * 1000,          // 5 minutes
  gcTime: 30 * 60 * 1000,            // Keep in cache 30 min
})
```

### Cache Key Rules

```javascript
// ✅ GOOD - Include all filter params in cache key
queryKey: ['screener', { symbol: 'AAPL', min_price: 100 }]

// ❌ BAD - Same cache key despite different filters
queryKey: ['screener']  // Will return wrong data
```

---

## 10. Error Handling & Retries

### Client-Side Retry Logic

```javascript
// ✅ GOOD - Retry with exponential backoff
async function fetchWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fetch(url)
    } catch (error) {
      if (i === maxRetries - 1) throw error
      
      const delay = Math.pow(2, i) * 1000  // 1s, 2s, 4s
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
}

// React Query handles this automatically
useQuery({
  queryKey: ['screener'],
  queryFn: fetchScreener,
  retry: 3,
  retryDelay: attemptIndex => Math.pow(2, attemptIndex) * 1000,
})
```

### Retryable vs Non-Retryable Errors

```
Retryable (5xx):
- 500 Internal Server Error
- 503 Service Unavailable
- Network timeouts
- Connection refused

Non-Retryable (4xx):
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
```

---

## 11. Rate Limiting

### Rate Limit Headers

```
Response Headers:
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1623801600

// Implementation
if (remainingRequests === 0) {
  waitUntilReset(resetTime)
}
```

---

## 12. Versioning

### API Versioning

```
Current:  /api/v1/*
Legacy:   /api/v0/*

// Each version is backward compatible
// Deprecation notice 6+ months before removal
```

### Schema Evolution

```
// ✅ GOOD - Adding optional field
{
  ...oldFields,
  newOptionalField?: string
}

// ❌ BAD - Removing required field
{
  ...fieldsWithoutRequired  // Breaks old clients
}
```

---

## 13. Data Consistency

### Transactions

```python
# Database transactions ensure consistency
async with db.transaction():
    # Either all succeed or all rollback
    await update_portfolio(portfolio_id, stats)
    await update_trades(portfolio_id, trades)
    await update_user_cache(user_id)
```

### Optimistic Locking

```json
// Include version field
{
  "id": "123",
  "version": 5,
  "data": {...}
}

// Update fails if version changed
PUT /api/v1/portfolio/123
{
  "data": {...},
  "version": 5
}

// Response if stale
409 Conflict
{
  "error": "Resource was modified"
}
```

---

## 14. Data Privacy

### Personally Identifiable Information (PII)

```
NEVER expose in responses:
- User passwords
- API keys/tokens
- Social security numbers
- Credit card numbers
- Health information

Response should only include:
- user_id (UUID, not email)
- name
- Public profile info
```

### Sensitive Data Filtering

```python
# ✅ GOOD - Only return safe fields
def get_user_response(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,  # User's own email only
    }

# ❌ BAD - Return all fields including password
def get_user_response(user):
    return user.dict()  # Includes password_hash!
```

---

## 15. Documentation Rules

Every API endpoint must document:
- **Request format** (headers, params, body)
- **Response format** (success & error)
- **Status codes** possible
- **Pagination** (if applicable)
- **Authentication** required
- **Rate limits** (if applicable)
- **Example request/response**

```markdown
### GET /api/v1/screener

Get filtered options list

**Authentication:** Required (Bearer token)

**Query Parameters:**
- `symbol` (string): Stock symbol (e.g., 'AAPL')
- `min_price` (number): Minimum price
- `max_price` (number): Maximum price
- `limit` (integer): Results per page (default: 50)
- `offset` (integer): Pagination offset (default: 0)

**Response:**
- 200: Successfully returned results
- 400: Invalid parameters
- 401: Unauthorized
- 429: Rate limited

**Example:**
```

---

## Next Steps

- **Check Coding Standards?** → [CODING-STANDARDS](./CODING-STANDARDS.md)
- **View Folder Conventions?** → [FOLDER-CONVENTIONS](./FOLDER-CONVENTIONS.md)
- **See Architecture?** → [00-ARCHITECTURE-INDEX](../00-ARCHITECTURE-INDEX.md)

---

**Version:** A | **Last Updated:** 2026-06-15
