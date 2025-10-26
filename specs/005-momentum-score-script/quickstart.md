# Quickstart: Momentum Score Script Example

**Feature**: 005-momentum-score-script  
**Date**: 2025-01-27

## Overview

Create a momentum score calculation script example and enhance the platform to support historical data access in sandbox scripts. The momentum score measures stock momentum using weighted linear regression on logarithmic price data.

## What's Being Created

### 1. Platform Enhancement
- Add `get_history()` function to sandbox executor
- Enable scripts to query historical stock data
- Support custom error handler callbacks

### 2. Example Script
- Create `script_example/momentum_score.py`
- Demonstrate weighted linear regression
- Include error handling examples
- Serve as template for custom calculations

## Implementation Steps

### Step 1: Enhance Sandbox Executor

**File**: `app/services/sandbox_executor.py`

Add historical data access function to safe globals:

```python
def _configure_safe_globals(self):
    """Configure safe builtin functions and modules"""
    safe = safe_globals.copy()
    
    # Add math module
    safe['math'] = math
    
    # Add get_history function for historical data access
    def get_history(symbol: str, days: int) -> list:
        """
        Get historical price data for a stock
        
        Args:
            symbol: Stock symbol (e.g., 'SH.600519')
            days: Number of trading days to retrieve (max 1000)
            
        Returns:
            List of dicts with 'close_price', 'trade_date', 'volume', 'price_change_pct'
        """
        from database.connection import db_manager
        from models.stock_data import StockDailyData
        from sqlalchemy import desc
        
        # Validate inputs
        if not symbol or not isinstance(symbol, str):
            return []
        
        if not isinstance(days, int) or days < 1 or days > 1000:
            days = 250  # Default to 250 days
        
        try:
            with db_manager.get_session() as session:
                query = session.query(StockDailyData).filter(
                    StockDailyData.symbol == symbol
                ).order_by(desc(StockDailyData.trade_date)).limit(days)
                
                results = query.all()
                
                return [{
                    'close_price': float(r.close_price) if r.close_price else None,
                    'trade_date': r.trade_date.strftime('%Y-%m-%d') if r.trade_date else None,
                    'volume': int(r.volume) if r.volume else 0,
                    'price_change_pct': float(r.price_change_pct) if r.price_change_pct else None
                } for r in results]
        except Exception as e:
            logger.error(f"Error retrieving history for {symbol}: {e}")
            return []
    
    safe['get_history'] = get_history
    self._safe_globals = safe
```

### Step 2: Create Example Script

**File**: `script_example/momentum_score.py`

```python
"""
Momentum Score Calculation Example

Calculates momentum score using weighted linear regression on logarithmic price data.
Serves as a template for custom stock analysis calculations.
"""

# ============ Configuration ============
# Parameters: modify these values as needed
DAYS = 250           # Number of trading days to analyze
WEIGHT_START = 1     # Starting weight for older data (linear progression)
WEIGHT_END = 2       # Ending weight for recent data
ANNUALIZATION = 250  # Trading days in a year for annualized return

# ============ Error Handler ============
def handle_error(data_available, data_requested, error_type):
    """
    Custom error handler for insufficient data scenarios
    
    Args:
        data_available: Number of data points actually available
        data_requested: Number of data points requested
        error_type: Type of error encountered
        
    Returns:
        Tuple (result_value, error_message) or single value
    """
    if error_type == 'insufficient_data':
        # Return None for insufficient data with error message
        return None
    return None

# ============ Helper Functions ============
def weighted_linear_regression(x, y, weights):
    """
    Calculate weighted linear regression
    
    Formula: m = sum(w*(x-x_mean)*(y-y_mean)) / sum(w*(x-x_mean)^2)
    
    Returns: (slope, intercept)
    """
    n = len(x)
    if n < 2:
        return 0, y[0] if y else 0
    
    weighted_sum_x = sum(w * xi for xi, w in zip(x, weights))
    weighted_sum_y = sum(w * yi for yi, w in zip(y, weights))
    weighted_sum = sum(weights)
    
    x_mean = weighted_sum_x / weighted_sum
    y_mean = weighted_sum_y / weighted_sum
    
    numerator = sum(w * (xi - x_mean) * (yi - y_mean) for xi, yi, w in zip(x, y, weights))
    denominator = sum(w * (xi - x_mean) ** 2 for xi, w in zip(x, weights))
    
    slope = numerator / denominator if denominator != 0 else 0
    intercept = y_mean - slope * x_mean
    
    return slope, intercept

def weighted_r_squared(x, y, weights, slope, intercept):
    """
    Calculate weighted R² coefficient
    
    Formula: R² = 1 - (sum(w*(y-predicted)^2) / sum(w*(y-y_mean)^2))
    """
    n = len(x)
    if n < 2:
        return 0
    
    weighted_sum_y = sum(w * yi for yi, w in zip(y, weights))
    weighted_sum = sum(weights)
    y_mean = weighted_sum_y / weighted_sum
    
    ss_res = sum(w * (yi - (slope * xi + intercept)) ** 2 for xi, yi, w in zip(x, y, weights))
    ss_tot = sum(w * (yi - y_mean) ** 2 for yi, w in zip(y, weights))
    
    return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

# ============ Main Calculation ============
def calculate_momentum(row):
    """
    Calculate momentum score for a stock
    
    Algorithm:
    1. Retrieve historical price data
    2. Apply logarithmic transform to prices
    3. Generate linearly increasing weights
    4. Calculate weighted linear regression
    5. Annualize the regression slope
    6. Calculate weighted R²
    7. Return momentum score = annualized_return * r_squared
    """
    # Get historical data
    history = get_history(row['symbol'], DAYS)
    
    # Check if we have minimum data (30 days)
    if len(history) < 30:
        error_handler = globals().get('handle_error', None)
        if error_handler:
            return error_handler(len(history), DAYS, 'insufficient_data')
        return None
    
    # Extract close prices and apply log transform
    prices = [h['close_price'] for h in history]
    y = [math.log(p) for p in prices if p > 0]
    
    if len(y) < 30:
        return None
    
    n = len(y)
    x = list(range(n))
    
    # Generate linearly increasing weights
    weights = []
    for i in range(n):
        if n > 1:
            weight = WEIGHT_START + (WEIGHT_END - WEIGHT_START) * i / (n - 1)
        else:
            weight = 1
        weights.append(weight)
    
    # Calculate weighted linear regression
    slope, intercept = weighted_linear_regression(x, y, weights)
    
    # Calculate annualized return: (e^slope)^250 - 1
    annualized_return = (math.exp(slope) ** ANNUALIZATION) - 1
    
    # Calculate weighted R²
    r_squared = weighted_r_squared(x, y, weights, slope, intercept)
    
    # Final momentum score
    momentum_score = annualized_return * r_squared
    
    return momentum_score

# ============ Execute Calculation ============
momentum = calculate_momentum(row)
result = momentum
```

## Testing

### Manual API Testing

1. **Start the application**:
```bash
python start_flask_app.py
```

2. **Test script execution**:
```bash
curl -X POST http://localhost:8000/api/custom-calculation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "<paste script code>",
    "stock_symbols": ["SH.600519", "SZ.000001"],
    "column_name": "momentum_score"
  }'
```

3. **Expected response**:
```json
{
  "code": 200,
  "message": "执行成功",
  "data": {
    "results": [
      {"symbol": "SH.600519", "value": 0.1523, "error": null},
      {"symbol": "SZ.000001", "value": 0.0892, "error": null}
    ]
  }
}
```

4. **Test with insufficient data**:
```bash
# Request 250 days for a new IPO with only 45 days of data
curl -X POST http://localhost:8000/api/custom-calculation/execute \
  -d '{"script": "...", "stock_symbols": ["SH.123456"], "column_name": "momentum"}'
```

### Validation Checklist

- [ ] Script executes without errors for stocks with sufficient data
- [ ] Script returns null/error for stocks with insufficient data
- [ ] Error handler called correctly when data insufficient
- [ ] Historical data API function works correctly
- [ ] Script passes sandbox security checks
- [ ] Calculation results are reasonable (between -1 and 1 typically)
- [ ] Script execution time < 2 seconds per stock

## Error Handling Examples

### Example 1: Custom Error Handler
```python
def handle_error(available, requested, error_type):
    """Use minimum data if available >= 30 days"""
    if available >= 30:
        return calculate_with_minimum_data()
    return None
```

### Example 2: Return Default Value
```python
def handle_error(available, requested, error_type):
    """Return neutral momentum score"""
    return 0.0
```

### Example 3: Re-throw Error
```python
def handle_error(available, requested, error_type):
    """Raise error to stop execution"""
    raise ValueError(f"Insufficient data: {available}/{requested}")
```

## Performance Testing

```bash
# Test with 10 stocks
time curl -X POST http://localhost:8000/api/custom-calculation/execute \
  -d '{"script": "...", "stock_symbols": ["SH.600519", "SH.600028", ...], "column_name": "momentum"}'

# Expected: < 20 seconds for 10 stocks
```

## Next Steps

1. Test with multiple stocks
2. Verify calculation accuracy with manual checks
3. Create variations of the script with different parameters
4. Save script to database for reuse
5. Document script modifications for end users

## Related Files

- `research.md` - Technical research and decisions
- `data-model.md` - Data model details
- `contracts/api-contracts.json` - API contract definition
- `app/services/sandbox_executor.py` - Sandbox executor (modify)
- `app/routes/custom_calculation.py` - API endpoints (no changes needed)

