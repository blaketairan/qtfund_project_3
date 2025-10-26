# Data Model: Dynamic Script Columns

**Feature**: Dynamic Script Columns in List Query  
**Date**: 2025-01-27  
**Status**: Design Complete

## Entities

### Stock Info (Existing)

**Table**: `stock_info`  
**Purpose**: Store stock metadata

| Field | Type | Description |
|-------|------|-------------|
| symbol | string | Stock symbol with market prefix (e.g., "SH.600519") |
| stock_name | string | Full stock name |
| market_code | string | Market code (SH/SZ/BJ) |
| is_active | string | Active status (Y/N) |

**No changes required** - existing model is sufficient.

---

### Stock Daily Data (Existing)

**Table**: `stock_daily_data`  
**Purpose**: Store daily stock price and trading data

| Field | Type | Description |
|-------|------|-------------|
| symbol | string | Stock symbol (FK to stock_info) |
| trade_date | date | Trading date |
| close_price | decimal | Closing price |
| price_change_pct | decimal | Price change percentage |
| volume | integer | Trading volume |

**No changes required** - existing model is sufficient.

---

### Custom Script (Existing)

**Table**: `custom_scripts`  
**Purpose**: Store user-defined calculation scripts

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Primary key |
| name | string | Script name |
| column_name | string | Column name for this script |
| code | text | Python script code |
| created_at | timestamp | Creation timestamp |
| updated_at | timestamp | Last update timestamp |

**No changes required** - existing model is sufficient.

---

## Data Flow

### Request → Response Flow

```
User Request
GET /api/stock-price/list?script_ids=[1,2,3]&limit=100&market_code=SH

         ↓
         
1. Query Stocks
   SELECT * FROM stock_info 
   WHERE market_code='SH' AND is_active='Y'
   LIMIT 100
   
         ↓
         
2. Load Scripts
   SELECT * FROM custom_scripts 
   WHERE id IN (1, 2, 3)
   
         ↓
         
3. Get Latest Price Data
   For each stock:
   SELECT * FROM stock_daily_data
   WHERE symbol=? ORDER BY trade_date DESC LIMIT 1
   
         ↓
         
4. Execute Scripts
   For each stock and each script:
   - Build context (row data)
   - Execute script in sandbox
   - Collect result
   
         ↓
         
5. Build Response
   Append script_results to each stock record

         ↓
         
Response
{
  "data": [
    {
      "symbol": "SH.600519",
      "stock_name": "...",
      "close_price": 1750.50,
      ...,
      "script_results": {
        "1": 0.14,
        "2": 225.67,
        "3": null
      }
    }
  ]
}
```

---

## Data Access Patterns

### Pattern 1: Stock List Retrieval

**Query Type**: Standard SQL with filters  
**Indexes**: `symbol`, `market_code`, `is_active`  
**Performance**: Fast (< 100ms for 100 stocks)

### Pattern 2: Script Loading

**Query Type**: `SELECT * FROM custom_scripts WHERE id IN (...)`  
**Indexes**: `id` (primary key)  
**Performance**: Fast (< 10ms for 5 scripts)

### Pattern 3: Latest Price Data

**Query Type**: Already handled by `list_stocks_with_latest_price()`  
**Method**: LATERAL JOIN  
**Performance**: Fast (< 100ms for 100 stocks)

### Pattern 4: Script Execution

**Method**: RestrictedPython sandbox  
**Context**: Stock row data + `get_history()` function  
**Performance**: CPU-bound, ~5-10ms per script per stock

---

## Response Data Structure

### Extended Stock Record

```json
{
  "symbol": "SH.600519",
  "stock_name": "贵州茅台",
  "market_code": "SH",
  "is_active": "Y",
  "close_price": 1750.50,
  "price_change_pct": 2.35,
  "volume": 12500000,
  "latest_trade_date": "2025-01-26",
  "script_results": {
    "1": 0.14,
    "2": 225.67,
    "3": null
  }
}
```

### Script Results Sub-Object

| Field | Type | Description |
|-------|------|-------------|
| [script_id] | number \| null | Calculated result from script, or null if failed |

**Behavior**:
- Only included when `script_ids` parameter is provided
- Keys are script IDs as strings (JSON object keys)
- Values are script calculation results (numbers) or null if execution failed
- Missing keys indicate script was not requested

---

## Validation Rules

### Input Validation

1. **script_ids**:
   - Must be array of integers
   - Maximum 5 IDs per request
   - IDs must exist in custom_scripts table
   - Return 404 if any ID is invalid

2. **Existing Parameters** (unchanged):
   - `limit`: 1-10000, default 100
   - `offset`: >= 0, default 0
   - `market_code`: SH/SZ/BJ, optional
   - `is_active`: Y/N, default Y

### Output Validation

1. **script_results**:
   - Keys are script IDs (integers as strings)
   - Values are numbers or null
   - Missing keys indicate script not requested

2. **Response Structure**:
   - Must match API contract exactly
   - script_results only present when script_ids provided
   - Base fields unchanged

---

## Performance Considerations

### Query Performance

- **Stock List Query**: < 100ms for 100 stocks (with LATERAL JOIN)
- **Script Loading**: < 10ms for 5 scripts (single query)
- **Script Execution**: ~10ms per stock per script (CPU-bound)

### Optimization Strategies

1. **Batch Script Loading**: Load all scripts in one query
2. **Script Caching**: SandboxExecutor already caches compiled scripts
3. **Database Connection**: Reuse existing session
4. **Parallel Execution**: Consider async if performance is issue

**Note**: Performance depends on script complexity and database load.

---

## Error Scenarios

### Script Not Found

**Condition**: script_ids contains non-existent ID  
**Response**: 404 with message "脚本不存在"  
**Details**: "One or more script_ids not found"

### Script Execution Error

**Condition**: Script fails for specific stock  
**Response**: Include null for that script in that stock's script_results  
**Details**: Log error server-side, don't block other stocks

### Database Error

**Condition**: Database query fails  
**Response**: 500 with message "查询失败"  
**Details**: Return error to client, log details server-side

---

## Relationship Diagram

```
┌──────────────┐       ┌──────────────────┐
│  stock_info  │──1:N──│ stock_daily_data │
└──────────────┘       └──────────────────┘
       ↓                      ↓
       │                      │
       │              (Latest price)
       │                      │
       └──────┐        ┌───────┘
              ↓        ↓
         Stock Record (for script execution)
              │
              ↓
         Script Execution Context
              │
              ↓
         script_results (computed)
```

**Note**: Scripts are independent entities, not foreign key relationships. They are referenced by ID and loaded on-demand.

