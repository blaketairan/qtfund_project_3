-- 添加 is_etf 列到 stock_info 表
-- ETF Support Feature (006-etf-support)

-- 添加 is_etf 列
ALTER TABLE stock_info 
ADD COLUMN IF NOT EXISTS is_etf CHAR(1) DEFAULT 'N' NOT NULL;

-- 添加注释
COMMENT ON COLUMN stock_info.is_etf IS '是否ETF标识：Y-ETF, N-股票';

-- 基于股票名称模式填充数据
UPDATE stock_info 
SET is_etf = 'Y' 
WHERE stock_name LIKE '%ETF%' 
   OR stock_name LIKE '%etf%'
   OR stock_name LIKE '%基金%';

-- 验证数据
-- SELECT COUNT(*) as total_instruments FROM stock_info;
-- SELECT COUNT(*) as total_etfs FROM stock_info WHERE is_etf = 'Y';
-- SELECT COUNT(*) as total_stocks FROM stock_info WHERE is_etf = 'N';

