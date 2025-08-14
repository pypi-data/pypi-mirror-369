import os
import sys
import time
import json
import signal
import socket
import asyncio
import logging
import threading
import contextlib
import importlib
import multiprocessing
from typing import List
from collections import defaultdict, deque

import redis
from redis import asyncio as aioredis
from watchdog.observers import Observer

from .task import Task
from .event_pool import EventPool
from ..executors import AsyncioExecutor, MultiAsyncioExecutor
from ..monitoring import FileChangeHandler
from ..utils import gen_task_name

logger = logging.getLogger('app')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 尝试导入性能优化库
try:
    import uvloop
    UVLOOP_AVAILABLE = True
    # 自动启用uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.debug("Using uvloop for better performance")
except ImportError:
    UVLOOP_AVAILABLE = False

try:
    import ujson
    # 使用更快的JSON库
    json_loads = ujson.loads
    json_dumps = ujson.dumps
    logger.debug("Using ujson for better JSON performance")
except ImportError:
    json_loads = json.loads
    json_dumps = json.dumps

_on_app_finalizers = set()

# 全局连接池复用
_redis_pools = {}
_async_redis_pools = {}

def get_redis_pool(redis_url: str, max_connections: int = 200):
    """获取或创建Redis连接池"""
    if redis_url not in _redis_pools:
        # 构建socket keepalive选项，仅在Linux上使用
        socket_keepalive_options = {}
        if hasattr(socket, 'TCP_KEEPIDLE'):
            socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
        if hasattr(socket, 'TCP_KEEPINTVL'):
            socket_keepalive_options[socket.TCP_KEEPINTVL] = 3
        if hasattr(socket, 'TCP_KEEPCNT'):
            socket_keepalive_options[socket.TCP_KEEPCNT] = 5
        
        _redis_pools[redis_url] = redis.ConnectionPool.from_url(
            redis_url, 
            decode_responses=True,
            max_connections=max_connections,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            socket_keepalive=True,
            socket_keepalive_options=socket_keepalive_options if socket_keepalive_options else None,
            health_check_interval=30,
            # 优化超时配置以处理高负载
            socket_connect_timeout=10,  # 增加连接超时时间
            socket_timeout=15,          # 增加读取超时时间，避免频繁超时
        )
    return _redis_pools[redis_url]

def get_async_redis_pool(redis_url: str, max_connections: int = 200):
    """获取或创建异步Redis连接池"""
    if redis_url not in _async_redis_pools:
        # 构建socket keepalive选项，仅在Linux上使用
        socket_keepalive_options = {}
        if hasattr(socket, 'TCP_KEEPIDLE'):
            socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
        if hasattr(socket, 'TCP_KEEPINTVL'):
            socket_keepalive_options[socket.TCP_KEEPINTVL] = 3
        if hasattr(socket, 'TCP_KEEPCNT'):
            socket_keepalive_options[socket.TCP_KEEPCNT] = 5
        
        _async_redis_pools[redis_url] = aioredis.ConnectionPool.from_url(
            redis_url,
            decode_responses=True,
            max_connections=max_connections,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            socket_keepalive=True,
            socket_keepalive_options=socket_keepalive_options if socket_keepalive_options else None,
            health_check_interval=30,
            # 优化超时配置以处理高负载
            socket_connect_timeout=10,  # 增加连接超时时间
            socket_timeout=15,          # 增加读取超时时间，避免频繁超时
        )
    return _async_redis_pools[redis_url]


def connect_on_app_finalize(callback):
    """Connect callback to be called when any app is finalized."""
    _on_app_finalizers.add(callback)
    return callback


class Jettask(object):

    def __init__(self, redis_url: str = None, include: list = None, max_connections: int = 200, 
                 consumer_strategy: str = None, consumer_config: dict = None, tasks=None,
                 redis_prefix: str = None) -> None:
        self._tasks = tasks or {}
        self.asyncio = False
        self.include = include or []
        self.redis_url = redis_url
        self.max_connections = max_connections
        self.consumer_strategy = consumer_strategy
        self.consumer_config = consumer_config or {}
        
        # Redis prefix configuration
        self.redis_prefix = redis_prefix or "jettask"
        
        # Update prefixes with the configured prefix using colon namespace
        self.STATUS_PREFIX = f"{self.redis_prefix}:STATUS:"
        self.RESULT_PREFIX = f"{self.redis_prefix}:RESULT:"
        
        # 预编译常用操作，减少运行时开销
        self._json_loads = json_loads
        self._json_dumps = json_dumps
        self._status_prefix = self.STATUS_PREFIX
        self._result_prefix = self.RESULT_PREFIX
        
        # 注册清理处理器
        self._setup_cleanup_handlers()
    
    def _setup_cleanup_handlers(self):
        """设置清理处理器"""
        self._cleanup_done = False
        self._should_exit = False
        self._worker_started = False  # 标记worker是否启动过
        
        def signal_cleanup_handler(signum=None, frame=None):
            """信号处理器"""
            if self._cleanup_done:
                return
            # 只有启动过worker才需要打印清理信息
            if self._worker_started:
                logger.info("Received shutdown signal, cleaning up...")
            self.cleanup()
            if signum:
                # 设置标记表示需要退出
                self._should_exit = True
                # 对于多进程环境，不直接操作事件循环
                # 让执行器自己检测退出标志并优雅关闭
        
        def atexit_cleanup_handler():
            """atexit处理器"""
            if self._cleanup_done:
                return
            # atexit时不重复打印日志，静默清理
            self.cleanup()
        
        # 注册信号处理器
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_cleanup_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, signal_cleanup_handler)
        
        # 注册atexit处理器
        import atexit
        atexit.register(atexit_cleanup_handler)
    
    def cleanup(self):
        """清理应用资源"""
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        # 只有真正启动过worker才打印日志
        if self._worker_started:
            logger.info("Cleaning up Jettask resources...")
            
            # 清理EventPool
            if hasattr(self, 'ep') and self.ep:
                self.ep.cleanup()
            
            logger.info("Jettask cleanup completed")
        else:
            # 如果只是实例化但没有启动，静默清理
            if hasattr(self, 'ep') and self.ep:
                self.ep.cleanup()
            logger.debug("Jettask instance cleanup (no worker started)")
    
    @property
    def consumer_manager(self):
        """获取消费者管理器"""
        return self.ep.consumer_manager if hasattr(self.ep, 'consumer_manager') else None

    @property
    def async_redis(self):
        """优化：复用连接池"""
        name = "_async_redis"
        if hasattr(self, name):
            return getattr(self, name)
        
        pool = get_async_redis_pool(self.redis_url, self.max_connections)
        async_redis = aioredis.StrictRedis(connection_pool=pool)
        setattr(self, name, async_redis)
        return async_redis

    @property
    def redis(self):
        """优化：复用连接池"""
        name = "_redis"
        if hasattr(self, name):
            return getattr(self, name)
            
        pool = get_redis_pool(self.redis_url, self.max_connections)
        redis_cli = redis.StrictRedis(connection_pool=pool)
        setattr(self, name, redis_cli)
        return redis_cli

    @property
    def ep(self):
        name = "_ep"
        if hasattr(self, name):
            ep = getattr(self, name)
        else:
            # 传递redis_prefix到consumer_config
            consumer_config = self.consumer_config.copy() if self.consumer_config else {}
            consumer_config['redis_prefix'] = self.redis_prefix
            
            ep = EventPool(
                self.redis, 
                self.async_redis, 
                redis_url=self.redis_url,
                consumer_strategy=self.consumer_strategy,
                consumer_config=consumer_config,
                redis_prefix=self.redis_prefix
            )
            setattr(self, name, ep)
        return ep

    def clear(self):
        if hasattr(self, "process"):
            delattr(self, "process")
        if hasattr(self, "_ep"):
            delattr(self, "_ep")

    def get_task_by_name(self, name: str) -> Task:
        return self._tasks.get(name)

    def include_module(self, modules: list):
        self.include += modules

    def _task_from_fun(
        self, fun, name=None, base=None, queue=None, bind=False, **options
    ) -> Task:
        name = name or gen_task_name(fun.__name__, fun.__module__)
        base = base or Task
        if name not in self._tasks:
            run = staticmethod(fun)
            task: Task = type(
                fun.__name__,
                (base,),
                dict(
                    {
                        "app": self,
                        "name": name,
                        "run": run,
                        "queue": queue,
                        "bind": bind,
                        "_decorated": True,
                        "__doc__": fun.__doc__,
                        "__module__": fun.__module__,
                        "__annotations__": fun.__annotations__,
                        "__wrapped__": run,
                    },
                    **options,
                ),
            )()
            task.bind_app(self)
            with contextlib.suppress(AttributeError):
                task.__qualname__ = fun.__qualname__
            self._tasks[task.name] = task
        else:
            task = self._tasks[name]
        return task

    def task(
        self,
        name: str = None,
        queue: str = None,
        base: Task = None,
        *args,
        **kwargs,
    ):
        def _create_task_cls(fun):
            return self._task_from_fun(fun, name, base, queue, *args, **kwargs)

        return _create_task_cls

    def _mount_module(self):
        for module in self.include:
            module = importlib.import_module(module)
            for attr_name in dir(module):
                obj = getattr(module, attr_name)
                if hasattr(obj, "app"):
                    self._tasks.update(getattr(obj, "app")._tasks)

    def _validate_tasks_for_executor(self, execute_type: str, queues: List[str]):
        """验证任务类型是否与执行器兼容"""
        if execute_type in ["asyncio", "multi_asyncio"]:
            return  # AsyncIO和MultiAsyncio可以处理异步任务
        
        # 只有Thread执行器不能处理异步任务
        incompatible_tasks = []
        for task_name, task in self._tasks.items():
            # 检查任务是否属于指定队列
            if task.queue not in queues:
                continue
                
            # 检查是否是异步任务
            if asyncio.iscoroutinefunction(task.run):
                incompatible_tasks.append({
                    'name': task_name,
                    'queue': task.queue,
                    'type': 'async'
                })
        
        if incompatible_tasks:
            error_msg = f"\n错误：{execute_type} 执行器不能处理异步任务！\n"
            error_msg += "发现以下异步任务：\n"
            for task in incompatible_tasks:
                error_msg += f"  - {task['name']} (队列: {task['queue']})\n"
            error_msg += f"\n解决方案：\n"
            error_msg += f"1. 使用 asyncio 或 process 执行器\n"
            error_msg += f"2. 或者将这些任务改为同步函数（去掉 async/await）\n"
            error_msg += f"3. 或者将这些任务的队列从监听列表中移除\n"
            raise ValueError(error_msg)
    
    def _start(
        self,
        execute_type: str = "asyncio",
        queues: List[str] = None,
        concurrency: int = 1,
        prefetch_multiplier: int = 1,
        **kwargs
    ):
        # 设置默认队列
        if not queues:
            queues = [self.redis_prefix]
        
        self.ep.queues = queues
        self.ep.init_routing()
        self._mount_module()
        # 验证任务兼容性 
        self._validate_tasks_for_executor(execute_type, queues)
        
        event_queue = deque()
        
        # 创建消费者组
        try:
            self.ep.create_group()
        except Exception as e:
            logger.warning(f"创建消费者组时出错: {e}")
            # 继续执行，listening_event会自动处理
        
        # 根据执行器类型创建对应的执行器
        if execute_type == "asyncio":
            # 对于asyncio执行器，使用asyncio.Queue
            async_event_queue = asyncio.Queue()
            
            async def run_asyncio_executor():
                # 启动异步事件监听
                asyncio.create_task(self.ep.listening_event(async_event_queue, prefetch_multiplier))
                # 创建并运行执行器
                executor = AsyncioExecutor(async_event_queue, self, concurrency)
                await executor.loop()
            
            # try:
            loop = asyncio.get_event_loop()
            # except RuntimeError:
            #     # 如果当前线程没有事件循环，创建一个新的
            #     loop = asyncio.new_event_loop()
            #     asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(run_asyncio_executor())
            except RuntimeError as e:
                if "Event loop stopped" in str(e):
                    logger.info("Event loop stopped, shutting down gracefully")
                else:
                    raise
        elif execute_type == "multi_asyncio":
            # multi_asyncio在每个子进程中会启动自己的监听器
            executor = MultiAsyncioExecutor(event_queue, self, concurrency)
            executor.prefetch_multiplier = prefetch_multiplier
            
            # 设置信号处理器以正确响应Ctrl+C
            def multi_asyncio_signal_handler(signum, _frame):
                logger.info(f"Multi-asyncio mode received signal {signum}")
                executor._main_received_signal = True
                executor.shutdown_event.set()
                # 强制退出主循环
                raise KeyboardInterrupt()
            
            signal.signal(signal.SIGINT, multi_asyncio_signal_handler)
            signal.signal(signal.SIGTERM, multi_asyncio_signal_handler)
            
            try:
                executor.loop()
            except KeyboardInterrupt:
                logger.info("Multi-asyncio mode interrupted")
            finally:
                executor.shutdown()
        else:
            raise ValueError(f"不支持的执行器类型：{execute_type}，仅支持 'asyncio' 和 'multi_asyncio'")

    def _run_subprocess(self, *args, **kwargs):
        logger.info("Started Worker Process")
        process = multiprocessing.Process(target=self._start, args=args, kwargs=kwargs)
        process.start()
        return process

    def start(
        self,
        execute_type: str = "asyncio",
        queues: List[str] = None,
        concurrency: int = 1,
        prefetch_multiplier: int = 1,
        reload: bool = False,
    ):
        # 标记worker已启动
        self._worker_started = True
        
        if execute_type == "multi_asyncio" and self.consumer_strategy == "pod":
            raise ValueError("multi_asyncio模式下无法使用pod策略")
        self.process = self._run_subprocess(
            execute_type=execute_type,
            queues=queues,
            concurrency=concurrency,
            prefetch_multiplier=prefetch_multiplier,
        )
        if reload:
            event_handler = FileChangeHandler(
                self,
                execute_type=execute_type,
                queues=queues,
                concurrency=concurrency,
                prefetch_multiplier=prefetch_multiplier,
            )
            observer = Observer()
            observer.schedule(event_handler, ".", recursive=True)
            observer.start()
        # 使用事件来等待，而不是无限循环
        try:
            while not self._should_exit:
                time.sleep(0.1)  # 短暂睡眠，快速响应退出信号
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.cleanup()
            if self.process and self.process.is_alive():
                self.process.terminate()
                self.process.join(timeout=2)
                if self.process.is_alive():
                    logger.warning("Process did not terminate, killing...")
                    self.process.kill()

    def bulk_write(self, tasks: list, asyncio: bool = False):
        """优化批量写入性能"""
        if not tasks:
            raise ValueError("tasks 参数不能为空！")
            
        # 优化：减少字典操作开销
        task_mapping = {}
        for task in tasks:
            queue = task["queue"]
            if queue not in task_mapping:
                task_mapping[queue] = []
            task_mapping[queue].append(task)
            
        if asyncio:
            return self._bulk_write(task_mapping)
        
        # 优化：批量处理减少网络往返
        event_ids = []
        
        for queue, queue_tasks in task_mapping.items():
            queue_event_ids = self.ep.batch_send_event(queue, queue_tasks)
            event_ids.extend(queue_event_ids)
            
            # 使用新的Hash方式批量设置初始状态
            current_time = str(time.time())
            pipeline = self.redis.pipeline()
            for event_id in queue_event_ids:
                key = f"{self.redis_prefix}:TASK:{event_id}"
                pipeline.hset(key, mapping={
                    "status": "pending",
                    "created_at": current_time
                })
                pipeline.expire(key, 3600)
        
        # 执行pipeline
        if event_ids:
            pipeline.execute()
            
        return event_ids

    async def _bulk_write(self, task_mapping):
        """异步批量写入优化"""
        event_ids = []
        
        for queue, tasks in task_mapping.items():
            queue_event_ids = await self.ep.batch_send_event(queue, tasks, asyncio=True)
            event_ids.extend(queue_event_ids)
            
            # 使用新的Hash方式批量设置初始状态
            current_time = str(time.time())
            pipeline = self.async_redis.pipeline()
            for event_id in queue_event_ids:
                key = f"{self.redis_prefix}:TASK:{event_id}"
                pipeline.hset(key, mapping={
                    "status": "pending",
                    "created_at": current_time
                })
                pipeline.expire(key, 3600)
        
        # 执行pipeline
        if event_ids:
            await pipeline.execute()
            
        return event_ids

    def get_task_status(self, event_id: str, asyncio: bool = False):
        """优化状态获取"""
        client = self.get_redis_client(asyncio)
        key = f"{self._status_prefix}{event_id}"
        ret = client.get(key)
        
        if asyncio:
            return self._get_task_status(ret)
        else:
            return self._json_loads(ret) if ret else None

    async def _get_task_status(self, ret):
        s = await ret
        return self._json_loads(s) if s else None

    def set_task_status(self, event_id: str, status: str, asyncio: bool = False):
        """优化状态设置"""
        client = self.get_redis_client(asyncio)
        key = f"{self._status_prefix}{event_id}"
        # Store status as a JSON object instead of just a string
        status_data = {
            "status": status,
            "updated_at": int(time.time() * 1000)
        }
        return client.set(key, self._json_dumps(status_data), ex=3600)

    def set_task_status_by_batch(self, mapping: dict, asyncio: bool = False):
        """优化批量状态设置"""
        client = self.get_redis_client(asyncio)
        
        # 预构建键值对，减少循环中的字符串操作
        current_time = int(time.time() * 1000)
        redis_mapping = {
            f"{self._status_prefix}{event_id}": self._json_dumps({
                "status": status,
                "updated_at": current_time
            })
            for event_id, status in mapping.items()
        }
        
        return client.mset(redis_mapping)

    def del_task_status(self, event_id: str, asyncio: bool = False):
        client = self.get_redis_client(asyncio)
        return client.delete(f"{self._status_prefix}{event_id}")

    def get_redis_client(self, asyncio: bool = False):
        return self.async_redis if asyncio else self.redis

    def set_data(
        self, event_id: str, result: str, ex: int = 3600, asyncio: bool = False
    ):
        """优化数据设置"""
        client = self.get_redis_client(asyncio)
        key = f"{self._result_prefix}{event_id}"
        return client.set(key, value=result, ex=ex)
    
    async def get_and_delayed_deletion(self, key: str, ex: int):
        client = self.get_redis_client(True)
        result = await client.get(key)
        await client.expire(key, time=ex)
        return result
    
    def get_result(self, event_id: str, delete: bool = False, asyncio: bool = False, delayed_deletion_ex: int = None):
        """优化结果获取"""
        client = self.get_redis_client(asyncio)
        key = f"{self._result_prefix}{event_id}"
        
        if delayed_deletion_ex is not None:
            return self.get_and_delayed_deletion(key, delayed_deletion_ex)
        elif delete:
            return client.getdel(key)
        else:
            return client.get(key)