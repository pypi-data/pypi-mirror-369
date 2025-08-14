import asyncio
import json
import logging
import os
import socket
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from collections import defaultdict

import redis.asyncio as redis
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, update, insert, and_, or_

from jettask.webui.config import PostgreSQLConfig, RedisConfig
from jettask.webui.models import Base, Task

logger = logging.getLogger(__name__)


class PostgreSQLConsumer:
    """PostgreSQL消费者，从Redis队列消费任务并持久化到PostgreSQL"""
    
    def _get_next_sync_time(self, sync_check_count: int) -> float:
        """计算下次同步时间的时间戳（指数退避）"""
        # 指数退避：1, 2, 4, 8, 16, 32, 64 秒
        delay = min(2 ** sync_check_count, 64)
        return time.time() + delay
    
    def __init__(self, pg_config: PostgreSQLConfig, redis_config: RedisConfig, prefix: str = "jettask", node_id: str = None):
        self.pg_config = pg_config
        self.redis_config = redis_config
        self.prefix = prefix
        self.redis_client: Optional[Redis] = None
        self.async_engine = None
        self.AsyncSessionLocal = None
        self.consumer_group = f"{prefix}_pg_consumer"
        self.consumer_id = f"pg_consumer_{int(time.time()*1000)}"  # 使用时间戳确保唯一性
        # 节点标识，用于分布式环境
        import socket
        self.node_id = node_id or f"{socket.gethostname()}_{os.getpid()}"
        self._running = False
        self._tasks = []
        self._known_queues = set()  # 缓存已知的队列
        self._consecutive_errors = defaultdict(int)  # 记录每个队列的连续错误次数
        # 动态批次大小
        self.batch_size = 1000  # 初始批次大小
        self.min_batch_size = 100
        self.max_batch_size = 1000
        # 分区信息
        self.partition_info = {
            'min_id': None,
            'max_id': None,
            'id_ranges': [],  # [(start, end), ...]
            'active_nodes': 1,
            'node_index': 0,
            'last_update': 0,
            'is_last_node': False,  # 是否是最后一个节点
            'grace_period': True,  # 宽限期标志
            'grace_start': 0  # 宽限期开始时间
        }
        self.pubsub = None  # Pub/Sub客户端
        
    async def start(self):
        """启动消费者"""
        logger.info(f"Starting PostgreSQL consumer on node: {self.node_id}")
        
        # 使用 Redis 协调后不需要启动延迟
        
        # 连接Redis
        self.redis_client = await redis.Redis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            db=self.redis_config.db,
            password=self.redis_config.password,
            decode_responses=False
        )
        
        # 创建SQLAlchemy异步引擎 - 优化配置
        # 将 DSN 转换为 SQLAlchemy 格式
        if self.pg_config.dsn.startswith('postgresql://'):
            dsn = self.pg_config.dsn.replace('postgresql://', 'postgresql+psycopg://', 1)
        else:
            dsn = self.pg_config.dsn
            
        self.async_engine = create_async_engine(
            dsn,
            pool_size=20,      # 连接池大小
            max_overflow=10,   # 最大溢出连接数
            pool_pre_ping=True,  # 连接前检查
            pool_recycle=300,    # 5分钟回收连接
            echo=False
        )
        
        # 创建异步会话工厂
        self.AsyncSessionLocal = sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # 初始化数据库架构
        await self._init_database()
        
        self._running = True
        
        # 创建Pub/Sub客户端用于节点通知
        self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe(f"{self.prefix}:NODE_EVENTS")
        
        # 启动消费任务
        self._tasks = [
            asyncio.create_task(self._consume_queues()),
            asyncio.create_task(self._update_task_status()),
            asyncio.create_task(self._partition_coordinator()),  # 分区协调器
            asyncio.create_task(self._database_maintenance()),  # 数据库维护任务
            asyncio.create_task(self._node_event_listener())    # 节点事件监听器
        ]
        
        logger.info("PostgreSQL consumer started successfully")
        
    async def stop(self):
        """停止消费者"""
        logger.info("Stopping PostgreSQL consumer...")
        self._running = False
        
        # 发布节点离开事件
        try:
            await self.redis_client.publish(
                f"{self.prefix}:NODE_EVENTS", 
                json.dumps({"event": "node_leave", "node_id": self.node_id})
            )
            # 删除心跳键
            await self.redis_client.delete(f"{self.prefix}:NODE:{self.node_id}")
            logger.info(f"Published node leave event for {self.node_id}")
        except Exception as e:
            logger.error(f"Error publishing node leave event: {e}")
        
        # 取消所有任务
        for task in self._tasks:
            task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # 关闭连接
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
            
        if self.redis_client:
            await self.redis_client.close()
        
        if self.async_engine:
            await self.async_engine.dispose()
            
        logger.info("PostgreSQL consumer stopped")
        
    async def _init_database(self):
        """初始化数据库架构"""
        schema_path = "/home/yuyang/easy-task/jettask/webui/schema.sql"
        try:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            async with self.AsyncSessionLocal() as session:
                await session.execute(text(schema_sql))
                await session.commit()
                logger.info("Database schema initialized")
        except FileNotFoundError:
            logger.warning(f"Schema file not found at {schema_path}, skipping initialization")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            
    async def _discover_queues(self):
        """定期发现新队列"""
        while self._running:
            try:
                pattern = f"{self.prefix}:QUEUE:*"
                new_queues = set()
                
                async for key in self.redis_client.scan_iter(match=pattern, count=100):
                    queue_name = key.decode('utf-8').split(":")[-1]
                    new_queues.add(queue_name)
                
                # 为新发现的队列创建消费者组
                for queue in new_queues - self._known_queues:
                    stream_key = f"{self.prefix}:QUEUE:{queue}"
                    try:
                        await self.redis_client.xgroup_create(
                            stream_key, self.consumer_group, id='0', mkstream=True
                        )
                        logger.info(f"Created consumer group for new queue: {queue}")
                    except redis.ResponseError:
                        # 消费者组已存在
                        pass
                
                self._known_queues = new_queues
                
                # 每30秒发现一次新队列
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error discovering queues: {e}")
                await asyncio.sleep(10)
    
    async def _consume_queue(self, queue_name: str):
        """消费单个队列的任务"""
        stream_key = f"{self.prefix}:QUEUE:{queue_name}"
        check_backlog = True  # 是否检查历史消息
        lastid = "0-0"  # 初始ID
        
        while self._running and queue_name in self._known_queues:
            try:
                # 决定从哪里开始读取
                if check_backlog:
                    myid = lastid
                else:
                    myid = ">"
                
                # 读取消息
                messages = await self.redis_client.xreadgroup(
                    self.consumer_group,
                    self.consumer_id,
                    {stream_key: myid},
                    count=1000,  # 每次最多读取50条
                    block=1000 if not check_backlog else 0  # 有历史消息时不阻塞，否则阻塞1秒
                )
                
                # 检查是否还有更多历史消息
                if not messages or (messages and len(messages[0][1]) == 0):
                    check_backlog = False
                    continue
                
                # 处理消息
                if messages:
                    await self._process_messages(messages)
                    # 重置错误计数
                    self._consecutive_errors[queue_name] = 0
                    
                    # 更新lastid为最后一条消息的ID
                    if messages[0] and messages[0][1]:
                        lastid = messages[0][1][-1][0].decode('utf-8') if isinstance(messages[0][1][-1][0], bytes) else messages[0][1][-1][0]
                        
                        # 如果读取到了完整批次，说明可能还有更多历史消息
                        if len(messages[0][1]) >= 50:
                            check_backlog = True
                        else:
                            check_backlog = False
                    
            except redis.ResponseError as e:
                if "NOGROUP" in str(e):
                    # 消费者组不存在，尝试创建
                    try:
                        await self.redis_client.xgroup_create(
                            stream_key, self.consumer_group, id='0', mkstream=True
                        )
                        logger.info(f"Recreated consumer group for queue: {queue_name}")
                        # 重置状态，从头开始读取
                        check_backlog = True
                        lastid = "0-0"
                    except:
                        pass
                else:
                    logger.error(f"Redis error for queue {queue_name}: {e}")
                    self._consecutive_errors[queue_name] += 1
                    
                # 如果连续错误太多，暂时跳过这个队列
                if self._consecutive_errors[queue_name] > 10:
                    logger.warning(f"Too many errors for queue {queue_name}, will retry later")
                    await asyncio.sleep(30)
                    self._consecutive_errors[queue_name] = 0
                # else:
                #     await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error consuming queue {queue_name}: {e}", exc_info=True)
                self._consecutive_errors[queue_name] += 1
                await asyncio.sleep(1)
    
    async def _consume_queues(self):
        """启动所有队列的消费任务"""
        # 启动队列发现任务
        discover_task = asyncio.create_task(self._discover_queues())
        
        # 为每个队列创建独立的消费任务
        queue_tasks = {}
        
        while self._running:
            try:
                # 为新队列创建任务
                for queue in self._known_queues:
                    if queue not in queue_tasks or queue_tasks[queue].done():
                        queue_tasks[queue] = asyncio.create_task(self._consume_queue(queue))
                        logger.info(f"Started consumer task for queue: {queue}")
                
                # 清理已完成或已移除的队列任务
                for queue in list(queue_tasks.keys()):
                    if queue not in self._known_queues:
                        queue_tasks[queue].cancel()
                        del queue_tasks[queue]
                        logger.info(f"Stopped consumer task for removed queue: {queue}")
                
                # 等待一段时间再检查
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in consume_queues manager: {e}")
                await asyncio.sleep(5)
        
        # 清理所有任务
        discover_task.cancel()
        for task in queue_tasks.values():
            task.cancel()
        
        await asyncio.gather(discover_task, *queue_tasks.values(), return_exceptions=True)
                
    async def _process_messages(self, messages: List):
        """处理消息并保存到PostgreSQL"""
        tasks_to_insert = []
        
        for stream_key, stream_messages in messages:
            if not stream_messages:
                logger.debug(f"No messages in stream {stream_key}")
                continue
                
            # 处理stream_key
            if isinstance(stream_key, bytes):
                stream_key_str = stream_key.decode('utf-8')
            else:
                stream_key_str = stream_key
                
            queue_name = stream_key_str.split(":")[-1]
            
            for msg_id, data in stream_messages:
                try:
                    # 跳过空消息
                    if not msg_id or not data:
                        logger.warning(f"Skipping empty message in queue {queue_name}")
                        continue
                        
                    # 解析任务数据
                    task_data = {
                        k.decode('utf-8') if isinstance(k, bytes) else k: 
                        v.decode('utf-8') if isinstance(v, bytes) else v
                        for k, v in data.items()
                    }
                    
                    # 处理消息ID
                    msg_id_str = msg_id.decode('utf-8') if isinstance(msg_id, bytes) else str(msg_id)
                    
                    # 获取task_name，优先使用name字段
                    task_name = task_data.get('name', task_data.get('task', 'unknown'))
                    logger.debug(f"Task {msg_id_str} name: {task_name}, available fields: {list(task_data.keys())}")
                    
                    # 提取trigger_time时间戳并转换为UTC时间作为created_at
                    created_at = None
                    if 'trigger_time' in task_data:
                        try:
                            timestamp = float(task_data['trigger_time'])
                            # 将时间戳转换为UTC datetime对象
                            created_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid trigger_time value: {task_data['trigger_time']}")
                    
                    # 准备插入数据
                    task_info = {
                        'id': msg_id_str,
                        'queue_name': queue_name,
                        'task_name': task_name,
                        'task_data': json.dumps(task_data),
                        'priority': int(task_data.get('priority', 0)),
                        'retry_count': int(task_data.get('retry', 0)),
                        'max_retry': int(task_data.get('max_retry', 3)),
                        'status': 'pending',
                        'metadata': json.dumps(task_data.get('metadata', {})),
                        'created_at': created_at  # UTC datetime对象
                    }
                    logger.info(f'准备插入数据: {created_at=}')
                    tasks_to_insert.append(task_info)
                    
                    # 确认消息
                    await self.redis_client.xack(stream_key, self.consumer_group, msg_id)
                    
                except Exception as e:
                    logger.error(f"Error processing message {msg_id}: {e}")
                    
        # 批量插入到PostgreSQL
        if tasks_to_insert:
            await self._insert_tasks(tasks_to_insert)
            
    async def _insert_tasks(self, tasks: List[Dict[str, Any]]):
        """批量插入任务到PostgreSQL"""
        if not tasks:
            return
            
        try:
            async with self.AsyncSessionLocal() as session:
                # 使用原生SQL执行批量插入（SQLAlchemy的批量插入对于UPSERT比较复杂）
                query = text("""
                    INSERT INTO tasks (id, queue_name, task_name, task_data, priority, 
                                     retry_count, max_retry, status, metadata, created_at)
                    VALUES (:id, :queue_name, :task_name, CAST(:task_data AS jsonb), :priority, 
                           :retry_count, :max_retry, :status, CAST(:metadata AS jsonb), :created_at)
                    ON CONFLICT (id) DO UPDATE SET
                        task_name = EXCLUDED.task_name,
                        retry_count = EXCLUDED.retry_count,
                        metadata = EXCLUDED.metadata
                """)
                
                # 准备数据
                for task in tasks:
                    await session.execute(query, {
                        'id': task['id'],
                        'queue_name': task['queue_name'],
                        'task_name': task['task_name'],
                        'task_data': task['task_data'],  # 已经是JSON字符串
                        'priority': task['priority'],
                        'retry_count': task['retry_count'],
                        'max_retry': task['max_retry'],
                        'status': task['status'],
                        'metadata': task['metadata'],  # 已经是JSON字符串
                        'created_at': task.get('created_at')
                    })
                
                await session.commit()
                logger.info(f"Inserted {len(tasks)} tasks to PostgreSQL")
                
                # 调试：检查第一个任务的数据
                if tasks:
                    logger.debug(f"First task data: id={tasks[0]['id']}, name={tasks[0]['task_name']}")
                
        except Exception as e:
            logger.error(f"Error inserting tasks to PostgreSQL: {e}")
            
    async def _update_task_status(self):
        """定期更新任务状态"""
        # 查询结果缓存
        query_cache = {
            'tasks': [],
            'last_update': 0,
            'cache_ttl': 1.0  # 1秒缓存
        }
        
        while self._running:
            try:
                
                
                # 1. 等待分区信息就绪
                if self.partition_info['active_nodes'] == 0:
                    logger.info("Waiting for partition info...")
                    await asyncio.sleep(2)
                    continue
                
                # 2. 宽限期处理 - 重新上线的节点暂不处理任务
                if self.partition_info.get('grace_period', False):
                    grace_elapsed = time.time() - self.partition_info.get('grace_start', 0)
                    if grace_elapsed < 10:  # 10秒宽限期
                        logger.info(f"Node in grace period, waiting... ({10 - grace_elapsed:.1f}s remaining)")
                        await asyncio.sleep(1)
                        continue
                    else:
                        # 宽限期结束
                        self.partition_info['grace_period'] = False
                        logger.info("Grace period ended, resuming normal operation")
                
                # 2. 从PostgreSQL查询分配给当前节点的任务
                start_time = time.time()
                
                # 检查缓存是否有效
                if (query_cache['tasks'] and 
                    time.time() - query_cache['last_update'] < query_cache['cache_ttl']):
                    # 使用缓存的任务
                    unfinished_tasks = query_cache['tasks']
                    logger.debug(f"Using cached tasks: {len(unfinished_tasks)} tasks")
                else:
                    async with self.AsyncSessionLocal() as session:
                        # 设置语句超时
                        await session.execute(text("SET statement_timeout = '5000'"))  # 5秒超时
                        
                        # 使用更简单的分区策略：基于ID字符比较
                        # 将ID空间平均分成N份
                        if self.partition_info['is_last_node']:
                            # 最后一个节点：处理自己的分区 + 所有新任务
                            # 基于ID中'-'后面的数字进行分区
                            query = text("""
                                SELECT id, sync_check_count 
                                FROM tasks 
                                WHERE status IN ('pending', 'running')
                                  AND next_sync_time <= :current_time
                                  AND (
                                    -- 属于当前节点的分区（基于-后面的数字取模）
                                    MOD(CAST(SPLIT_PART(id, '-', 2) AS INTEGER), :active_nodes) = :node_index
                                    -- 或者是新任务（ID大于max_id）
                                    OR id > :max_id
                                  )
                                ORDER BY next_sync_time
                                LIMIT :batch_size
                                """)
                            result = await session.execute(query, {
                                'batch_size': self.batch_size,
                                'current_time': time.time(),
                                'active_nodes': self.partition_info['active_nodes'],
                                'node_index': self.partition_info['node_index'],
                                'max_id': self.partition_info['max_id'] or ''
                            })
                            unfinished_tasks = result.mappings().all()
                        else:
                            # 其他节点：只处理自己的分区
                            # 基于ID中'-'后面的数字进行分区
                            query = text("""
                                SELECT id, sync_check_count 
                                FROM tasks 
                                WHERE status IN ('pending', 'running')
                                  AND next_sync_time <= :current_time
                                  AND MOD(CAST(SPLIT_PART(id, '-', 2) AS INTEGER), :active_nodes) = :node_index
                                ORDER BY next_sync_time
                                LIMIT :batch_size
                                """)
                            result = await session.execute(query, {
                                'batch_size': self.batch_size,
                                'current_time': time.time(),
                                'active_nodes': self.partition_info['active_nodes'],
                                'node_index': self.partition_info['node_index']
                            })
                            unfinished_tasks = result.mappings().all()
                        
                        # 更新缓存
                        query_cache['tasks'] = unfinished_tasks
                        query_cache['last_update'] = time.time()
                    
                    
                if not unfinished_tasks:
                    continue
                    
                query_time = time.time() - start_time
                logger.info(f"Node {self.partition_info['node_index']}/{self.partition_info['active_nodes']}: "
                          f"Found {len(unfinished_tasks)} tasks "
                          f"{'(including new tasks)' if self.partition_info['is_last_node'] else ''} "
                          f"查询耗时: {query_time:.2f}秒")
                
                # 性能警告
                if query_time > 1.0:
                    logger.warning(f"Database query took {query_time:.2f}s, which is slow. "
                                 f"Consider running ANALYZE on the tasks table.")

                # 3. 批量获取任务的Redis数据（不需要加锁，因为使用了分区）
                start_time = time.time()
                pipeline = self.redis_client.pipeline()
                task_infos = []
                
                for task in unfinished_tasks:
                    # Now using mappings() so we can access by name
                    task_id = task['id']
                    sync_check_count = task['sync_check_count'] or 0
                    task_infos.append({
                        'id': task_id,
                        'sync_check_count': sync_check_count
                    })
                    # 从Hash获取所有字段
                    task_key = f"{self.prefix}:TASK:{task_id}"
                    pipeline.hgetall(task_key)
                    
                # 执行批量查询
                redis_values = await pipeline.execute()
                logger.info(f'遍历redis耗时： {time.time() - start_time:.2f}秒')
                
                # 4. 处理查询结果
                updates = []
                no_change_tasks = []  # 没有变化的任务，需要更新next_sync_time
                
                for i, task_info in enumerate(task_infos):
                    task_id = task_info['id']
                    sync_check_count = task_info['sync_check_count']
                    hash_data = redis_values[i]  # TASK Hash数据
                    
                    update_info = {
                        'id': task_id,
                        'status': None,
                        'result': None,
                        'error_message': None,
                        'started_at': None,
                        'completed_at': None,
                        'worker_id': None,
                        'execution_time': None,
                        'duration': None,
                        'metadata': None
                    }
                    
                    # 优先处理新的Hash数据
                    if hash_data:
                        try:
                            # Hash数据已经是字典格式，直接使用
                            # 解码bytes键和值
                            hash_dict = {}
                            for k, v in hash_data.items():
                                key = k.decode('utf-8') if isinstance(k, bytes) else k
                                value = v.decode('utf-8') if isinstance(v, bytes) else v
                                hash_dict[key] = value
                            
                            # 映射字段
                            update_info['status'] = hash_dict.get('status')
                            update_info['error_message'] = hash_dict.get('error_msg') or hash_dict.get('exception')
                            
                            # 转换时间戳字符串为UTC datetime
                            if hash_dict.get('started_at'):
                                update_info['started_at'] = datetime.fromtimestamp(float(hash_dict['started_at']), tz=timezone.utc)
                            if hash_dict.get('completed_at'):
                                update_info['completed_at'] = datetime.fromtimestamp(float(hash_dict['completed_at']), tz=timezone.utc)
                                
                            update_info['worker_id'] = hash_dict.get('consumer') or hash_dict.get('worker_id')
                            
                            # 转换数值字符串为浮点数
                            if hash_dict.get('execution_time'):
                                update_info['execution_time'] = float(hash_dict['execution_time'])
                            if hash_dict.get('duration'):
                                update_info['duration'] = float(hash_dict['duration'])
                            
                            # 处理result字段
                            if 'result' in hash_dict:
                                result_str = hash_dict['result']
                                if result_str == 'null':
                                    update_info['result'] = None
                                else:
                                    update_info['result'] = result_str
                            
                            logger.debug(f"Task {task_id} from hash: {hash_dict}")
                            
                        except Exception as e:
                            logger.warning(f"Failed to parse hash data for task {task_id}: {e}")
                    
                    
                    # 只有当有数据更新时才添加到更新列表（任何字段有值都应该更新）
                    if any(v is not None for k, v in update_info.items() if k not in ['id', 'sync_check_count']):
                        update_info['sync_check_count'] = sync_check_count
                        updates.append(update_info)
                    else:
                        # 没有变化的任务
                        no_change_tasks.append({
                            'id': task_id,
                            'sync_check_count': sync_check_count
                        })
                
                # 5. 批量更新任务状态
                if updates:
                    start_time = time.time()
                    await self._update_tasks(updates)
                    elapsed_time = time.time() - start_time
                    logger.info(f"Updated {len(updates)} task statuses from {len(task_infos)} processed 耗时={elapsed_time:.2f}秒")
                    
                    # 动态调整批次大小
                    if elapsed_time > 5:  # 处理时间超过5秒，减小批次
                        self.batch_size = max(self.min_batch_size, int(self.batch_size * 0.8))
                        logger.info(f"Decreased batch size to {self.batch_size} due to slow processing")
                    elif elapsed_time < 1 and len(unfinished_tasks) == self.batch_size:  # 处理很快且达到批次上限
                        self.batch_size = min(self.max_batch_size, int(self.batch_size * 1.2))
                        logger.info(f"Increased batch size to {self.batch_size} due to fast processing")
                
                # 5. 更新没有变化的任务的下次同步时间
                if no_change_tasks:
                    await self._update_next_sync_time(no_change_tasks)
                    logger.debug(f"Updated next_sync_time for {len(no_change_tasks)} unchanged tasks")
                
                # 6. 动态等待时间
                if not updates and not no_change_tasks:
                    # 没有需要处理的任务，等待一段时间
                    await asyncio.sleep(2)
                else:
                    # 有任务处理，继续处理下一批
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"Error in update_task_status: {e}", exc_info=True)
                
    async def _update_tasks(self, updates: List[Dict[str, Any]]):
        """批量更新任务状态"""
        if not updates:
            return
            
        try:
            async with self.AsyncSessionLocal() as session:
                # 根据状态分组更新，简化SQL
                completed_tasks = []
                running_tasks = []
                
                for update in updates:
                    task_id = update['id']
                    status = update.get('status')
                    
                    
                    if status in ('success', 'error', 'failed', 'timeout', 'cancelled'):
                        completed_tasks.append(update)
                    else:
                        running_tasks.append(update)
                
                # 批量更新已完成的任务
                if completed_tasks:
                    # 使用循环执行更新（SQLAlchemy的批量更新对于复杂的UPDATE FROM VALUES比较困难）
                    for task in completed_tasks:
                        query = text("""
                            UPDATE tasks SET
                                status = :status,
                                result = CAST(:result AS jsonb),
                                error_message = :error_message,
                                started_at = COALESCE(:started_at, started_at),
                                completed_at = :completed_at,
                                worker_id = COALESCE(:worker_id, worker_id),
                                execution_time = :execution_time,
                                duration = :duration,
                                sync_check_count = 0,
                                next_sync_time = 999999999999
                            WHERE id = :id
                        """)
                        
                        await session.execute(query, {
                            'id': task['id'],
                            'status': task.get('status'),
                            'result': task.get('result'),  # 已经是JSON字符串
                            'error_message': task.get('error_message'),
                            'started_at': task.get('started_at'),
                            'completed_at': task.get('completed_at'),
                            'worker_id': task.get('worker_id'),
                            'execution_time': task.get('execution_time'),
                            'duration': task.get('duration')
                        })
                    
                    await session.commit()
                    logger.debug(f"Updated {len(completed_tasks)} completed tasks")
                
                # 批量更新运行中的任务
                if running_tasks:
                    # 只更新有变化的字段
                    task_ids = [t['id'] for t in running_tasks]
                    # 准备更新数据
                    for task in running_tasks:
                        sync_count = task.get('sync_check_count', 0) + 1
                        next_sync = self._get_next_sync_time(sync_count)
                        
                        query = text("""
                            UPDATE tasks
                            SET sync_check_count = :sync_check_count,
                                next_sync_time = :next_sync_time
                            WHERE id = :id
                        """)
                        
                        await session.execute(query, {
                            'id': task['id'],
                            'sync_check_count': sync_count,
                            'next_sync_time': next_sync
                        })
                    
                    await session.commit()
                    logger.debug(f"Updated {len(running_tasks)} running tasks")
                
                logger.info(f"Updated {len(updates)} task statuses")
                
        except Exception as e:
            logger.error(f"Error updating task statuses: {e}")

    async def _update_next_sync_time(self, tasks: List[Dict[str, Any]]):
        """更新没有变化的任务的下次同步时间"""
        if not tasks:
            return
            
        # 准备更新数据
        update_data = []
        for task in tasks:
            sync_count = task.get('sync_check_count', 0) + 1
            next_sync = self._get_next_sync_time(sync_count)
            update_data.append((task['id'], sync_count, next_sync))
        
        try:
            async with self.AsyncSessionLocal() as session:
                # 使用循环执行更新
                for task_id, sync_count, next_sync in update_data:
                    query = text("""
                        UPDATE tasks
                        SET sync_check_count = :sync_check_count,
                            next_sync_time = :next_sync_time
                        WHERE id = :id
                    """)
                    
                    await session.execute(query, {
                        'id': task_id,
                        'sync_check_count': sync_count,
                        'next_sync_time': next_sync
                    })
                
                await session.commit()
                logger.debug(f"Updated next_sync_time for {len(tasks)} unchanged tasks")
        except Exception as e:
            logger.error(f"Error updating next_sync_time: {e}")

    async def _partition_coordinator(self):
        """分区协调器 - 定期统计任务并分配分区
        
        分区策略：
        1. 使用 MD5(id) 的哈希值对节点数取模，确保任务均匀分布
        2. 最后一个节点额外处理所有新增的任务（ID > max_id）
        3. 这样既保证了负载均衡，又确保新任务能被及时处理
        
        PostgreSQL中的哈希计算：
        MOD(('x' || substr(md5(id), 1, 8))::bit(32)::int, node_count) = node_index
        - md5(id): 计算ID的MD5哈希
        - substr(..., 1, 8): 取前8个字符（32位）
        - 'x' || ...: 添加前缀避免负数
        - ::bit(32)::int: 转换为整数
        - MOD(..., node_count): 对节点数取模
        """
        partition_key = f"{self.prefix}:PARTITION_INFO"
        node_heartbeat_key = f"{self.prefix}:NODE:{self.node_id}"
        
        while self._running:
            try:
                # 1. 更新节点心跳
                is_new_node = not await self.redis_client.exists(node_heartbeat_key)
                await self.redis_client.setex(node_heartbeat_key, 30, time.time())
                
                # 如果是新节点或从离线恢复
                if is_new_node:
                    # 检查是否是重新上线（通过检查是否有历史分区信息）
                    stored_info = await self.redis_client.hget(partition_key, self.node_id)
                    if stored_info:
                        # 是重新上线的节点，设置宽限期
                        logger.warning(f"Node {self.node_id} is rejoining after offline, entering grace period")
                        self.partition_info['grace_period'] = True
                        self.partition_info['grace_start'] = time.time()
                    
                    await self.redis_client.publish(
                        f"{self.prefix}:NODE_EVENTS", 
                        json.dumps({"event": "node_join", "node_id": self.node_id})
                    )
                    logger.info(f"Published node join event for {self.node_id}")
                
                # 2. 获取所有活跃节点
                pattern = f"{self.prefix}:NODE:*"
                active_nodes = []
                async for key in self.redis_client.scan_iter(match=pattern):
                    heartbeat = await self.redis_client.get(key)
                    if heartbeat:
                        node_id = key.decode('utf-8').split(':')[-1]
                        active_nodes.append(node_id)
                
                active_nodes.sort()  # 确保所有节点看到相同的顺序
                node_count = len(active_nodes)
                
                if self.node_id in active_nodes:
                    node_index = active_nodes.index(self.node_id)
                else:
                    logger.error(f"Node {self.node_id} not in active nodes list")
                    await asyncio.sleep(5)
                    continue
                
                # 3. 检测节点数量变化，快速响应
                if node_count != self.partition_info['active_nodes']:
                    logger.info(f"Node count changed from {self.partition_info['active_nodes']} to {node_count}, updating partition immediately")
                    self.partition_info['last_update'] = 0  # 强制立即更新
                
                # 4. 获取任务ID范围（每30秒更新一次，或节点数变化时立即更新）
                current_time = time.time()
                if current_time - self.partition_info['last_update'] > 30:
                    async with self.AsyncSessionLocal() as session:
                        # 获取当前任务的ID范围
                        query = text("""
                            SELECT MIN(id) as min_id, MAX(id) as max_id
                            FROM tasks 
                            WHERE status IN ('pending', 'running')
                              AND next_sync_time <= :current_time
                        """)
                        result_obj = await session.execute(query, {'current_time': time.time()})
                        result = result_obj.mappings().fetchone()
                        
                        if result and result['min_id'] and result['max_id']:
                            min_id = result['min_id']
                            max_id = result['max_id']
                            
                            # 4. 基于ID计算分区
                            # 将ID空间分成N份
                            id_ranges = []
                            
                            # 对于字符串ID，使用哈希分区
                            for i in range(node_count):
                                is_last = (i == node_count - 1)
                                id_ranges.append({
                                    'node_index': i,
                                    'is_last': is_last
                                })
                            
                            # 当前节点的信息
                            current_node = id_ranges[node_index]
                            
                            self.partition_info.update({
                                'min_id': min_id,
                                'max_id': max_id,
                                'active_nodes': node_count,
                                'node_index': node_index,
                                'is_last_node': current_node['is_last'],
                                'last_update': current_time
                            })
                            
                            # 5. 发布分区信息到 Redis（供监控使用）
                            await self.redis_client.hset(partition_key, self.node_id, json.dumps({
                                'node_index': node_index,
                                'total_nodes': node_count,
                                'is_last_node': current_node['is_last'],
                                'updated_at': current_time
                            }))
                            
                            logger.info(f"Partition updated: node {node_index}/{node_count}, "
                                      f"is_last_node: {current_node['is_last']}")
                
                # 每5秒检查一次
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in partition coordinator: {e}", exc_info=True)
                await asyncio.sleep(10)
    
    async def _database_maintenance(self):
        """定期执行数据库维护任务"""
        last_analyze_time = 0
        analyze_interval = 3600  # 每小时执行一次ANALYZE
        
        while self._running:
            try:
                current_time = time.time()
                
                # 定期执行ANALYZE来更新统计信息
                if current_time - last_analyze_time > analyze_interval:
                    async with self.AsyncSessionLocal() as session:
                        logger.info("Running ANALYZE on tasks table to update statistics...")
                        await session.execute(text("ANALYZE tasks"))
                        await session.commit()
                        logger.info("ANALYZE completed successfully")
                        last_analyze_time = current_time
                
                # 每5分钟检查一次
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in database maintenance: {e}")
                await asyncio.sleep(60)
    
    async def _node_event_listener(self):
        """监听节点事件，实时响应节点变化"""
        while self._running:
            try:
                # 监听Pub/Sub消息
                message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                
                if message and message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        event_type = data.get('event')
                        node_id = data.get('node_id')
                        
                        if event_type in ['node_join', 'node_leave']:
                            logger.info(f"Received {event_type} event from node {node_id}")
                            # 强制立即更新分区信息
                            self.partition_info['last_update'] = 0
                            
                            # 如果正在处理任务，等待当前批次完成
                            await asyncio.sleep(0.5)
                            
                    except Exception as e:
                        logger.error(f"Error processing node event: {e}")
                        
            except asyncio.TimeoutError:
                # 没有消息，继续循环
                pass
            except Exception as e:
                logger.error(f"Error in node event listener: {e}")
                await asyncio.sleep(1)


async def run_pg_consumer(pg_config: PostgreSQLConfig, redis_config: RedisConfig):
    """运行PostgreSQL消费者"""
    consumer = PostgreSQLConsumer(pg_config, redis_config)
    
    try:
        await consumer.start()
        
        # 保持运行
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await consumer.stop()

def main():
    """主入口函数"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建配置
    pg_config = PostgreSQLConfig(
        host=os.getenv('JETTASK_PG_HOST', 'localhost'),
        port=int(os.getenv('JETTASK_PG_PORT', '5432')),
        database=os.getenv('JETTASK_PG_DB', 'jettask'),
        user=os.getenv('JETTASK_PG_USER', 'jettask'),
        password=os.getenv('JETTASK_PG_PASSWORD', '123456'),
    )
    
    redis_config = RedisConfig(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        db=int(os.getenv('REDIS_DB', '0')),
        password=os.getenv('REDIS_PASSWORD'),
    )
    
    # 运行消费者
    asyncio.run(run_pg_consumer(pg_config, redis_config))

if __name__ == '__main__':
    main()