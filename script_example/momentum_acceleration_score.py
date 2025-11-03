"""
动量加速度评分脚本

基于滑动窗口计算每日动量分数，并通过二阶导数评估动量加速度。
最终返回最新的动量分数。

使用方法：
1. 通过 POST /api/custom-calculations/scripts 上传此脚本
2. 在 GET /api/stock-price/list?script_ids=[script_id] 中调用

返回值：当前动量分数（考虑加速度的动量评分）

注意：math 模块已由平台提供，无需 import
"""

# math 模块已在沙箱环境中提供，无需导入

# ============ 配置参数 ============
MOMENTUM_DAY = 34        # 每个滑动窗口的天数
TOTAL_DAYS = 68         # 获取历史数据总天数（MOMENTUM_DAY * 2）
MIN_DATA_POINTS = 34     # 最少数据点要求

# ============ 辅助函数 ============

def calculate_momentum_score(prices):
    """
    计算单个窗口的动量分数
    
    Args:
        prices: 收盘价列表
        
    Returns:
        动量分数（年化收益率 × R²）
    """
    if len(prices) < MIN_DATA_POINTS:
        return None
    
    # 对价格取对数
    y = [math.log(p) for p in prices if p > 0]
    if len(y) < MIN_DATA_POINTS:
        return None
    
    n = len(y)
    x = list(range(n))
    
    # 计算线性回归（y = slope * x + intercept）
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    
    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    denominator = sum((xi - x_mean) ** 2 for xi in x)
    
    if denominator == 0:
        return None
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    # 计算年化收益率: (e^slope)^250 - 1
    annualized_return = (math.exp(slope) ** 250) - 1
    
    # 计算R²
    ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    # 动量分数 = 年化收益率 × R²
    momentum_score = annualized_return * r_squared
    
    return momentum_score


def calculate_second_derivative(scores):
    """
    计算分数序列的二阶导数（加速度）
    
    使用二阶多项式拟合: y = ax² + bx + c
    二阶导数 = 2a
    
    Args:
        scores: 分数列表
        
    Returns:
        二阶导数值
    """
    if len(scores) < 3:
        return 0
    
    n = len(scores)
    x = list(range(n))
    
    # 简化的二阶多项式拟合
    # 使用最小二乘法计算系数 a, b, c
    # 这里简化为使用三点法估算二阶导数
    
    # 使用最后三个点估算二阶导数
    if n >= 3:
        # 二阶差分近似二阶导数
        # f''(x) ≈ (f(x+h) - 2f(x) + f(x-h)) / h²
        # 取 h=1
        second_diff = scores[-1] - 2 * scores[-2] + scores[-3]
        return second_diff
    
    return 0


def handle_error(data_available, data_requested, error_type):
    """
    错误处理器
    
    Args:
        data_available: 实际可用数据点数
        data_requested: 请求的数据点数
        error_type: 错误类型
        
    Returns:
        None 表示返回 null
    """
    if error_type == 'insufficient_data':
        return None
    return None


# ============ 主计算逻辑 ============

def calculate_momentum_acceleration(row):
    """
    计算动量加速度评分
    
    算法步骤：
    1. 获取 TOTAL_DAYS 天历史数据
    2. 使用滑动窗口（MOMENTUM_DAY）计算每日动量分数
    3. 对每日分数序列计算二阶导数（加速度）
    4. 返回最新的动量分数
    
    Args:
        row: 股票/ETF数据字典
        
    Returns:
        动量加速度评分（float 或 None）
    """
    # 获取历史数据
    history = get_history(row['symbol'], TOTAL_DAYS)
    
    # 检查数据充分性
    if len(history) < MOMENTUM_DAY + MIN_DATA_POINTS:
        error_handler = globals().get('handle_error', None)
        if error_handler:
            return error_handler(len(history), TOTAL_DAYS, 'insufficient_data')
        return None
    
    # 提取收盘价
    prices = []
    for h in history:
        if h.get('close_price') and h['close_price'] > 0:
            prices.append(h['close_price'])
    
    if len(prices) < MOMENTUM_DAY + MIN_DATA_POINTS:
        return None
    
    # 计算每日动量分数（滑动窗口）
    daily_scores = []
    for day_idx in range(MOMENTUM_DAY, len(prices)):
        # 取当前时间点往前 MOMENTUM_DAY 天的数据
        window_prices = prices[day_idx - MOMENTUM_DAY:day_idx]
        
        # 计算该窗口的动量分数
        score = calculate_momentum_score(window_prices)
        
        if score is not None:
            daily_scores.append(score)
    
    # 检查每日分数是否充足
    if len(daily_scores) < 3:
        return None
    
    # 计算二阶导数（加速度）
    second_deriv = calculate_second_derivative(daily_scores)
    
    # 返回最新的动量分数（可选：加入加速度权重）
    current_score = daily_scores[-1]
    
    # 方案1：直接返回当前分数
    return current_score
    
    # 方案2：考虑加速度的加权分数（取消注释使用）
    # acceleration_weight = 0.2  # 加速度权重
    # weighted_score = current_score * (1 + acceleration_weight * second_deriv)
    # return weighted_score


# ============ 执行 ============
momentum_score = calculate_momentum_acceleration(row)
result = momentum_score

