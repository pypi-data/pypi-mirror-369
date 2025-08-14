-- JetTask PostgreSQL Schema
-- 用于存储任务队列信息和执行结果

-- 创建任务表
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(255) PRIMARY KEY,  -- Redis Stream的事件ID
    queue_name VARCHAR(255) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    task_data JSONB,  -- 任务的原始数据
    priority INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    max_retry INTEGER DEFAULT 3,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, running, success, failed, timeout
    result JSONB,  -- 执行结果
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    worker_id VARCHAR(255),
    execution_time DOUBLE PRECISION,  -- 任务执行时间（秒）
    duration DOUBLE PRECISION,  -- 任务总持续时间（秒）
    metadata JSONB  -- 额外的元数据
);

-- 创建索引以优化查询
CREATE INDEX IF NOT EXISTS idx_tasks_queue_name ON tasks(queue_name);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
-- 删除不常用的索引
-- CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
-- CREATE INDEX IF NOT EXISTS idx_tasks_worker_id ON tasks(worker_id);
-- CREATE INDEX IF NOT EXISTS idx_tasks_status_created ON tasks(status, created_at);

-- 创建队列统计表
CREATE TABLE IF NOT EXISTS queue_stats (
    id SERIAL PRIMARY KEY,
    queue_name VARCHAR(255) NOT NULL,
    total_tasks INTEGER DEFAULT 0,
    pending_tasks INTEGER DEFAULT 0,
    running_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    failed_tasks INTEGER DEFAULT 0,
    avg_processing_time INTERVAL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(queue_name)
);

-- 创建worker信息表
CREATE TABLE IF NOT EXISTS workers (
    id VARCHAR(255) PRIMARY KEY,
    hostname VARCHAR(255),
    process_id INTEGER,
    queues TEXT[],  -- 订阅的队列列表
    status VARCHAR(50) DEFAULT 'active',  -- active, inactive, dead
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- 创建更新统计的触发器函数
CREATE OR REPLACE FUNCTION update_queue_stats() RETURNS TRIGGER AS $$
BEGIN
    -- 更新队列统计信息
    INSERT INTO queue_stats (queue_name, total_tasks, pending_tasks, running_tasks, completed_tasks, failed_tasks)
    VALUES (
        COALESCE(NEW.queue_name, OLD.queue_name),
        1,
        CASE WHEN NEW.status = 'pending' THEN 1 ELSE 0 END,
        CASE WHEN NEW.status = 'running' THEN 1 ELSE 0 END,
        CASE WHEN NEW.status = 'success' THEN 1 ELSE 0 END,
        CASE WHEN NEW.status = 'failed' THEN 1 ELSE 0 END
    )
    ON CONFLICT (queue_name) DO UPDATE SET
        total_tasks = queue_stats.total_tasks + 1,
        pending_tasks = queue_stats.pending_tasks + 
            CASE 
                WHEN NEW.status = 'pending' AND OLD.status != 'pending' THEN 1
                WHEN NEW.status != 'pending' AND OLD.status = 'pending' THEN -1
                ELSE 0
            END,
        running_tasks = queue_stats.running_tasks + 
            CASE 
                WHEN NEW.status = 'running' AND OLD.status != 'running' THEN 1
                WHEN NEW.status != 'running' AND OLD.status = 'running' THEN -1
                ELSE 0
            END,
        completed_tasks = queue_stats.completed_tasks + 
            CASE WHEN NEW.status = 'success' AND OLD.status != 'success' THEN 1 ELSE 0 END,
        failed_tasks = queue_stats.failed_tasks + 
            CASE WHEN NEW.status = 'failed' AND OLD.status != 'failed' THEN 1 ELSE 0 END,
        last_updated = CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER update_queue_stats_trigger
AFTER INSERT OR UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION update_queue_stats();

-- 升级脚本：为现有表添加新字段（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name = 'tasks' AND column_name = 'execution_time') THEN
        ALTER TABLE tasks ADD COLUMN execution_time DOUBLE PRECISION;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name = 'tasks' AND column_name = 'duration') THEN
        ALTER TABLE tasks ADD COLUMN duration DOUBLE PRECISION;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name = 'tasks' AND column_name = 'last_checked_at') THEN
        ALTER TABLE tasks ADD COLUMN last_checked_at TIMESTAMP WITH TIME ZONE;
    END IF;
    
    -- 添加 next_sync_time 字段，默认值为 epoch 时间（1970-01-01）
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name = 'tasks' AND column_name = 'next_sync_time') THEN
        ALTER TABLE tasks ADD COLUMN next_sync_time DOUBLE PRECISION DEFAULT 0;
        -- 更新现有记录的默认值
        UPDATE tasks SET next_sync_time = 0 WHERE next_sync_time IS NULL;
    END IF;
    
    -- 添加同步检查次数，用于实现退避策略
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name = 'tasks' AND column_name = 'sync_check_count') THEN
        ALTER TABLE tasks ADD COLUMN sync_check_count INTEGER DEFAULT 0;
    END IF;
    
    -- sync_node_id 已经不再使用，删除它
    IF EXISTS (SELECT 1 FROM information_schema.columns 
              WHERE table_name = 'tasks' AND column_name = 'sync_node_id') THEN
        ALTER TABLE tasks DROP COLUMN sync_node_id;
    END IF;
    
    -- 如果 last_checked_at 存在，可以删除它（迁移到 next_sync_time）
    IF EXISTS (SELECT 1 FROM information_schema.columns 
              WHERE table_name = 'tasks' AND column_name = 'last_checked_at') THEN
        -- 迁移数据：将已有的 last_checked_at 转换为 next_sync_time（时间戳格式）
        UPDATE tasks 
        SET next_sync_time = EXTRACT(EPOCH FROM (last_checked_at + INTERVAL '5 seconds'))
        WHERE last_checked_at IS NOT NULL AND (next_sync_time IS NULL OR next_sync_time = 0);
        
        -- 删除旧列
        ALTER TABLE tasks DROP COLUMN IF EXISTS last_checked_at;
    END IF;
END$$;

-- 删除旧的不再需要的索引
DROP INDEX IF EXISTS idx_tasks_status_last_checked;
DROP INDEX IF EXISTS idx_tasks_created_at;
DROP INDEX IF EXISTS idx_tasks_worker_id;
DROP INDEX IF EXISTS idx_tasks_status_created;
DROP INDEX IF EXISTS idx_tasks_hash_partition;
DROP INDEX IF EXISTS idx_tasks_status_next_sync;
DROP INDEX IF EXISTS idx_tasks_new_tasks;

-- 主查询索引：用于基于ID分区的查询
-- 这个索引加速 MOD(CAST(SPLIT_PART(id, '-', 2) AS INTEGER), N) 的计算
CREATE INDEX IF NOT EXISTS idx_tasks_id_partition
ON tasks(MOD(CAST(SPLIT_PART(id, '-', 2) AS INTEGER), 10), next_sync_time, id, sync_check_count)
WHERE status IN ('pending', 'running');

-- 覆盖索引：包含查询需要的所有列，避免回表
CREATE INDEX IF NOT EXISTS idx_tasks_covering_sync
ON tasks(next_sync_time, status, id, sync_check_count)
WHERE status IN ('pending', 'running');