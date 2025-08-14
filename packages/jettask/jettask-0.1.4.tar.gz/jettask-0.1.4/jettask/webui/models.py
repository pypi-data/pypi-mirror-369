"""SQLAlchemy models for JetTask WebUI database."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, JSON, 
    ARRAY, UniqueConstraint, Index, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()


class Task(Base):
    """任务表模型"""
    __tablename__ = 'tasks'
    
    id = Column(String(255), primary_key=True)  # Redis Stream的事件ID
    queue_name = Column(String(255), nullable=False)
    task_name = Column(String(255), nullable=False)
    task_data = Column(JSONB)  # 任务的原始数据
    priority = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    max_retry = Column(Integer, default=3)
    status = Column(String(50), default='pending')  # pending, running, success, failed, timeout
    result = Column(JSONB)  # 执行结果
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    worker_id = Column(String(255))
    execution_time = Column(Float)  # 任务执行时间（秒）
    duration = Column(Float)  # 任务总持续时间（秒）
    task_metadata = Column('metadata', JSONB)  # 额外的元数据，在数据库中仍叫metadata
    next_sync_time = Column(Float, default=0)  # 下次同步时间的时间戳
    sync_check_count = Column(Integer, default=0)  # 同步检查次数
    
    __table_args__ = (
        Index('idx_tasks_queue_name', 'queue_name'),
        Index('idx_tasks_status', 'status'),
        # 分区查询索引
        Index(
            'idx_tasks_id_partition',
            func.mod(func.cast(func.split_part(id, '-', 2), Integer), 10),
            'next_sync_time', 'id', 'sync_check_count',
            postgresql_where=(status.in_(['pending', 'running']))
        ),
        # 覆盖索引
        Index(
            'idx_tasks_covering_sync',
            'next_sync_time', 'status', 'id', 'sync_check_count',
            postgresql_where=(status.in_(['pending', 'running']))
        ),
    )


class QueueStats(Base):
    """队列统计表模型"""
    __tablename__ = 'queue_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    queue_name = Column(String(255), nullable=False, unique=True)
    total_tasks = Column(Integer, default=0)
    pending_tasks = Column(Integer, default=0)
    running_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    avg_processing_time = Column(String)  # PostgreSQL INTERVAL type stored as string
    last_updated = Column(DateTime(timezone=True), default=func.current_timestamp())


class Worker(Base):
    """Worker信息表模型"""
    __tablename__ = 'workers'
    
    id = Column(String(255), primary_key=True)
    hostname = Column(String(255))
    process_id = Column(Integer)
    queues = Column(ARRAY(Text))  # 订阅的队列列表
    status = Column(String(50), default='active')  # active, inactive, dead
    last_heartbeat = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    worker_metadata = Column('metadata', JSONB)  # 元数据，在数据库中仍叫metadata