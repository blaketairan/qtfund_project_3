"""
Momentum Score Calculation Example

计算股票的动量分，使用加权线性回归方法分析对数价格数据。
计算方法：
1. 获取历史价格数据
2. 对价格取自然对数
3. 生成线性递增权重（最近数据权重更高）
4. 计算加权线性回归
5. 计算年化收益率
6. 计算R²系数
7. 返回动量分 = 年化收益率 × R²

适用于在平台的自定义计算API中执行。
"""

# ============ Configuration ============
# 参数配置：用户可以根据需要修改这些值

DAYS = 250           # 分析的交易天数
WEIGHT_START = 1     # 旧数据的起始权重
WEIGHT_END = 2       # 新数据的结束权重（线性递增）
ANNUALIZATION = 250  # 年度交易天数（用于年化收益）

# ============ Error Handler ============
def handle_error(data_available, data_requested, error_type):
    """
    自定义错误处理器，用于处理数据不足的情况
    
    Args:
        data_available: 实际可用的数据点数
        data_requested: 请求的数据点数
        error_type: 错误类型
        
    Returns:
        None 表示返回null值
    """
    if error_type == 'insufficient_data':
        # 数据不足，返回None
        return None
    return None

# ============ Helper Functions ============

def weighted_linear_regression(x, y, weights):
    """
    计算加权线性回归
    
    使用加权最小二乘法：
    slope = sum(w*(x-x_mean)*(y-y_mean)) / sum(w*(x-x_mean)^2)
    intercept = y_mean - slope * x_mean
    
    Args:
        x: x值列表
        y: y值列表
        weights: 权重列表
        
    Returns:
        (slope, intercept) 元组
    """
    n = len(x)
    if n < 2:
        return 0, y[0] if len(y) > 0 and y[0] else 0
    
    # 计算加权均值
    weighted_sum_x = sum(w * xi for xi, w in zip(x, weights))
    weighted_sum_y = sum(w * yi for yi, w in zip(y, weights))
    weighted_sum = sum(weights)
    
    x_mean = weighted_sum_x / weighted_sum
    y_mean = weighted_sum_y / weighted_sum
    
    # 计算斜率
    numerator = sum(w * (xi - x_mean) * (yi - y_mean) for xi, yi, w in zip(x, y, weights))
    denominator = sum(w * (xi - x_mean) ** 2 for xi, w in zip(x, weights))
    
    slope = numerator / denominator if denominator != 0 else 0
    intercept = y_mean - slope * x_mean
    
    return slope, intercept

def weighted_r_squared(x, y, weights, slope, intercept):
    """
    计算加权R²系数
    
    R² = 1 - (sum(w*(y-predicted)^2) / sum(w*(y-y_mean)^2))
    
    Args:
        x: x值列表
        y: y值列表
        weights: 权重列表
        slope: 回归斜率
        intercept: 回归截距
        
    Returns:
        R² 系数
    """
    n = len(x)
    if n < 2:
        return 0
    
    # 计算加权均值
    weighted_sum_y = sum(w * yi for yi, w in zip(y, weights))
    weighted_sum = sum(weights)
    y_mean = weighted_sum_y / weighted_sum
    
    # 计算残差平方和与总平方和
    ss_res = sum(w * (yi - (slope * xi + intercept)) ** 2 for xi, yi, w in zip(x, y, weights))
    ss_tot = sum(w * (yi - y_mean) ** 2 for yi, w in zip(y, weights))
    
    return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

# ============ Main Calculation ============

def calculate_momentum(row):
    """
    计算股票的动量分
    
    算法步骤：
    1. 获取历史价格数据
    2. 对价格取对数
    3. 生成线性递增权重
    4. 计算加权线性回归
    5. 计算年化收益
    6. 计算R²
    7. 返回动量分 = 年化收益 × R²
    
    Args:
        row: 股票数据字典，包含symbol等字段
        
    Returns:
        动量分值（float或None）
    """
    # 获取历史数据
    history = get_history(row['symbol'], DAYS)
    
    # 检查最小数据要求（至少30天）
    if len(history) < 30:
        error_handler = globals().get('handle_error', None)
        if error_handler:
            return error_handler(len(history), DAYS, 'insufficient_data')
        return None
    
    # 提取收盘价并取对数
    prices = []
    for h in history:
        if h.get('close_price') and h['close_price'] > 0:
            prices.append(h['close_price'])
    
    if len(prices) < 30:
        return None
    
    # 对数变换
    y = [math.log(p) for p in prices]
    n = len(y)
    x = list(range(n))
    
    # 生成线性递增权重
    weights = []
    for i in range(n):
        if n > 1:
            weight = WEIGHT_START + (WEIGHT_END - WEIGHT_START) * i / (n - 1)
        else:
            weight = 1
        weights.append(weight)
    
    # 计算加权线性回归
    slope, intercept = weighted_linear_regression(x, y, weights)
    
    # 计算年化收益率: (e^slope)^250 - 1
    annualized_return = (math.exp(slope) ** ANNUALIZATION) - 1
    
    # 计算加权R²
    r_squared = weighted_r_squared(x, y, weights, slope, intercept)
    
    # 最终动量分
    momentum_score = annualized_return * r_squared
    
    return momentum_score

# ============ Execute Calculation ============
# 执行计算并将结果赋值给result变量

momentum = calculate_momentum(row)
result = momentum

