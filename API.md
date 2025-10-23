# API 接口文档

股票数据查询服务 API 文档

**版本**: v1.0  
**基础URL**: `http://localhost:8000`  
**内容类型**: `application/json`

---

## 📋 目录

- [1. 系统接口](#1-系统接口)
  - [1.1 健康检查](#11-健康检查)
  - [1.2 版本信息](#12-版本信息)
  - [1.3 服务信息](#13-服务信息)
- [2. 股票行情接口](#2-股票行情接口)
  - [2.1 查询股票行情](#21-查询股票行情)
  - [2.2 获取股票基础信息](#22-获取股票基础信息)
  - [2.3 列出所有股票](#23-列出所有股票)
- [3. 股票信息接口](#3-股票信息接口)
  - [3.1 从本地JSON查询](#31-从本地json查询)
  - [3.2 获取统计信息](#32-获取统计信息)
- [4. 错误码说明](#4-错误码说明)
- [5. 数据模型](#5-数据模型)

---

## 1. 系统接口

### 1.1 健康检查

检查服务运行状态和数据库连接。

**接口地址**: `/api/health`  
**请求方法**: `GET`  
**认证**: 无

#### 请求示例

```bash
curl http://localhost:8000/api/health
```

#### 返回示例（成功）

```json
{
  "code": 200,
  "message": "系统运行正常",
  "timestamp": "2025-10-24 10:30:45",
  "data": {
    "status": "healthy",
    "timestamp": "2025-10-24 10:30:45",
    "database": "connected",
    "version": "1.0.0 (查询服务)",
    "api_server": "running"
  }
}
```

#### 返回示例（异常）

```json
{
  "code": 503,
  "message": "系统异常",
  "timestamp": "2025-10-24 10:30:45",
  "detail": "数据库连接失败",
  "error": true,
  "data": {
    "status": "unhealthy",
    "database": "disconnected"
  }
}
```

---

### 1.2 版本信息

获取服务版本和功能信息。

**接口地址**: `/api/version`  
**请求方法**: `GET`  
**认证**: 无

#### 请求示例

```bash
curl http://localhost:8000/api/version
```

#### 返回示例

```json
{
  "code": 200,
  "message": "版本信息查询成功",
  "timestamp": "2025-10-24 10:30:45",
  "data": {
    "name": "股票数据查询服务",
    "version": "1.0.0",
    "framework": "Flask",
    "database": "TimescaleDB",
    "python_version": "3.9+",
    "description": "纯净的数据库查询服务",
    "features": [
      "股票行情数据查询 (TimescaleDB)",
      "股票信息查询 (数据库 + 本地JSON)",
      "健康检查和版本信息"
    ]
  }
}
```

---

### 1.3 服务信息

获取服务端点和功能概览。

**接口地址**: `/`  
**请求方法**: `GET`  
**认证**: 无

#### 请求示例

```bash
curl http://localhost:8000/
```

#### 返回示例

```json
{
  "code": 200,
  "message": "股票数据查询服务运行中",
  "timestamp": "2025-10-24 10:30:45",
  "data": {
    "name": "股票数据查询服务",
    "version": "1.0.0",
    "description": "纯净的数据库查询服务",
    "endpoints": {
      "健康检查": "/api/health",
      "版本信息": "/api/version",
      "股票行情查询": {
        "查询行情数据": "/api/stock-price/query",
        "获取股票信息": "/api/stock-price/info/<symbol>",
        "列出所有股票": "/api/stock-price/list"
      },
      "股票信息查询": {
        "本地JSON查询": "/api/stock-info/local",
        "统计信息": "/api/stock-info/statistics"
      }
    },
    "note": "本服务仅提供查询功能，数据同步请使用同步服务(端口7777)"
  }
}
```

---

## 2. 股票行情接口

### 2.1 查询股票行情

从TimescaleDB查询股票历史行情数据。

**接口地址**: `/api/stock-price/query`  
**请求方法**: `GET` | `POST`  
**认证**: 无

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| symbol | string | 是 | - | 股票代码（格式：SH.600519） |
| start_date | string | 否 | - | 开始日期（格式：YYYY-MM-DD） |
| end_date | string | 否 | - | 结束日期（格式：YYYY-MM-DD） |
| limit | int | 否 | 100 | 返回数量限制（1-10000） |

#### 请求示例（GET）

```bash
curl "http://localhost:8000/api/stock-price/query?symbol=SH.600519&start_date=2024-01-01&end_date=2024-12-31&limit=10"
```

#### 请求示例（POST）

```bash
curl -X POST http://localhost:8000/api/stock-price/query \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "SH.600519",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "limit": 10
  }'
```

#### 返回示例

```json
{
  "code": 200,
  "message": "查询成功",
  "timestamp": "2025-10-24 10:30:45",
  "symbol": "SH.600519",
  "source": "database",
  "count": 10,
  "total": 245,
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31",
    "count": 10
  },
  "data": [
    {
      "trade_date": "2024-12-31",
      "symbol": "SH.600519",
      "stock_name": "贵州茅台",
      "open_price": 1650.00,
      "high_price": 1680.00,
      "low_price": 1645.00,
      "close_price": 1675.00,
      "volume": 1234567,
      "turnover": 2058750000.00,
      "price_change": 25.00,
      "price_change_pct": 1.52,
      "premium_rate": null,
      "market_code": "SH"
    }
  ]
}
```

#### 错误示例

```json
{
  "code": 400,
  "message": "参数错误",
  "timestamp": "2025-10-24 10:30:45",
  "detail": "股票代码格式错误，应为: SH.600519",
  "error": true
}
```

---

### 2.2 获取股票基础信息

获取单个股票的基础信息。

**接口地址**: `/api/stock-price/info/{symbol}`  
**请求方法**: `GET`  
**认证**: 无

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | string | 是 | 股票代码（格式：SH.600519） |

#### 请求示例

```bash
curl http://localhost:8000/api/stock-price/info/SH.600519
```

#### 返回示例

```json
{
  "code": 200,
  "message": "查询成功",
  "timestamp": "2025-10-24 10:30:45",
  "data": {
    "symbol": "SH.600519",
    "stock_name": "贵州茅台",
    "stock_code": "600519",
    "market_code": "SH",
    "stock_type": "股票",
    "industry": "白酒",
    "is_active": "Y",
    "last_sync_date": "2024-12-31T00:00:00",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

#### 错误示例

```json
{
  "code": 404,
  "message": "未找到股票信息",
  "timestamp": "2025-10-24 10:30:45",
  "detail": "未知错误",
  "error": true
}
```

---

### 2.3 列出所有股票

列出数据库中的股票清单，支持分页和筛选。

**接口地址**: `/api/stock-price/list`  
**请求方法**: `GET`  
**认证**: 无

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| market_code | string | 否 | - | 市场代码（SH/SZ/BJ） |
| is_active | string | 否 | Y | 是否活跃（Y/N） |
| limit | int | 否 | 100 | 返回数量限制（1-10000） |
| offset | int | 否 | 0 | 分页偏移量（≥0） |

#### 请求示例

```bash
# 默认查询（前100条活跃股票）
curl http://localhost:8000/api/stock-price/list

# 查询上海市场的股票（500条）
curl "http://localhost:8000/api/stock-price/list?market_code=SH&limit=500"

# 分页查询（第2页）
curl "http://localhost:8000/api/stock-price/list?limit=100&offset=100"

# 查询所有股票（包括非活跃）
curl "http://localhost:8000/api/stock-price/list?is_active=N&limit=1000"
```

#### 返回示例

```json
{
  "code": 200,
  "message": "查询到 100 只股票",
  "timestamp": "2025-10-24 10:30:45",
  "total": 5000,
  "data": [
    {
      "symbol": "SH.600519",
      "stock_name": "贵州茅台",
      "market_code": "SH",
      "is_active": "Y",
      "last_sync_date": "2024-12-31T00:00:00"
    },
    {
      "symbol": "SH.600036",
      "stock_name": "招商银行",
      "market_code": "SH",
      "is_active": "Y",
      "last_sync_date": "2024-12-31T00:00:00"
    }
  ]
}
```

#### 错误示例（参数超限）

```json
{
  "code": 400,
  "message": "参数错误",
  "timestamp": "2025-10-24 10:30:45",
  "detail": "limit参数不能超过10000，建议使用分页查询",
  "error": true
}
```

---

## 3. 股票信息接口

### 3.1 从本地JSON查询

从本地JSON文件查询股票信息（不依赖数据库）。

**接口地址**: `/api/stock-info/local`  
**请求方法**: `GET`  
**认证**: 无

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| exchange_code | string | 否 | - | 交易所代码（XSHG/XSHE/BJSE） |
| keyword | string | 否 | - | 搜索关键词（股票名称或代码） |
| is_active | string | 否 | true | 是否只返回活跃股票（true/false） |
| limit | int | 否 | 100 | 返回数量限制（1-10000） |

#### 请求示例

```bash
# 默认查询（前100条活跃股票）
curl http://localhost:8000/api/stock-info/local

# 查询上交所股票（500条）
curl "http://localhost:8000/api/stock-info/local?exchange_code=XSHG&limit=500"

# 搜索关键词
curl "http://localhost:8000/api/stock-info/local?keyword=茅台"

# 查询所有股票（包括非活跃）
curl "http://localhost:8000/api/stock-info/local?is_active=false&limit=1000"
```

#### 返回示例

```json
{
  "code": 200,
  "message": "查询到 100 只股票",
  "timestamp": "2025-10-24 10:30:45",
  "count": 100,
  "data": [
    {
      "ticker": "600519",
      "name": "贵州茅台",
      "symbol": "SH.600519",
      "exchange_code": "XSHG",
      "exchange_name_cn": "上海证券交易所",
      "is_active": true,
      "country_code": "CN",
      "currency_code": "CNY",
      "first_fetch_time": "2024-01-01T00:00:00"
    },
    {
      "ticker": "600036",
      "name": "招商银行",
      "symbol": "SH.600036",
      "exchange_code": "XSHG",
      "exchange_name_cn": "上海证券交易所",
      "is_active": true,
      "country_code": "CN",
      "currency_code": "CNY",
      "first_fetch_time": "2024-01-01T00:00:00"
    }
  ]
}
```

---

### 3.2 获取统计信息

获取股票清单的统计信息。

**接口地址**: `/api/stock-info/statistics`  
**请求方法**: `GET`  
**认证**: 无

#### 请求示例

```bash
curl http://localhost:8000/api/stock-info/statistics
```

#### 返回示例

```json
{
  "code": 200,
  "message": "统计信息查询成功",
  "timestamp": "2025-10-24 10:30:45",
  "data": {
    "total_stocks": 5000,
    "active_stocks": 4800,
    "inactive_stocks": 200,
    "exchanges": {
      "XSHG": {
        "name": "上海证券交易所",
        "count": 2000,
        "active": 1950
      },
      "XSHE": {
        "name": "深圳证券交易所",
        "count": 2800,
        "active": 2700
      },
      "BJSE": {
        "name": "北京证券交易所",
        "count": 200,
        "active": 150
      }
    },
    "last_updated": "2024-12-31T00:00:00"
  }
}
```

---

## 4. 错误码说明

### HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源未找到 |
| 405 | 请求方法不允许 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用（数据库连接失败等） |

### 错误响应格式

所有错误响应都遵循统一格式：

```json
{
  "code": 400,
  "message": "错误简要描述",
  "timestamp": "2025-10-24 10:30:45",
  "detail": "详细错误信息",
  "error": true
}
```

### 常见错误

#### 参数错误

```json
{
  "code": 400,
  "message": "参数错误",
  "detail": "股票代码不能为空",
  "error": true
}
```

#### 股票代码格式错误

```json
{
  "code": 400,
  "message": "参数错误",
  "detail": "股票代码格式错误，应为: SH.600519",
  "error": true
}
```

#### 日期格式错误

```json
{
  "code": 400,
  "message": "参数错误",
  "detail": "开始日期格式错误，应为: YYYY-MM-DD",
  "error": true
}
```

#### limit参数超限

```json
{
  "code": 400,
  "message": "参数错误",
  "detail": "limit参数不能超过10000，建议使用分页查询",
  "error": true
}
```

#### 数据库查询失败

```json
{
  "code": 500,
  "message": "查询失败",
  "detail": "数据库连接超时",
  "error": true
}
```

---

## 5. 数据模型

### 股票行情数据模型 (StockPriceData)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| trade_date | string | 交易日期（YYYY-MM-DD） |
| symbol | string | 股票代码（含市场前缀） |
| stock_name | string | 股票名称 |
| open_price | float | 开盘价 |
| high_price | float | 最高价 |
| low_price | float | 最低价 |
| close_price | float | 收盘价 |
| volume | int | 成交量（手） |
| turnover | float | 成交额（元） |
| price_change | float | 涨跌额 |
| price_change_pct | float | 涨跌幅（%） |
| premium_rate | float | 溢价率（%，仅基金） |
| market_code | string | 市场代码（SH/SZ/BJ） |

### 股票基础信息模型 (StockInfo)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| symbol | string | 股票代码（含市场前缀） |
| stock_name | string | 股票名称 |
| stock_code | string | 股票代码（不含市场前缀） |
| market_code | string | 市场代码（SH/SZ/BJ） |
| stock_type | string | 股票类型 |
| industry | string | 所属行业 |
| is_active | string | 是否活跃（Y/N） |
| last_sync_date | string | 最后同步日期 |
| created_at | string | 创建时间 |

### 本地JSON股票信息模型 (LocalStockInfo)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| ticker | string | 股票代码 |
| name | string | 股票名称 |
| symbol | string | 完整代码（含市场前缀） |
| exchange_code | string | 交易所代码 |
| exchange_name_cn | string | 交易所中文名称 |
| is_active | boolean | 是否活跃 |
| country_code | string | 国家代码 |
| currency_code | string | 货币代码 |
| first_fetch_time | string | 首次获取时间 |

---

## 6. 使用示例

### Python 示例

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000"

# 1. 健康检查
response = requests.get(f"{BASE_URL}/api/health")
print(response.json())

# 2. 查询股票行情
params = {
    "symbol": "SH.600519",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "limit": 10
}
response = requests.get(f"{BASE_URL}/api/stock-price/query", params=params)
data = response.json()
print(f"查询到 {data['count']} 条记录")

# 3. 获取股票基础信息
response = requests.get(f"{BASE_URL}/api/stock-price/info/SH.600519")
stock_info = response.json()
print(stock_info['data']['stock_name'])

# 4. 分页查询所有股票
def get_all_stocks(market_code='SH'):
    all_stocks = []
    limit = 100
    offset = 0
    
    while True:
        params = {
            'market_code': market_code,
            'limit': limit,
            'offset': offset
        }
        response = requests.get(f"{BASE_URL}/api/stock-price/list", params=params)
        data = response.json()
        
        stocks = data['data']
        all_stocks.extend(stocks)
        
        print(f"已获取: {len(all_stocks)}/{data['total']}")
        
        if len(stocks) < limit:
            break
        
        offset += limit
    
    return all_stocks

# 获取所有上海市场股票
sh_stocks = get_all_stocks('SH')
print(f"共获取 {len(sh_stocks)} 只上海市场股票")

# 5. 搜索股票
response = requests.get(f"{BASE_URL}/api/stock-info/local", params={'keyword': '茅台'})
print(response.json())
```

### JavaScript 示例

```javascript
// 基础URL
const BASE_URL = 'http://localhost:8000';

// 1. 健康检查
fetch(`${BASE_URL}/api/health`)
  .then(response => response.json())
  .then(data => console.log(data));

// 2. 查询股票行情
const queryStockPrice = async (symbol) => {
  const params = new URLSearchParams({
    symbol: symbol,
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    limit: 10
  });
  
  const response = await fetch(`${BASE_URL}/api/stock-price/query?${params}`);
  const data = await response.json();
  console.log(`查询到 ${data.count} 条记录`);
  return data;
};

// 3. 分页获取所有股票
const getAllStocks = async (marketCode = 'SH') => {
  const allStocks = [];
  let offset = 0;
  const limit = 100;
  
  while (true) {
    const params = new URLSearchParams({
      market_code: marketCode,
      limit: limit,
      offset: offset
    });
    
    const response = await fetch(`${BASE_URL}/api/stock-price/list?${params}`);
    const data = await response.json();
    
    allStocks.push(...data.data);
    console.log(`已获取: ${allStocks.length}/${data.total}`);
    
    if (data.data.length < limit) {
      break;
    }
    
    offset += limit;
  }
  
  return allStocks;
};

// 使用示例
queryStockPrice('SH.600519');
getAllStocks('SH').then(stocks => {
  console.log(`共获取 ${stocks.length} 只股票`);
});
```

### Bash/cURL 示例

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# 1. 健康检查
echo "=== 健康检查 ==="
curl -s "${BASE_URL}/api/health" | jq .

# 2. 查询股票行情
echo -e "\n=== 查询股票行情 ==="
curl -s "${BASE_URL}/api/stock-price/query?symbol=SH.600519&limit=5" | jq .

# 3. 获取股票信息
echo -e "\n=== 获取股票信息 ==="
curl -s "${BASE_URL}/api/stock-price/info/SH.600519" | jq .

# 4. 分页获取所有股票
echo -e "\n=== 分页获取股票 ==="
OFFSET=0
LIMIT=100
TOTAL=0

while true; do
  response=$(curl -s "${BASE_URL}/api/stock-price/list?limit=${LIMIT}&offset=${OFFSET}")
  count=$(echo "$response" | jq -r '.data | length')
  TOTAL=$(echo "$response" | jq -r '.total')
  
  echo "已获取: $((OFFSET + count))/${TOTAL}"
  
  if [ "$count" -lt "$LIMIT" ]; then
    break
  fi
  
  OFFSET=$((OFFSET + LIMIT))
done

echo "获取完成"

# 5. 搜索股票
echo -e "\n=== 搜索股票 ==="
curl -s "${BASE_URL}/api/stock-info/local?keyword=茅台" | jq .
```

---

## 7. 最佳实践

### 分页查询

对于大量数据，建议使用分页查询：

```python
def fetch_with_pagination(url, params, batch_size=100):
    """通用分页查询函数"""
    all_data = []
    offset = 0
    
    while True:
        params['limit'] = batch_size
        params['offset'] = offset
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if not data.get('data'):
            break
        
        all_data.extend(data['data'])
        
        # 如果返回的数据少于batch_size，说明已经到最后了
        if len(data['data']) < batch_size:
            break
        
        offset += batch_size
    
    return all_data
```

### 错误处理

```python
def safe_api_call(url, params=None):
    """安全的API调用，包含错误处理"""
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()  # 检查HTTP状态码
        
        data = response.json()
        
        # 检查业务错误
        if data.get('error'):
            print(f"业务错误: {data.get('message')} - {data.get('detail')}")
            return None
        
        return data
    
    except requests.exceptions.Timeout:
        print("请求超时")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    
    except ValueError:
        print("响应JSON解析失败")
        return None
```

### 性能优化

1. **使用合适的limit值**：根据实际需求设置，避免一次获取过多数据
2. **缓存常用数据**：对于股票列表等不常变化的数据，建议缓存
3. **并发请求**：在需要查询多个股票时，可以使用并发请求
4. **连接复用**：使用Session对象复用HTTP连接

```python
import requests
from concurrent.futures import ThreadPoolExecutor

session = requests.Session()

def query_stock(symbol):
    return session.get(
        f"{BASE_URL}/api/stock-price/info/{symbol}"
    ).json()

# 并发查询多个股票
symbols = ['SH.600519', 'SH.600036', 'SZ.000001']
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(query_stock, symbols))
```

---

## 8. 更新日志

### v1.0.0 (2025-10-24)

- ✅ 初始版本发布
- ✅ 提供股票行情查询接口
- ✅ 提供股票信息查询接口
- ✅ 提供系统健康检查接口
- ✅ 支持分页查询
- ✅ 添加参数验证和错误处理

---

## 9. 联系方式

如有问题或建议，请通过以下方式联系：

- **GitHub**: https://github.com/blaketairan/qtfund_project_3
- **Issues**: https://github.com/blaketairan/qtfund_project_3/issues

---

**文档版本**: v1.0  
**最后更新**: 2025-10-24  
**作者**: terrell

