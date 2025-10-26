# Research: Momentum Score Script Implementation

**Feature**: 005-momentum-score-script  
**Date**: 2025-01-27  
**Status**: Complete

## Research Questions

### Q1: How to implement historical data access API in RestrictedPython sandbox?

**Decision**: Add `get_history()` function to `SandboxExecutor._safe_globals` that queries TimescaleDB and returns historical price data.

**Rationale**:
- RestrictedPython sandbox allows adding functions to `safe_globals`
- Scripts need read-only access to historical price data
- Query TimescaleDB efficiently using existing database connection
- Function must return data in format usable by scripts (list of dicts)

**Implementation**:
```python
# In sandbox_executor.py
def _configure_safe_globals(self):
    safe = safe_globals.copy()
    
    # Add get_history function
    def get_history(symbol: str, days: int) -> list:
        """
        Get historical price data for a stock
        
        Args:
            symbol: Stock symbol (e.g., 'SH.600519')
            days: Number of trading days to retrieve
            
        Returns:
            List of dicts with 'close_price', 'trade_date', etc.
        """
        from database.connection import db_manager
        from models.stock_data import StockDailyData
        from sqlalchemy import desc
        
        with db_manager.get_session() as session:
            query = session.query(StockDailyData).filter(
                StockDailyData.symbol == symbol
            ).order_by(desc(StockDailyData.trade_date)).limit(days)
            
            results = query.all()
            
            return [{
                'close_price': float(r.close_price),
                'trade_date': r.trade_date.strftime('%Y-%m-%d'),
                'volume': int(r.volume),
                'price_change_pct': float(r.price_change_pct) if r.price_change_pct else None
            } for r in results]
    
    safe['get_history'] = get_history
    self._safe_globals = safe
```

**Security Considerations**:
- Read-only access to TimescaleDB
- No file system access
- No network access outside database
- Input validation (symbol format, days range)

**Alternatives considered**:
- Pre-fetch data and pass as context parameter: Less flexible, requires API changes
- Use raw SQL with execute(): More vulnerable to injection attacks

### Q2: How to implement weighted linear regression without numpy in RestrictedPython?

**Decision**: Implement weighted linear regression using basic Python math operations and formulas.

**Rationale**:
- RestrictedPython sandbox blocks numpy imports
- Need core regression calculation without external libraries
- Manual implementation using mathematical formulas
- Use basic Python operations: sum, len, range, math.exp, math.pow

**Implementation**:
```python
# Weighted linear regression formula
# y = mx + b where weights apply to residuals
# m = sum(w*(x-x_mean)*(y-y_mean)) / sum(w*(x-x_mean)^2)
# b = y_mean - m*x_mean

def weighted_linear_regression(x, y, weights):
    n = len(x)
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

# R² calculation with weighted residuals
def weighted_r_squared(x, y, weights, slope, intercept):
    y_mean = sum(w * yi for yi, w in zip(y, weights)) / sum(weights)
    
    ss_res = sum(w * (yi - (slope * xi + intercept)) ** 2 for xi, yi, w in zip(x, y, weights))
    ss_tot = sum(w * (yi - y_mean) ** 2 for yi, w in zip(y, weights))
    
    return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
```

**Performance**: Acceptable for 60-250 data points. Manual calculation without optimization libraries.

**Alternatives considered**:
- Include numpy in safe globals: Security risk, restricted imports
- Use sqlalchemy for calculations: Complex, DB-dependent

### Q3: How to implement custom error handler callback pattern?

**Decision**: Check if script defines `handle_error()` function, use it if available, otherwise use platform default.

**Rationale**:
- Scripts may define error handlers in their code
- Default fallback for scripts without custom handlers
- Simple function existence check before execution
- Platform provides sensible defaults

**Implementation**:
```python
# In sandbox_executor.py execute() method
def execute(self, script_code: str, context: Optional[Dict[str, Any]] = None):
    # Compile and execute script
    byte_code = compile_restricted(script_code, ...)
    exec(byte_code.code, exec_globals)
    
    # Check if script defines error handler
    has_custom_handler = 'handle_error' in exec_globals
    
    if has_custom_handler:
        # Script can call handle_error(data_available, data_requested, error_type)
        pass
    else:
        # Provide default implementation
        def default_error_handler(available, requested, error_type):
            return None, f"Insufficient data: requested {requested}, available {available}"
        
        exec_globals['handle_error'] = default_error_handler
    
    # Execute with error handling support
    ...
```

**Error Handler Interface**:
```python
def handle_error(data_available: int, data_requested: int, error_type: str) -> tuple:
    """
    Custom error handler for insufficient data
    
    Args:
        data_available: Actual data points available
        data_requested: Data points requested
        error_type: Type of error ('insufficient_data', 'missing_prices', etc.)
        
    Returns:
        Tuple of (result, error_message)
    """
    # Script can implement custom logic:
    # - Return None/null
    # - Use minimum available data
    # - Return default value
    # - Re-throw error
```

**Alternatives considered**:
- Predefined error handling policies: Less flexible
- Always use default: No customization possible
- Pass handler as parameter: API complexity

### Q4: How to structure the example script for clarity and reuse?

**Decision**: Create standalone Python script with clear sections: imports/configuration, error handler, main calculation logic, output formatting.

**Rationale**:
- Example scripts should be self-contained and readable
- Clear organization aids understanding and modification
- Include inline comments explaining calculation steps
- Demonstrate best practices (error handling, parameter configuration)

**Script Structure**:
```python
# script_example/momentum_score.py

# ============ Configuration ============
# Parameters (users modify these values)
DAYS = 250           # Number of trading days to analyze
WEIGHT_START = 1     # Starting weight for older data
WEIGHT_END = 2       # Ending weight for recent data
ANNUALIZATION = 250  # Trading days in a year

# ============ Error Handler ============
def handle_error(available, requested, error_type):
    """Custom error handler"""
    if error_type == 'insufficient_data':
        # Return None for insufficient data
        return None
    return None

# ============ Main Calculation ============
def calculate_momentum(row):
    # Get historical data
    history = get_history(row['symbol'], DAYS)
    
    if len(history) < 30:  # Minimum required data
        return handle_error(len(history), DAYS, 'insufficient_data')
    
    # Extract close prices and apply log transform
    prices = [h['close_price'] for h in history]
    y = [math.log(p) for p in prices]
    n = len(y)
    x = list(range(n))
    
    # Generate weights (linear increase)
    weights = []
    for i in range(n):
        weight = WEIGHT_START + (WEIGHT_END - WEIGHT_START) * i / (n - 1) if n > 1 else 1
        weights.append(weight)
    
    # Calculate weighted linear regression
    slope, intercept = weighted_linear_regression(x, y, weights)
    
    # Calculate annualized return
    annualized_return = (math.exp(slope) ** ANNUALIZATION) - 1
    
    # Calculate R²
    r_squared = weighted_r_squared(x, y, weights, slope, intercept)
    
    # Final momentum score
    momentum_score = annualized_return * r_squared
    
    return momentum_score

# ============ Result ============
# Execute calculation and set result variable
momentum = calculate_momentum(row)
result = momentum
```

**Alternatives considered**:
- Monolithic script without sections: Less readable
- External config file: Adds complexity, not needed for example

## Technology Choices

### Historical Data Access
- **Decision**: Direct TimescaleDB query via safe globals function
- **Why**: Efficient, secure (read-only), fits existing architecture
- **Tradeoff**: Requires database connection in sandbox context

### Regression Implementation
- **Decision**: Manual calculation without numpy
- **Why**: Security (no external libraries), sufficient for 60-250 data points
- **Performance**: Acceptable O(n) complexity, <100ms for typical datasets

### Error Handling
- **Decision**: Optional custom handlers with platform defaults
- **Why**: Flexible for advanced users, simple for beginners
- **Pattern**: Check function existence before providing default

## Integration Points

### Sandbox Executor Enhancement
- Add `get_history()` to `_safe_globals` in `app/services/sandbox_executor.py`
- Function should query TimescaleDB and return formatted historical data
- Must handle symbol format validation, days range limits, error cases

### Example Script Placement
- Create `script_example/momentum_score.py` with complete implementation
- Include all helper functions (regression, R² calculation, error handling)
- Comment code extensively for educational value

### API Compatibility
- Example script uses existing `/api/custom-calculation/execute` endpoint
- No API changes required, only sandbox enhancement
- Script can be saved to database and executed like other custom scripts

## Implementation Approach Summary

1. **Enhance Sandbox Executor** (`app/services/sandbox_executor.py`):
   - Add `get_history()` function to safe globals
   - Implement weighted regression helper functions
   - Provide default error handler implementation
   - Update validation to check for custom error handlers

2. **Create Example Script** (`script_example/momentum_score.py`):
   - Implement momentum score calculation with weighted linear regression
   - Include error handler example
   - Document all calculation steps with comments
   - Use hardcoded configuration parameters

3. **Testing**:
   - Test with stocks having 250+ days of data
   - Test with stocks having insufficient data (<30 days)
   - Test error handler behavior
   - Verify execution time < 2 seconds

## Unknowns Resolved

- ✅ Historical data access via sandbox function
- ✅ Weighted regression without numpy
- ✅ Custom error handler pattern
- ✅ Example script structure and organization
- ✅ Security constraints in RestrictedPython
- ✅ Integration with existing custom calculation API

## References

- RestrictedPython documentation
- PostgreSQL TimescaleDB query patterns
- Weighted linear regression mathematical formulas
- Sandbox security best practices for Python code execution
- Custom calculation API existing implementations

