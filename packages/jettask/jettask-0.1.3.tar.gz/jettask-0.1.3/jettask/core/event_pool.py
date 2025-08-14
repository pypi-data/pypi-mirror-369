import json
import time
import threading
import logging
import contextlib
import asyncio
from collections import defaultdict, deque, Counter
from typing import List, Optional, TYPE_CHECKING, Union

import redis
from redis import asyncio as aioredis


from ..utils.helpers import get_hostname
from .consumer_manager import ConsumerManager, ConsumerStrategy

logger = logging.getLogger('app')


class EventPool(object):
    STATE_MACHINE_NAME = "STATE_MACHINE"
    TIMEOUT = 60 * 5

    def __init__(
        self,
        redis_client: redis.StrictRedis,
        async_redis_client: aioredis.StrictRedis,
        queues: list = None,
        redis_url: str = None,
        consumer_strategy: str = None,
        consumer_config: dict = None,
        redis_prefix: str = None,
    ) -> None:
        self.redis_client = redis_client
        self.async_redis_client = async_redis_client
        self.queues = queues
        self._redis_url = redis_url or 'redis://localhost:6379/0'
        self.redis_prefix = redis_prefix or 'jettask'
        
        # 初始化消费者管理器
        strategy = ConsumerStrategy(consumer_strategy) if consumer_strategy else ConsumerStrategy.HEARTBEAT
        # 确保配置中包含队列信息
        manager_config = consumer_config or {}
        manager_config['queues'] = queues or []
        
        self.consumer_manager = ConsumerManager(
            redis_client=redis_client,
            strategy=strategy,
            config=manager_config
        )
        
        # 创建带前缀的队列名称映射
        self.prefixed_queues = {}
        
        self.solo_routing_tasks = {}
        self.solo_running_state = {}
        self.solo_urgent_retry = {}
        self.batch_routing_tasks = {}
        self.task_scheduler = {}
        self.running_task_state_mappings = {}
        self.delay_tasks = []
        self.solo_agg_task = {}
        self.rlock = threading.RLock()
        self._claimed_message_ids = set()  # 跟踪已认领的消息ID，防止重复处理
    
    def _put_task(self, event_queue: Union[deque, asyncio.Queue], task, urgent: bool = False):
        """统一的任务放入方法"""
        # 如果是deque，使用原有逻辑
        if isinstance(event_queue, deque):
            if urgent:
                event_queue.appendleft(task)
            else:
                event_queue.append(task)
        # 如果是asyncio.Queue，则暂时只能按顺序放入（Queue不支持优先级）
        elif isinstance(event_queue, asyncio.Queue):
            # 对于asyncio.Queue，我们需要在async上下文中操作
            # 这里先保留接口，具体实现在async方法中
            pass
    
    async def _async_put_task(self, event_queue: asyncio.Queue, task, urgent: bool = False):
        """异步任务放入方法"""
        await event_queue.put(task)

    def init_routing(self):
        for queue in self.queues:
            self.solo_agg_task[queue] = defaultdict(list)
            self.solo_routing_tasks[queue] = defaultdict(list)
            self.solo_running_state[queue]  = defaultdict(bool)
            self.batch_routing_tasks[queue]  = defaultdict(list)
            self.task_scheduler[queue] = defaultdict(int)
            self.running_task_state_mappings[queue] = defaultdict(dict)
            
    def get_prefixed_queue_name(self, queue: str) -> str:
        """为队列名称添加前缀"""
        return f"{self.redis_prefix}:QUEUE:{queue}"
    
    def get_redis_client(self, asyncio: bool = False):
        return self.async_redis_client if asyncio else self.redis_client

    def create_group(self):
        for queue in self.queues:
            prefixed_queue = self.get_prefixed_queue_name(queue)
            with contextlib.suppress(Exception):
                self.redis_client.xgroup_create(
                    name=prefixed_queue,
                    groupname=prefixed_queue,
                    id="0",
                    mkstream=True,
                )

    def send_event(self, queue, message: dict, asyncio: bool = False):
        client = self.get_redis_client(asyncio)
        prefixed_queue = self.get_prefixed_queue_name(queue)
        try:
            return client.xadd(prefixed_queue, message, maxlen=3000)
        except redis.exceptions.ResponseError as e:
            # 如果队列不存在，创建它
            if "ERR" in str(e):
                logger.warning(f'队列 {prefixed_queue} 不存在，正在创建...')
                try:
                    # 先创建队列
                    event_id = client.xadd(prefixed_queue, message, maxlen=3000)
                    # 再创建消费者组
                    with contextlib.suppress(Exception):
                        client.xgroup_create(
                            name=prefixed_queue,
                            groupname=prefixed_queue,
                            id="0"
                        )
                    return event_id
                except Exception as create_error:
                    logger.error(f'创建队列失败: {create_error}')
                    raise
            else:
                raise

    def batch_send_event(self, queue, messages: List[dict], asyncio: bool = False):
        client = self.get_redis_client(asyncio)
        pipe = client.pipeline()
        prefixed_queue = self.get_prefixed_queue_name(queue)
        if asyncio:
            return self._batch_send_event(prefixed_queue, messages, pipe)
        for message in messages:
            pipe.xadd(prefixed_queue, message)
        return pipe.execute()

    async def _batch_send_event(self, prefixed_queue, messages: List[dict], pipe):
        for message in messages:
            await pipe.xadd(prefixed_queue, message)
        return await pipe.execute()
    
    def is_urgent(self, routing_key):
        is_urgent = self.solo_urgent_retry.get(routing_key, False)
        if is_urgent == True:
            del self.solo_urgent_retry[routing_key]
        return is_urgent
    
    @classmethod
    def separate_by_key(cls, lst):
        groups = {}
        for item in lst:
            key = item[0]['routing_key']
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        result = []
        group_values = list(groups.values())
        while True:
            exists_data = False
            for values in group_values:
                try:
                    result.append(values.pop(0))
                    exists_data = True
                except:
                    pass
            if not exists_data:
                break
        return result
    
    async def async_check_solo_agg_tasks(self, event_queue: asyncio.Queue):
        """异步版本的聚合任务检查"""
        last_solo_running_state = defaultdict(dict)
        last_wait_time = defaultdict(int)
        queue_batch_tasks = defaultdict(list)
        left_queue_batch_tasks = defaultdict(list)
        
        while True:
            has_work = False
            current_time = time.time()
            
            for queue in self.queues:
                for agg_key, tasks in self.solo_agg_task[queue].items():
                    if not tasks:
                        continue
                        
                    has_work = True
                    need_del_index = []
                    need_lock_routing_keys = []
                    sort_by_tasks = self.separate_by_key(tasks)
                    max_wait_time = 5
                    max_records = 3
                    
                    for index, (routing, task) in enumerate(sort_by_tasks):
                        routing_key = routing['routing_key']
                        max_records = routing.get('max_records', 1)
                        max_wait_time = routing.get('max_wait_time', 0)
                        
                        with self.rlock:
                            if self.solo_running_state[queue].get(routing_key, 0) > 0:
                                continue
                                
                        if len(queue_batch_tasks[queue] + left_queue_batch_tasks[queue]) >= max_records:
                            break 
                            
                        task["routing"] = routing

                        if self.is_urgent(routing_key):
                            left_queue_batch_tasks[queue].append(task)
                        else:
                            queue_batch_tasks[queue].append(task)
                        need_lock_routing_keys.append(routing_key)
                        need_del_index.append(index)

                    for routing_key, count in Counter(need_lock_routing_keys).items():
                        with self.rlock:
                            self.solo_running_state[queue][routing_key] = count
                            
                    if last_solo_running_state[queue] != self.solo_running_state[queue]:
                        last_solo_running_state[queue] = self.solo_running_state[queue].copy()
                        
                    tasks = [task for index, task in enumerate(sort_by_tasks) if index not in need_del_index]
                    self.solo_agg_task[queue][agg_key] = tasks
                    
                    if (len(queue_batch_tasks[queue] + left_queue_batch_tasks[queue]) >= max_records or 
                        (last_wait_time[queue] and last_wait_time[queue] < current_time - max_wait_time)):
                        for task in queue_batch_tasks[queue]:
                            await self._async_put_task(event_queue, task)
                        for task in left_queue_batch_tasks[queue]:
                            await self._async_put_task(event_queue, task)    
                        queue_batch_tasks[queue] = []
                        left_queue_batch_tasks[queue] = []
                        last_wait_time[queue] = 0
                    elif last_wait_time[queue] == 0:
                        last_wait_time[queue] = current_time
                        
            # 优化：根据是否有工作决定休眠时间
            if has_work:
                await asyncio.sleep(0.001)  # 有工作时极短休眠
            else:
                await asyncio.sleep(0.01)   # 无工作时短暂休眠
    
    def check_solo_agg_tasks(self, event_queue: Union[deque, asyncio.Queue]):
        """优化聚合任务检查，减少休眠时间"""
        last_solo_running_state = defaultdict(dict)
        last_wait_time = defaultdict(int)
        queue_batch_tasks = defaultdict(list)
        left_queue_batch_tasks = defaultdict(list)
        
        while True:
            has_work = False
            current_time = time.time()
            
            for queue in self.queues:
                for agg_key, tasks in self.solo_agg_task[queue].items():
                    if not tasks:
                        continue
                        
                    has_work = True
                    need_del_index = []
                    need_lock_routing_keys = []
                    sort_by_tasks = self.separate_by_key(tasks)
                    max_wait_time = 5
                    max_records = 3
                    
                    for index, (routing, task) in enumerate(sort_by_tasks):
                        routing_key = routing['routing_key']
                        max_records = routing.get('max_records', 1)
                        max_wait_time = routing.get('max_wait_time', 0)
                        
                        with self.rlock:
                            if self.solo_running_state[queue].get(routing_key, 0) > 0:
                                continue
                                
                        if len(queue_batch_tasks[queue] + left_queue_batch_tasks[queue]) >= max_records:
                            break 
                            
                        task["routing"] = routing

                        if self.is_urgent(routing_key):
                            left_queue_batch_tasks[queue].append(task)
                        else:
                            queue_batch_tasks[queue].append(task)
                        need_lock_routing_keys.append(routing_key)
                        need_del_index.append(index)

                    for routing_key, count in Counter(need_lock_routing_keys).items():
                        with self.rlock:
                            self.solo_running_state[queue][routing_key] = count
                            
                    if last_solo_running_state[queue] != self.solo_running_state[queue]:
                        last_solo_running_state[queue] = self.solo_running_state[queue].copy()
                        
                    tasks = [task for index, task in enumerate(sort_by_tasks) if index not in need_del_index]
                    self.solo_agg_task[queue][agg_key] = tasks
                    
                    if (len(queue_batch_tasks[queue] + left_queue_batch_tasks[queue]) >= max_records or 
                        (last_wait_time[queue] and last_wait_time[queue] < current_time - max_wait_time)):
                        for task in queue_batch_tasks[queue]:
                            self._put_task(event_queue, task)
                        for task in left_queue_batch_tasks[queue]:
                            self._put_task(event_queue, task, urgent=True)    
                        queue_batch_tasks[queue] = []
                        left_queue_batch_tasks[queue] = []
                        last_wait_time[queue] = 0
                    elif last_wait_time[queue] == 0:
                        last_wait_time[queue] = current_time
                        
            # 优化：根据是否有工作决定休眠时间
            if has_work:
                time.sleep(0.001)  # 有工作时极短休眠
            else:
                time.sleep(0.01)   # 无工作时短暂休眠
    
    def check_sole_tasks(self, event_queue: Union[deque, asyncio.Queue]):
        agg_task_mappings = {queue:  defaultdict(list) for queue in self.queues}
        agg_wait_task_mappings = {queue:  defaultdict(float) for queue in self.queues}
        task_max_wait_time_mapping = {}
        make_up_for_index_mappings = {queue:  defaultdict(int) for queue in self.queues} 
        while True:
            put_count = 0
            for queue in self.queues:
                agg_task = agg_task_mappings[queue]
                for routing_key, tasks in self.solo_routing_tasks[queue].items():
                    schedule_time = self.task_scheduler[queue][routing_key]
                    if tasks:
                        for task in tasks:
                            prev_routing = task[0]
                            if agg_key:= prev_routing.get('agg_key'):
                                if not self.running_task_state_mappings[queue][agg_key]:
                                    self.solo_running_state[queue][routing_key] = False
                                    break 
                    if (
                        schedule_time <= time.time()
                        and self.solo_running_state[queue][routing_key] == False
                    ) :
                            try:
                                routing, task = tasks.pop(0)
                            except IndexError:
                                continue
                            task["routing"] = routing
                            
                            agg_key = routing.get('agg_key')
                            if agg_key is not None:
                                start_time = agg_wait_task_mappings[queue][agg_key]
                                if not start_time:
                                    agg_wait_task_mappings[queue][agg_key] = time.time()
                                    start_time = agg_wait_task_mappings[queue][agg_key]
                                agg_task[agg_key].append(task)
                                max_wait_time = routing.get('max_wait_time', 3)
                                task_max_wait_time_mapping[agg_key] = max_wait_time
                                if len(agg_task[agg_key])>=routing.get('max_records', 100) or time.time()-start_time>=max_wait_time:
                                    logger.info(f'{agg_key=} {len(agg_task[agg_key])} 已满，准备发车！{routing.get("max_records", 100)} {time.time()-start_time} {max_wait_time}')
                                    for task in agg_task[agg_key]:
                                        task['routing']['version'] = 1
                                        self.running_task_state_mappings[queue][agg_key][task['event_id']] = time.time()
                                        self._put_task(event_queue, task, urgent=self.is_urgent(routing_key))
                                    agg_task[agg_key] = []
                                    make_up_for_index_mappings[queue][agg_key] = 0 
                                    agg_wait_task_mappings[queue][agg_key] = 0
                            else:
                                self._put_task(event_queue, task, urgent=self.is_urgent(routing_key))
                            self.solo_running_state[queue][routing_key] = True
                            put_count += 1
                for agg_key in agg_task.keys():
                    if not agg_task[agg_key]:
                        continue
                    start_time = agg_wait_task_mappings[queue][agg_key]
                    max_wait_time = task_max_wait_time_mapping[agg_key]
                    if make_up_for_index_mappings[queue][agg_key]>= len(agg_task[agg_key])-1:
                        make_up_for_index_mappings[queue][agg_key] = 0
                    routing = agg_task[agg_key][make_up_for_index_mappings[queue][agg_key]]['routing']
                    routing_key = routing['routing_key']
                    self.solo_running_state[queue][routing_key] = False
                    make_up_for_index_mappings[queue][agg_key] += 1
                    if time.time()-start_time>=max_wait_time:
                        logger.info(f'{agg_key=} {len(agg_task[agg_key])}被迫发车！ {time.time()-start_time} {max_wait_time}')
                        for task in agg_task[agg_key]:
                            task['routing']['version'] = 1
                            self.running_task_state_mappings[queue][agg_key][task['event_id']] = time.time()
                            self._put_task(event_queue, task, urgent=self.is_urgent(routing_key))
                        agg_task[agg_key] = []
                        make_up_for_index_mappings[queue][agg_key] = 0
                        agg_wait_task_mappings[queue][agg_key] = 0
            # 优化：根据处理任务数量动态调整休眠时间
            if not put_count:
                time.sleep(0.001)
            elif put_count < 5:
                time.sleep(0.0005)  # 少量任务时极短休眠
                
    def check_batch_tasks(self, event_queue: Union[deque, asyncio.Queue]):
        agg_task_mappings = {queue:  defaultdict(list) for queue in self.queues}
        agg_wait_task_mappings = {queue:  defaultdict(float) for queue in self.queues}
        while True:
            for queue in self.queues:
                agg_task = agg_task_mappings[queue]
                for _, tasks in self.batch_routing_tasks[queue].items():
                    try:
                        metadata, task = tasks.pop(0)
                    except IndexError:
                        continue
                    agg_key = metadata['agg_key']
                    start_time = agg_wait_task_mappings[queue][agg_key]
                    if not start_time:
                        agg_wait_task_mappings[queue][agg_key] = time.time()
                        start_time = agg_wait_task_mappings[queue][agg_key]
                    max_wait_time = metadata['max_wait_time']
                    max_records = metadata['max_records']
                    agg_task[agg_key].append(task)
                    if len(agg_task[agg_key])>=max_records or time.time()-start_time>=max_wait_time:
                        self._put_task(event_queue, {
                            'queue': queue,
                            'task_type': 'batch',
                            'event_ids': [item['event_id'] for item in agg_task[agg_key]],
                            'event_data_list': [item['event_data'] for item in agg_task[agg_key]],
                            'name': agg_task[agg_key][0]['event_data']['name'],
                        })
                        agg_task[agg_key] = []
                        agg_wait_task_mappings[queue][agg_key] = time.time()
                for agg_key in agg_task.keys():
                    if not agg_task[agg_key]:
                        continue
                    start_time = agg_wait_task_mappings[queue][agg_key]
                    max_wait_time = json.loads(agg_task[agg_key][0]['event_data']['routing'])['max_wait_time']
                    if  time.time()-start_time>=max_wait_time:
                        self._put_task(event_queue, {
                            'queue': queue,
                            'task_type': 'batch',
                            'event_ids': [item['event_id'] for item in agg_task[agg_key]],
                            'event_data_list': [item['event_data'] for item in agg_task[agg_key]],
                            'name': agg_task[agg_key][0]['event_data']['name'],
                        })
                        agg_task[agg_key] = []
                        agg_wait_task_mappings[queue][agg_key] = time.time()
            # 优化：减少休眠时间
            time.sleep(0.001)

    def check_delay_tasks(self, event_queue):
        while True:
            put_count = 0
            need_del_index = []
            for i in range(len(self.delay_tasks)):
                schedule_time = self.delay_tasks[i][0]
                task = self.delay_tasks[i][1]
                if schedule_time <= time.time():
                    try:
                        self._put_task(event_queue, task)
                        need_del_index.append(i)
                        put_count += 1
                    except IndexError:
                        pass
            for i in need_del_index:
                del self.delay_tasks[i]
            if not put_count:          
                time.sleep(1)

    def _handle_redis_error(self, error: Exception, consecutive_errors: int, queue: str = None) -> tuple[bool, int]:
        """处理Redis错误的通用方法
        返回: (should_recreate_connection, new_consecutive_errors)
        """
        if isinstance(error, redis.exceptions.ConnectionError):
            logger.error(f'Redis连接错误: {error}')
            consecutive_errors += 1
            if consecutive_errors >= 5:
                logger.error(f'连续连接失败{consecutive_errors}次，重新创建连接')
                return True, 0
            return False, consecutive_errors
            
        elif isinstance(error, redis.exceptions.ResponseError):
            if "NOGROUP" in str(error) and queue:
                logger.warning(f'队列 {queue} 或消费者组不存在')
                return False, consecutive_errors
            else:
                logger.error(f'Redis错误: {error}')
                consecutive_errors += 1
                return False, consecutive_errors
        else:
            logger.error(f'意外错误: {error}')
            consecutive_errors += 1
            return False, consecutive_errors

    def _process_message_common(self, event_id: str, event_data: dict, queue: str, event_queue, is_async: bool = False, consumer_name: str = None):
        """通用的消息处理逻辑，供同步和异步版本使用"""
        # 检查消息是否已被认领，防止重复处理
        if event_id in self._claimed_message_ids:
            logger.debug(f"跳过已认领的消息 {event_id}")
            return event_id
        
        routing = event_data.get("routing")
        task_item = {
            "queue": queue,
            "event_id": event_id,
            "event_data": event_data,
            "consumer": consumer_name,  # 添加消费者信息
        }
        
        push_flag = True
        if routing:
            routing = json.loads(routing)
            if agg_key := routing.get('agg_key'):
                self.solo_agg_task[queue][agg_key].append(
                    [routing, task_item]
                )
                push_flag = False
        
        if push_flag:
            if is_async:
                # 这里不能直接await，需要返回一个标记
                return ('async_put', task_item)
            else:
                self._put_task(event_queue, task_item)
        
        return event_id

    async def listening_event(self, event_queue: asyncio.Queue, prefetch_multiplier: int = 1):
        async def listen_event_by_group(queue):
            check_backlog = True
            lastid = "0-0"
            consecutive_errors = 0
            max_consecutive_errors = 5

            # 启动异步任务处理solo_agg_tasks
            asyncio.create_task(self.async_check_solo_agg_tasks(event_queue))
            
            while True:
                if check_backlog:
                    myid = lastid
                else:
                    myid = ">"
                # 检查队列大小
                c_qsize = event_queue.qsize()
                
                if c_qsize >= max(prefetch_multiplier // 2, 1):
                    await asyncio.sleep(0.5)
                    continue
                logger.debug(
                    f"读取{queue}数据，当前堆积消息数：{c_qsize} {prefetch_multiplier-c_qsize=}"
                )
                try:
                    # 检查心跳是否超时
                    if self.consumer_manager.is_heartbeat_timeout():
                        logger.error(f"Heartbeat timeout detected for queue {queue}, shutting down...")
                        logger.error("Worker detected its own heartbeat timeout - likely network issue or being replaced")
                        logger.error("Initiating graceful shutdown to avoid conflicts with replacement worker")
                        
                        # 设置停止标志，触发优雅退出
                        self._stop_reading = True
                        
                        # 标记所有队列停止读取
                        for q in self.queues:
                            if q in self._queue_stop_flags:
                                self._queue_stop_flags[q] = True
                        
                        # 发送系统退出信号进行优雅关闭
                        import os
                        import signal
                        os.kill(os.getpid(), signal.SIGTERM)
                        return
                    
                    # 使用消费者管理器获取消费者名称
                    consumer_name = self.consumer_manager.get_consumer_name(queue)
                    # 计算要读取的消息数
                    count_to_read = max(1, prefetch_multiplier - c_qsize)
                    
                    prefixed_queue = self.get_prefixed_queue_name(queue)
                    messages = await self.async_redis_client.xreadgroup(
                        groupname=prefixed_queue,
                        consumername=consumer_name,
                        streams={prefixed_queue: myid},
                        count=count_to_read,
                        block=1000,  # 设置1秒超时而不是无限阻塞
                    )
                    # 成功读取，重置错误计数
                    consecutive_errors = 0
                    
                    if messages:
                        msg_count = len(messages[0][1]) if messages else 0
                        logger.info(f"Read {msg_count} messages from queue {queue}")
                        if msg_count > 0:
                            logger.info(f"Processing {msg_count} messages...")
                    
                except redis.exceptions.TimeoutError as e:
                    logger.warning(f'Redis读取超时: {e}，尝试重新连接...')
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f'连续超时{consecutive_errors}次，重新创建连接')
                        self._recreate_redis_connection()
                        consecutive_errors = 0
                    await asyncio.sleep(min(consecutive_errors * 0.5, 5))  # 指数退避
                    continue
                    
                except redis.exceptions.ConnectionError as e:
                    logger.error(f'Redis连接错误: {e}')
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f'连续连接失败{consecutive_errors}次，重新创建连接')
                        self._recreate_redis_connection()
                        consecutive_errors = 0
                    await asyncio.sleep(min(consecutive_errors, 10))  # 指数退避，最多10秒
                    continue
                    
                except redis.exceptions.ResponseError as e:
                    if "NOGROUP" in str(e):
                        # 队列或消费者组不存在，尝试重新创建
                        logger.warning(f'队列 {queue} 或消费者组不存在，尝试重新创建...')
                        try:
                            # 尝试创建消费者组 - 使用带前缀的队列名
                            prefixed_queue = self.get_prefixed_queue_name(queue)
                            await self.async_redis_client.xgroup_create(
                                name=prefixed_queue,
                                groupname=prefixed_queue,
                                id="0",
                                mkstream=True
                            )
                            logger.debug(f'成功重新创建队列 {prefixed_queue} 和消费者组')
                            check_backlog = True
                            lastid = "0-0"  # 重置ID，从头开始读取
                            consecutive_errors = 0
                            continue
                        except Exception as create_error:
                            logger.error(f'创建队列失败: {create_error}')
                            consecutive_errors += 1
                            await asyncio.sleep(min(consecutive_errors, 5))
                            continue
                    else:
                        logger.error(f'Redis错误: {e}')
                        consecutive_errors += 1
                        await asyncio.sleep(min(consecutive_errors, 5))
                        continue
                        
                except Exception as e:
                    logger.error(f'意外错误: {e}')
                    consecutive_errors += 1
                    await asyncio.sleep(min(consecutive_errors, 5))
                    continue
                
                # 检查messages是否为空
                if not messages:
                    check_backlog = False
                    continue
                    
                check_backlog = False if len(messages[0][1]) == 0 else True

                for message in messages:
                    for event in message[1]:
                        event_id = event[0]
                        event_data = event[1]
                        
                        # 使用通用的消息处理方法
                        result = self._process_message_common(event_id, event_data, queue, event_queue, is_async=True, consumer_name=consumer_name)
                        if isinstance(result, tuple) and result[0] == 'async_put':
                            # 异步放入队列
                            await self._async_put_task(event_queue, result[1])
                        lastid = event_id

        logger.info(f"Starting event listeners for queues: {self.queues}")
        # 使用asyncio创建并发任务
        tasks = []
        for queue in self.queues:
            logger.info(f"Starting listener task for queue: {queue}")
            task = asyncio.create_task(listen_event_by_group(queue))
            tasks.append(task)
        
        # 等待所有任务
        await asyncio.gather(*tasks)
    def read_pending(self, groupname: str, queue: str, asyncio: bool = False):
        client = self.get_redis_client(asyncio)
        prefixed_queue = self.get_prefixed_queue_name(queue)
        return client.xpending(prefixed_queue, groupname)

    def ack(self, queue, event_id, asyncio: bool = False):
        client = self.get_redis_client(asyncio)
        prefixed_queue = self.get_prefixed_queue_name(queue)
        result = client.xack(prefixed_queue, prefixed_queue, event_id)
        # 清理已认领的消息ID
        if event_id in self._claimed_message_ids:
            self._claimed_message_ids.remove(event_id)
        return result
    
    def _recreate_redis_connection(self):
        """重新创建Redis连接"""
        try:
            logger.info("开始重新创建Redis连接...")
            
            # 关闭现有连接
            if hasattr(self.redis_client, 'connection_pool'):
                try:
                    self.redis_client.connection_pool.disconnect()
                except:
                    pass
            
            if hasattr(self.async_redis_client, 'connection_pool'):
                try:
                    self.async_redis_client.connection_pool.disconnect()
                except:
                    pass
            
            # 重新创建连接池和客户端
            from ..core.app import get_redis_pool, get_async_redis_pool
            import redis
            from redis import asyncio as aioredis
            
            redis_url = self._redis_url
            
            # 重新创建同步连接
            pool = get_redis_pool(redis_url)
            new_redis_client = redis.StrictRedis(connection_pool=pool)
            
            # 重新创建异步连接
            async_pool = get_async_redis_pool(redis_url)
            new_async_redis_client = aioredis.StrictRedis(connection_pool=async_pool)
            
            # 测试新连接
            new_redis_client.ping()
            
            # 更新连接
            self.redis_client = new_redis_client
            self.async_redis_client = new_async_redis_client
            
            logger.info("Redis连接已成功重新创建")
            
        except Exception as e:
            logger.error(f"重新创建Redis连接失败: {e}")
            # 如果重新创建失败，尝试重置连接池
            try:
                if hasattr(self.redis_client, 'connection_pool'):
                    self.redis_client.connection_pool.reset()
                if hasattr(self.async_redis_client, 'connection_pool'):
                    self.async_redis_client.connection_pool.reset()
                logger.info("已重置现有连接池")
            except Exception as reset_error:
                logger.error(f"重置连接池失败: {reset_error}")
                
    def _safe_redis_operation(self, operation, *args, max_retries=3, **kwargs):
        """安全的Redis操作，带有重试机制"""
        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError) as e:
                if attempt == max_retries - 1:
                    logger.error(f"Redis操作失败，已重试{max_retries}次: {e}")
                    raise
                
                logger.warning(f"Redis操作失败，第{attempt + 1}次重试: {e}")
                if attempt == 0:  # 第一次失败时重新创建连接
                    self._recreate_redis_connection()
                time.sleep(min(2 ** attempt, 5))  # 指数退避，最多5秒
    
    def cleanup(self):
        """清理EventPool资源"""
        # 只有在有实际资源需要清理时才打印日志
        has_active_resources = False
        
        # 检查是否有活跃的消费者管理器
        if hasattr(self, 'consumer_manager') and self.consumer_manager:
            # 检查消费者管理器是否真的有活动
            if hasattr(self.consumer_manager, '_heartbeat_strategy'):
                strategy = self.consumer_manager._heartbeat_strategy
                if strategy and hasattr(strategy, 'consumer_id') and strategy.consumer_id:
                    has_active_resources = True
        
        if has_active_resources:
            logger.info("Cleaning up EventPool resources...")
            self.consumer_manager.cleanup()
            logger.info("EventPool cleanup completed")
        else:
            # 静默清理
            if hasattr(self, 'consumer_manager') and self.consumer_manager:
                self.consumer_manager.cleanup()