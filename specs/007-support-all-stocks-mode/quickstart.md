# Quickstart: Support All-Stocks Mode for Custom Calculations

**Feature**: 007-support-all-stocks-mode  
**Date**: 2025-01-27

## Overview

Extend the custom calculation API to support applying scripts to all active stocks when the `stock_symbols` array is empty. This allows users to calculate metrics for the entire stock universe without specifying individual symbols.

## What's Being Modified

### API Enhancement
- Modify `/api/custom-calculations/execute` to accept empty `stock_symbols` array
- Fetch all active stocks from database when array is empty
- Return execution summary for all-stocks operations
- Maintain backward compatibility with specific symbols

### Service Enhancement
- Add `get_all_active_stocks()` method to StockDataService
- Query database for all stocks with is_active='Y'
- Support optional market_code filtering

## Implementation Steps

### Step 1: Add Service Method

**File**: `app/services/stock_data_service.py`

Add method to fetch all active stocks:

```python
def get_all_active_stocks(self, market_code: Optional[str] = None) -> List[str]:
    """
    Get all active stock symbols from database
    
    Args:
        market_code: Optional market filter (SH/SZ/BJ)
        
    Returns:
        List of stock symbols
    """
    try:
        with db_manager.get_session() as session:
            query = session.query(StockInfo.symbol).filter(
                StockInfo.is_active == 'Y'
            )
            
            if market_code:
                query = query.filter(StockInfo.market_code == market_code)
            
            results = query.all()
            return [row.symbol for row in results]
            
    except Exception as e:
        logger.error(f"获取所有活跃股票失败: {e}")
        return []
```

### Step 2: Modify API Endpoint

**File**: `app/routes/custom_calculation.py`

Update the execute_script function:

```python
@custom_calculation_bp.route('/execute', methods=['POST'])
def execute_script():
    """执行自定义Python脚本"""
    try:
        data = request.get_json() or {}
        
        script = data.get('script', '')
        script_id = data.get('script_id')
        column_name = data.get('column_name', '')
        stock_symbols = data.get('stock_symbols', [])
        
        # Load script if script_id provided
        if script_id:
            from app.models.custom_script import CustomScriptService
            saved_script = CustomScriptService.get_by_id(script_id)
            if not saved_script:
                return create_error_response(404, "未找到脚本", f"脚本ID {script_id} 不存在")
            script = saved_script.code
        
        # Validate required parameters
        if not script:
            return create_error_response(400, "参数错误", "script或script_id不能为空")
        
        if not column_name:
            return create_error_response(400, "参数错误", "column_name不能为空")
        
        # Handle empty stock_symbols array (all stocks mode)
        if not stock_symbols or len(stock_symbols) == 0:
            # Fetch all active stocks
            from app.services.stock_data_service import StockDataService
            service = StockDataService()
            all_stocks = service.get_all_active_stocks()
            stock_symbols = all_stocks
            
            if not stock_symbols:
                return create_error_response(404, "未找到股票", "数据库中没有活跃股票")
        
        # Validate stock_symbols (backward compatibility check)
        if not isinstance(stock_symbols, list):
            return create_error_response(400, "参数错误", "stock_symbols必须是数组")
        
        if len(stock_symbols) > 200:
            return create_error_response(400, "参数错误", "stock_symbols最多支持200个")
        
        logger.info(f"执行自定义计算: column_name={column_name}, stocks={len(stock_symbols)}")
        
        # Validate script syntax
        from app.services.sandbox_executor import SandboxExecutor
        executor = SandboxExecutor()
        is_valid, syntax_error = executor.validate_syntax(script)
        if not is_valid:
            return create_error_response(400, "脚本语法错误", syntax_error)
        
        # Execute script for each stock
        results = []
        successful = 0
        failed = 0
        
        for symbol in stock_symbols:
            try:
                stock_row = _get_stock_data(symbol)
                
                if stock_row is None:
                    results.append({
                        "symbol": symbol,
                        "value": None,
                        "error": "股票数据不存在"
                    })
                    failed += 1
                    continue
                
                result, error = executor.execute(script, {"row": stock_row})
                
                results.append({
                    "symbol": symbol,
                    "value": result,
                    "error": error
                })
                
                if error:
                    failed += 1
                else:
                    successful += 1
                    
            except Exception as e:
                logger.error(f"执行脚本失败，股票: {symbol}, 错误: {e}")
                results.append({
                    "symbol": symbol,
                    "value": None,
                    "error": str(e)
                })
                failed += 1
        
        # Prepare response data
        response_data = {"results": results}
        
        # Add summary for all-stocks mode (more than 1 stock processed)
        if len(results) > 1:
            response_data["summary"] = {
                "total": len(results),
                "successful": successful,
                "failed": failed
            }
        
        return create_success_response(
            data=response_data,
            message=f"执行成功，处理 {len(results)} 只股票"
        )
        
    except Exception as e:
        logger.error(f"执行自定义计算失败: {e}")
        return create_error_response(500, "执行失败", str(e))
```

## Testing

### Manual API Testing

1. **Test with empty array (all stocks)**:
```bash
curl -X POST http://localhost:8000/api/custom-calculations/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "result = row[\"close_price\"] * 1.1",
    "stock_symbols": [],
    "column_name": "计算列"
  }'
```

2. **Test with specific symbols (backward compatibility)**:
```bash
curl -X POST http://localhost:8000/api/custom-calculations/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "result = row[\"close_price\"] * 1.1",
    "stock_symbols": ["SH.600519", "SZ.000001"],
    "column_name": "计算列"
  }'
```

### Validation Checklist

- [ ] Empty array returns results for all active stocks
- [ ] Specific symbols still work (backward compatibility)
- [ ] API returns execution summary for all-stocks mode
- [ ] Error handling works for missing stock data
- [ ] Script executes correctly for all stocks
- [ ] Response includes total, successful, failed counts

## API Behavior

### Empty Array Mode

**Request**:
```json
{
  "script": "result = row['close_price'] * 1.1",
  "stock_symbols": [],
  "column_name": "计算列"
}
```

**Behavior**: API fetches all active stocks from database and applies script to each.

**Response**:
```json
{
  "code": 200,
  "message": "执行成功，处理 1500 只股票",
  "data": {
    "results": [
      {"symbol": "SH.600519", "value": 1250.5, "error": null},
      {"symbol": "SZ.000001", "value": 15.2, "error": null},
      ...
    ],
    "summary": {
      "total": 1500,
      "successful": 1498,
      "failed": 2
    }
  }
}
```

### Backward Compatibility

**Request**:
```json
{
  "script": "result = row['close_price'] * 1.1",
  "stock_symbols": ["SH.600519", "SZ.000001"],
  "column_name": "计算列"
}
```

**Behavior**: API uses provided symbols, works exactly as before.

**Response**:
```json
{
  "code": 200,
  "message": "执行成功，处理 2 只股票",
  "data": {
    "results": [
      {"symbol": "SH.600519", "value": 1250.5, "error": null},
      {"symbol": "SZ.000001", "value": 15.2, "error": null}
    ]
  }
}
```

## Performance Considerations

### Execution Time

- Script execution: ~2 seconds per stock
- 100 stocks: ~200 seconds
- 500 stocks: ~1000 seconds

### Recommendations

1. **Small stock universes (< 100 stocks)**: Process all at once
2. **Medium (100-500 stocks)**: Warn user about execution time
3. **Large (> 500 stocks)**: Suggest adding filters or pagination

### Batching (Future Enhancement)

For very large universes, consider implementing batching:

```python
BATCH_SIZE = 100
for i in range(0, len(stock_symbols), BATCH_SIZE):
    batch = stock_symbols[i:i + BATCH_SIZE]
    # Process batch
    # Return intermediate results
```

## Migration Notes

### Backward Compatibility

- **No breaking changes**: Existing API calls work unchanged
- Specific symbols mode: Unchanged behavior
- New feature: Empty array applies to all stocks

### Database Impact

- Query all active stocks: Simple SELECT with existing index
- Performance: < 100ms for 1000 stocks
- No schema changes needed

## Next Steps

1. **Implement service method** (get_all_active_stocks)
2. **Modify API endpoint** (handle empty array)
3. **Test with real data** (verify correct behavior)
4. **Update documentation** (API usage guide)
5. **Frontend integration** (update UI to use all-stocks mode)

## Related Files

- [research.md](./research.md) - Technical research and decisions
- [data-model.md](./data-model.md) - Data model details
- [contracts/api-contracts.json](./contracts/api-contracts.json) - API contract
- `app/services/stock_data_service.py` - Service layer (modify)
- `app/routes/custom_calculation.py` - API endpoint (modify)

