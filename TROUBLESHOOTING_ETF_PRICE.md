# ETF价格数据诊断指南

## 问题描述

list接口能查到ETF名字，但没有价格数据。

## 问题分析

### ETF价格查询逻辑

ETF的价格数据存储在与股票相同的 `stock_daily_data` 表中，查询逻辑如下：

```sql
SELECT 
    si.symbol,
    si.stock_name,
    si.is_etf,
    lp.close_price,
    lp.volume,
    lp.price_change_pct,
    lp.trade_date as latest_trade_date
FROM stock_info si
LEFT JOIN LATERAL (
    SELECT 
        close_price, 
        volume, 
        price_change_pct,
        trade_date
    FROM stock_daily_data sd
    WHERE sd.symbol = si.symbol  -- 关键：按symbol匹配
    ORDER BY sd.trade_date DESC
    LIMIT 1
) lp ON true
WHERE si.is_etf = 'Y'
```

### 可能原因

1. **数据库中没有ETF价格数据**
   - `stock_daily_data` 表中没有对应ETF的 `symbol` 记录
   - ETF的数据尚未同步到数据库

2. **ETF的symbol在stock_daily_data中不存在**
   - 例如：`stock_info` 有 `SH.510300`，但 `stock_daily_data` 中没有该symbol的记录
   - 检查 `stock_info.is_etf = 'Y'` 的记录在 `stock_daily_data` 中是否有对应数据

3. **数据同步问题**
   - ETF数据可能未同步到 `stock_daily_data` 表
   - 需要运行数据同步脚本

## 诊断步骤

### 1. 检查ETF总数

```sql
SELECT COUNT(*) as total_etfs 
FROM stock_info 
WHERE is_etf = 'Y';
```

### 2. 检查有价格数据的ETF数量

```sql
SELECT COUNT(DISTINCT si.symbol) as etfs_with_price_data
FROM stock_info si
INNER JOIN stock_daily_data sd ON sd.symbol = si.symbol
WHERE si.is_etf = 'Y';
```

### 3. 检查特定ETF的价格数据

```sql
SELECT 
    si.symbol,
    si.stock_name,
    COUNT(sd.trade_date) as price_record_count,
    MAX(sd.trade_date) as latest_trade_date
FROM stock_info si
LEFT JOIN stock_daily_data sd ON sd.symbol = si.symbol
WHERE si.is_etf = 'Y'
GROUP BY si.symbol, si.stock_name
ORDER BY si.symbol
LIMIT 10;
```

### 4. 测试LATERAL JOIN查询

```sql
SELECT 
    si.symbol,
    si.stock_name,
    lp.close_price,
    lp.trade_date as latest_trade_date
FROM stock_info si
LEFT JOIN LATERAL (
    SELECT 
        close_price,
        volume,
        price_change_pct,
        trade_date
    FROM stock_daily_data sd
    WHERE sd.symbol = si.symbol
    ORDER BY sd.trade_date DESC
    LIMIT 1
) lp ON true
WHERE si.is_etf = 'Y'
LIMIT 5;
```

## 解决方案

### 方案1: 同步ETF价格数据

如果数据库中缺少ETF价格数据，需要运行数据同步脚本：

```python
# 运行ETF数据同步
python sync_etf_data.py
```

### 方案2: 检查数据同步逻辑

确保数据同步脚本包含ETF数据：

```python
# app/tasks/sync_stock_data.py
def sync_etf_data():
    """同步ETF数据"""
    etfs = query_etf_list()  # 从数据源获取ETF列表
    for etf in etfs:
        # 同步ETF的历史价格数据
        sync_daily_data(etf.symbol)
```

### 方案3: 手动添加ETF价格数据

如果需要快速测试，可以手动插入测试数据：

```sql
INSERT INTO stock_daily_data 
    (symbol, stock_name, trade_date, close_price, volume, price_change_pct, market_code)
VALUES 
    ('SH.510300', '沪深300ETF', '2025-10-27', 4.852, 52000000, 0.65, 'SH');
```

## 验证

查询LATERAL JOIN是否返回价格：

```bash
curl "http://localhost:8000/api/stock-price/list?is_etf=true&limit=5"
```

期望响应包含 `close_price` 字段：

```json
{
  "code": 200,
  "data": [
    {
      "symbol": "SH.510300",
      "stock_name": "沪深300ETF",
      "is_etf": true,
      "close_price": 4.852,  // 应该有关闭价
      "price_change_pct": 0.65,
      "volume": 52000000
    }
  ]
}
```

## 结论

ETF价格查询逻辑是正确的，使用LATERAL JOIN从 `stock_daily_data` 表中查询。

**问题根源**：数据库中缺少ETF的价格数据。

**解决方法**：运行数据同步脚本，将ETF的历史价格数据同步到 `stock_daily_data` 表中。

