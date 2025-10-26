-- 创建自定义脚本存储表
-- 用于保存用户创建的计算脚本供重复使用

CREATE TABLE IF NOT EXISTS custom_scripts (
    -- 主键
    id SERIAL PRIMARY KEY,
    
    -- 脚本名称（用户自定义）
    name VARCHAR(100) NOT NULL,
    
    -- 脚本描述（可选）
    description TEXT,
    
    -- Python脚本代码
    code TEXT NOT NULL,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_custom_scripts_name ON custom_scripts(name);
CREATE INDEX IF NOT EXISTS idx_custom_scripts_created_at ON custom_scripts(created_at);

-- 添加注释
COMMENT ON TABLE custom_scripts IS '存储用户自定义Python计算脚本';
COMMENT ON COLUMN custom_scripts.id IS '主键ID';
COMMENT ON COLUMN custom_scripts.name IS '脚本名称';
COMMENT ON COLUMN custom_scripts.description IS '脚本描述';
COMMENT ON COLUMN custom_scripts.code IS 'Python脚本代码';
COMMENT ON COLUMN custom_scripts.created_at IS '创建时间';
COMMENT ON COLUMN custom_scripts.updated_at IS '更新时间';

