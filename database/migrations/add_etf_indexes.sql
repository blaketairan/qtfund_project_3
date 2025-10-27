-- 添加 ETF 相关索引
-- ETF Support Feature (006-etf-support)

-- 添加 symbol 和 is_etf 的复合索引
CREATE INDEX IF NOT EXISTS idx_symbol_etf ON stock_info(symbol, is_etf);

-- 添加 is_etf 和 is_active 的复合索引（用于常见查询模式）
CREATE INDEX IF NOT EXISTS idx_is_etf_active ON stock_info(is_etf, is_active);

-- 添加注释
COMMENT ON INDEX idx_symbol_etf IS 'ETF筛选查询优化索引';
COMMENT ON INDEX idx_is_etf_active IS 'ETF筛选与活跃状态查询优化索引';

