import asyncio
import time
import logging
import traceback
import ujson
from typing import Optional, Union
from collections import defaultdict, deque

from .base import BaseExecutor

logger = logging.getLogger('app')

# Try to use uvloop for better performance
try:
    import uvloop
    uvloop.install()
    logger.info("Using uvloop for better performance")
except ImportError:
    pass


class AsyncioExecutor(BaseExecutor):
    """High-performance asyncio executor"""
    
    def __init__(self, event_queue, app, concurrency=100):
        super().__init__(event_queue, app, concurrency)
        
        # Caching for pending count
        self.pending_cache = {}
        self.pending_cache_expire = 0
        
        # 高性能模式默认设置
        self.ack_buffer_size = 500  # 高性能批量大小
        self.max_ack_buffer_size = 2000  # 最大批量大小
        self.status_batch_size = 1000  # 高性能状态更新批量
        self.data_batch_size = 1000   # 高性能数据更新批量
        
        # 性能优化2: 预分配内存避免频繁扩容
        self.pending_acks = []
        self.status_updates = []  
        self.data_updates = []
        self.task_info_updates = {}  # 新增：使用字典存储每个任务的Hash更新
        
        # 预分配初始容量
        self.pending_acks.extend([None] * self.ack_buffer_size)
        self.pending_acks.clear()
        
        # 添加前缀
        self.prefix = self.app.ep.redis_prefix or 'jettask'
        
        # 高性能刷新策略
        self.last_flush_time = time.time()
        self.max_flush_interval = 0.05  # 50ms最大刷新间隔
        self.min_flush_interval = 0.005  # 5ms最小刷新间隔
        
        # 性能优化4: 预编译常量和缓存
        self._status_prefix = self.app._status_prefix
        self._result_prefix = self.app._result_prefix
        self._prefixed_queue_cache = {}  # 缓存队列名称
        
        # 默认启用高性能模式
        self._stats_lock = asyncio.Lock()
        self._high_performance_mode = True  # 始终启用高性能模式
        
    def _get_prefixed_queue_cached(self, queue: str) -> str:
        """缓存队列名称以避免重复字符串拼接"""
        if queue not in self._prefixed_queue_cache:
            self._prefixed_queue_cache[queue] = self.app.ep.get_prefixed_queue_name(queue)
        return self._prefixed_queue_cache[queue]
        
    async def get_pending_count_cached(self, queue: str) -> int:
        """Get cached pending count"""
        current_time = time.time()
        
        if (current_time - self.pending_cache_expire > 30 or  # 优化：延长缓存时间
            queue not in self.pending_cache):
            try:
                pending_info = await self.app.ep.async_redis_client.xpending(queue, queue)
                self.pending_cache[queue] = pending_info.get("pending", 0)
                self.pending_cache_expire = current_time
            except Exception:
                self.pending_cache[queue] = 0
                
        return self.pending_cache.get(queue, 0)
    
    async def _quick_ack(self, queue: str, event_id: str):
        """Quick ACK with adaptive batching and smart flushing"""
        self.pending_acks.append((queue, event_id))
        current_time = time.time()
        
        # 高性能刷新策略：更激进的批量处理
        should_flush = (
            len(self.pending_acks) >= self.ack_buffer_size or  # 达到批量大小
            (len(self.pending_acks) >= 50 and  # 或有50个且超时
             current_time - self.last_flush_time >= self.max_flush_interval) or
            len(self.pending_acks) >= self.max_ack_buffer_size * 0.1  # 达到最大缓冲区10%
        )
        
        if should_flush:
            await self._flush_acks()
    
    async def _flush_acks(self):
        """Batch execute ACKs - optimized"""
        if not self.pending_acks:
            return
            
        # 按队列分组以优化批量操作
        from collections import defaultdict
        acks_by_queue = defaultdict(list)
        for queue, event_id in self.pending_acks:
            acks_by_queue[queue].append(event_id)
        
        self.pending_acks.clear()
        
        # 并发执行每个队列的批量ACK
        tasks = []
        
        for queue, event_ids in acks_by_queue.items():
            # 使用缓存的队列名称和高性能批量大小
            prefixed_queue = self._get_prefixed_queue_cached(queue)
            batch_size = 2000  # 高性能批量大小
            
            for i in range(0, len(event_ids), batch_size):
                batch = event_ids[i:i+batch_size]
                tasks.append(self.app.ep.async_redis_client.xack(prefixed_queue, prefixed_queue, *batch))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.last_flush_time = time.time()
    
    async def _flush_status_updates(self):
        """批量更新状态 - 优化使用MSET"""
        if not self.status_updates:
            return
            
        # 使用自适应批量大小
        batch_size = self.status_batch_size
        updates = self.status_updates[:batch_size]
        self.status_updates = self.status_updates[batch_size:]
        
        # 优化：使用MSET进行超高效批量更新
        mapping = {}
        expire_keys = []
        
        for event_id, status_dict in updates:
            key = f"{self._status_prefix}{event_id}"
            mapping[key] = ujson.dumps(status_dict)
            expire_keys.append(key)
        
        if mapping:
            # 使用pipeline批量设置值和过期时间
            pipeline = self.app.ep.async_redis_client.pipeline()
            pipeline.mset(mapping)
            
            # 批量设置过期时间
            for key in expire_keys:
                pipeline.expire(key, 3600)
            
            await pipeline.execute()
    
    async def _flush_data_updates(self):
        """批量更新数据 - 优化使用MSET"""
        if not self.data_updates:
            return
            
        # 使用自适应批量大小
        batch_size = self.data_batch_size
        updates = self.data_updates[:batch_size]
        self.data_updates = self.data_updates[batch_size:]
        
        # 优化：使用MSET
        mapping = {}
        expire_keys = []
        
        for event_id, data in updates:
            key = f"{self._result_prefix}{event_id}"
            mapping[key] = data
            expire_keys.append(key)
        
        if mapping:
            pipeline = self.app.ep.async_redis_client.pipeline()
            pipeline.mset(mapping)
            
            # 批量设置过期时间
            for key in expire_keys:
                pipeline.expire(key, 3600)
                
            await pipeline.execute()
    
    async def _flush_task_info_updates(self):
        """批量更新任务信息到Redis Hash - 新方法，合并STATUS和RESULT"""
        if not self.task_info_updates:
            return
            
        # 获取当前缓冲区的快照，避免并发修改问题
        updates_snapshot = dict(self.task_info_updates)
        self.task_info_updates.clear()
        
        # 使用pipeline批量处理
        pipeline = self.app.ep.async_redis_client.pipeline()
        
        # 处理每个任务的更新
        for event_id, updates in updates_snapshot.items():
            key = f"{self.prefix}:TASK:{event_id}"
            
            # 使用HSET更新多个字段
            if updates:
                pipeline.hset(key, mapping=updates)
                pipeline.expire(key, 3600)  # 1小时过期
        
        # 执行pipeline
        if pipeline:
            await pipeline.execute()
    
    async def _flush_all_buffers(self):
        """并发刷新所有缓冲区"""
        await asyncio.gather(
            self._flush_acks(),
            self._flush_status_updates(),
            self._flush_data_updates(),
            self._flush_task_info_updates(),  # 新增：刷新合并的任务信息
            return_exceptions=True
        )
    
    async def _collect_stats_async(self, queue: str, success: bool, processing_time: float, total_latency: float):
        """高性能异步统计收集，完全非阻塞"""
        try:
            if hasattr(self.app, 'consumer_manager') and self.app.consumer_manager:
                # 异步方式收集，不等待完成
                asyncio.create_task(self._update_stats_nonblocking(queue, success, processing_time, total_latency))
        except Exception:
            pass  # 统计错误不应影响主流程
    
    async def _update_stats_nonblocking(self, queue: str, success: bool, processing_time: float, total_latency: float):
        """非阻塞统计更新"""
        try:
            self.app.consumer_manager.task_finished(queue)
            self.app.consumer_manager.update_stats(
                queue=queue,
                success=success,
                processing_time=processing_time,
                total_latency=total_latency
            )
        except Exception as e:
            logger.debug(f"Stats collection error (non-critical): {e}")
    
        
    async def logic(self, semaphore: asyncio.Semaphore, event_id: str, event_data: dict, queue: str, routing: dict = None, consumer: str = None):
        """Process a single task"""
        try:
            # async with semaphore:
            task_name = event_data.get("name", "")
            task = self.app.get_task_by_name(task_name)
            if not task:
                exception = f"{task_name} {queue} {routing}未绑定任何task"
                logger.error(exception)
                await self._quick_ack(queue, event_id)
                
                # 任务不存在时也记录started_at（使用当前时间）
                current_time = time.time()
                trigger_time_float = float(event_data['trigger_time'])
                duration = current_time - trigger_time_float
                # 使用Hash更新
                self.task_info_updates[event_id] = {
                    "status": "error",
                    "exception": exception,
                    "started_at": str(current_time),
                    "completed_at": str(current_time),
                    "duration": str(duration),
                    "consumer": consumer,
                    "result": "null"  # 任务不存在时没有结果
                }
                await self._flush_task_info_updates()
                return
            
            self.pedding_count = await self.get_pending_count_cached(queue)
            
            status = "success"
            exception = None
            error_msg = None
            ret = None
            
            # 提前记录开始时间，避免在reject情况下未定义
            execution_start_time = time.time()
            
            args = ujson.loads(event_data["args"])
            kwargs = ujson.loads(event_data["kwargs"])
            
            # Execute lifecycle methods
            result = task.on_before(
                event_id=event_id,
                pedding_count=self.pedding_count,
                args=args,
                kwargs=kwargs,
            )
            if asyncio.iscoroutine(result):
                result = await result
                
            if result and result.reject:
                # 任务被reject，使用Hash更新
                self.task_info_updates[event_id] = {
                    "status": "rejected",
                    "consumer": consumer,
                    "started_at": str(execution_start_time),
                    "completed_at": str(time.time()),
                    "error_msg": "Task rejected by on_before"
                }
                await self._flush_task_info_updates()
                return
                
            # 标记任务开始执行
            if hasattr(self.app, 'consumer_manager') and self.app.consumer_manager:
                self.app.consumer_manager.task_started(queue)
            
            # 更新任务真正开始执行的时间（在on_before之后）
            execution_start_time = time.time()
            
            # 使用Hash更新running状态
            # 为了让用户能看到任务正在运行，立即写入running状态
            # running_key = f"{self.prefix}:TASK:{event_id}"
            # 保存开始信息，但不设置status为running，避免竞态条件
            self.task_info_updates[event_id] = {
                # "status": "running",  # 不在这里设置status
                "consumer": consumer,
                "started_at": str(execution_start_time)
            }
            # await self.app.ep.async_redis_client.hset(running_key, mapping={
            #     "status": "running",
            #     "consumer": consumer,
            #     "started_at": str(execution_start_time)
            # })
            
            try:
                
                task_result = task(event_id, event_data['trigger_time'], *args, **kwargs)
                if asyncio.iscoroutine(task_result):
                    ret = await task_result
                else:
                    ret = task_result
                result = task.on_success(
                    event_id=event_id,
                    args=args,
                    kwargs=kwargs,
                    result=ret,
                )
                if asyncio.iscoroutine(result):
                    await result
                    
            except SystemExit:
                # 处理系统退出信号，不记录为错误
                logger.info('Task interrupted by system exit')
                status = "interrupted"
                exception = "System exit"
                error_msg = "Task interrupted by shutdown"
            except Exception as e:
                logger.error('任务执行出错')
                status = "error"
                exception = traceback.format_exc()
                error_msg = str(e)
                traceback.print_exc()
                
            finally:
                # 添加到批量缓冲区而不是立即执行
                await self._quick_ack(queue, event_id)
                
                # 计算完成时间和消耗时间
                completed_at = time.time()
                trigger_time_float = float(event_data['trigger_time'])
                # 计算两个时间指标，确保不会出现负数
                execution_time = max(0, completed_at - execution_start_time)  # 实际执行时间
                total_latency = max(0, completed_at - trigger_time_float)     # 总延迟时间（包含等待）
                
                # 异步收集统计信息（高性能模式下非阻塞）
                await self._collect_stats_async(
                    queue=queue,
                    success=(status == "success"),
                    processing_time=execution_time,
                    total_latency=total_latency
                )
                
                # 使用Hash原子更新所有信息
                # 重要：先设置result，再设置status，确保不会出现status=success但result还没写入的情况
                task_info = {
                    "completed_at": str(completed_at),
                    "execution_time": str(execution_time),
                    "duration": str(total_latency),
                    "consumer": consumer,
                    'status': status
                }
                
                # 先写入结果
                if ret is None:
                    task_info["result"] = "null"  # JSON null
                else:
                    task_info["result"] = ret if isinstance(ret, str) else ujson.dumps(ret)
                
                # 再写入错误信息（如果有）
                if exception:
                    task_info["exception"] = exception
                if error_msg:
                    task_info["error_msg"] = error_msg
                    
                
                # 更新到缓冲区
                if event_id in self.task_info_updates:
                    # 合并更新（保留started_at等之前的信息）
                    # 重要：确保最终状态覆盖之前的running状态
                    self.task_info_updates[event_id].update(task_info)
                else:
                    self.task_info_updates[event_id] = task_info
                
                result = task.on_end(
                    event_id=event_id,
                    args=args,
                    kwargs=kwargs,
                    result=ret,
                    pedding_count=self.pedding_count,
                )
                if asyncio.iscoroutine(result):
                    await result
                    
                # Handle routing
                if routing:
                    agg_key = routing.get("agg_key")
                    routing_key = routing.get("routing_key")
                    if routing_key and agg_key:
                        # 避免在多进程环境下使用跨进程的锁
                        # 直接操作，依赖 Python GIL 和原子操作
                        if queue in self.app.ep.solo_running_state and routing_key in self.app.ep.solo_running_state[queue]:
                            self.app.ep.solo_running_state[queue][routing_key] -= 1
                    try:
                        if result and result.urgent_retry:
                            self.app.ep.solo_urgent_retry[routing_key] = True
                    except:
                        pass
                    if result and result.delay:
                        self.app.ep.task_scheduler[queue][routing_key] = time.time() + result.delay
                            
        finally:
            self.batch_counter -= 1
    
    async def loop(self):
        """Optimized main loop with dynamic batching"""
        semaphore = asyncio.Semaphore(self.concurrency)
        
        
        # Dynamic batch processing
        min_batch_size = 10   # 优化：降低最小批次
        max_batch_size = 500  # 优化：提高最大批次
        batch_size = 100
        tasks_batch = []
        
        # Performance tracking
        last_periodic_flush = time.time()
        last_batch_adjust = time.time()
        last_buffer_check = time.time()
        
        # 高性能缓冲区监控阈值
        max_buffer_size = 5000
        
        while True:
            # 检查是否需要退出
            if hasattr(self.app, '_should_exit') and self.app._should_exit:
                logger.info("AsyncioExecutor detected shutdown signal, exiting...")
                break
                
            # # 动态调整批处理大小
            current_time = time.time()
            if current_time - last_batch_adjust > 1.0:
                # 根据队列类型获取长度
                if isinstance(self.event_queue, deque):
                    queue_len = len(self.event_queue)
                elif isinstance(self.event_queue, asyncio.Queue):
                    queue_len = self.event_queue.qsize()
                else:
                    queue_len = 0
                    
                # 优化：更智能的动态调整
                if queue_len > 5000:
                    batch_size = min(max_batch_size, batch_size + 50)
                elif queue_len > 1000:
                    batch_size = min(max_batch_size, batch_size + 20)
                elif queue_len < 100:
                    batch_size = max(min_batch_size, batch_size - 20)
                elif queue_len < 500:
                    batch_size = max(min_batch_size, batch_size - 10)
                last_batch_adjust = current_time
                
            # 从队列获取事件
            event = None
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                event = None
                    
            if event:
                event.pop("execute_time", None)
                tasks_batch.append(event)
            # 批量创建协程任务
            if tasks_batch:
                for event in tasks_batch:
                    self.batch_counter += 1
                    asyncio.create_task(self.logic(semaphore, **event))
                
                tasks_batch.clear()
            
            # 智能缓冲区管理和刷新
            buffer_full = (
                len(self.pending_acks) >= max_buffer_size or
                len(self.status_updates) >= max_buffer_size or 
                len(self.data_updates) >= max_buffer_size or
                len(self.task_info_updates) >= max_buffer_size  # 新增：检查Hash缓冲区
            )
            
            # 定期或缓冲区满时刷新
            should_flush_periodic = (current_time - last_periodic_flush > self.max_flush_interval)
            has_pending_data = (self.pending_acks or self.status_updates or self.data_updates or self.task_info_updates)
            
            if buffer_full or (should_flush_periodic and has_pending_data):
                asyncio.create_task(self._flush_all_buffers())
                last_periodic_flush = current_time
            
            
            # 智能休眠策略
            has_events = False
            if isinstance(self.event_queue, deque):
                has_events = bool(self.event_queue)
            elif isinstance(self.event_queue, asyncio.Queue):
                has_events = not self.event_queue.empty()
                
            if has_events:
                await asyncio.sleep(0)  # 有任务时立即切换
            else:
                # 检查是否需要立即刷新缓冲区
                if (self.pending_acks or self.status_updates or self.data_updates or self.task_info_updates):
                    await self._flush_all_buffers()
                await asyncio.sleep(0.001)  # 无任务时短暂休眠
        
        # 退出前清理所有缓冲区
        logger.info("AsyncioExecutor flushing buffers before exit...")
        await self._flush_all_buffers()
        
        # 等待所有正在执行的任务完成
        logger.info("AsyncioExecutor stopped")