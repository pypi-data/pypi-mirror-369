import ujson
import time
from dataclasses import dataclass
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .app import Jettask


@dataclass
class ExecuteResponse:
    delay: Optional[float] = None 
    urgent_retry: bool = False 
    reject: bool = False
    retry_time: Optional[float] = None


class Request:
    id: str = None
    name: str = None
    app: "Jettask" = None

    def __init__(self, *args, **kwargs) -> None:
        self._update(*args, **kwargs)

    def _update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)


class Task:
    _app: "Jettask" = None
    name: str = None
    queue: str = None
    bind: bool = False
    trigger_time: float = None

    def __call__(self, event_id: str, trigger_time: float, *args: Any, **kwds: Any) -> Any:
        if self.bind:
            request = Request(id=event_id, name=self.name, app=self._app, trigger_time=trigger_time)
            args = [request] + list(args)
        return self.run(*args, **kwds)

    def run(self, *args, **kwargs):
        """The body of the task executed by workers."""
        raise NotImplementedError("Tasks must define the run method.")

    @classmethod
    def bind_app(cls, app):
        cls._app = app

    def apply_async(
        self,
        args: tuple = None,
        kwargs: dict = None,
        queue: str = None,
        at_once: bool = True,
        asyncio: bool = False,
        routing: dict = None,
    ):
        queue = queue or self.queue
        message = {
            "queue": queue,
            "name": self.name,
            "args": ujson.dumps(args or ()),
            "kwargs": ujson.dumps(kwargs or {}),
            'trigger_time': time.time()
        }
        if routing:
           message['routing'] = ujson.dumps(routing or {})
        if not at_once:
            return message
        if asyncio:
            return self._send_task(queue, message)
        else:
            return self.send_task(queue, message)

    def on_before(self, event_id, pedding_count, args, kwargs) -> ExecuteResponse:
        return ExecuteResponse()

    def on_end(self, event_id, pedding_count, args, kwargs, result) -> ExecuteResponse:
        return ExecuteResponse()

    def on_success(self, event_id, args, kwargs, result) -> ExecuteResponse:
        return ExecuteResponse()

    def send_task(self, queue, message):
        event_id = self._app.ep.send_event(queue, message, False)
        # 使用新的Hash方式设置初始状态
        key = f"{self._app.ep.redis_prefix or 'jettask'}:TASK:{event_id}"
        self._app.redis.hset(key, mapping={
            "status": "pending",
            "created_at": str(time.time())
        })
        self._app.redis.expire(key, 3600)
        return event_id

    async def _send_task(self, queue, message):
        event_id = await self._app.ep.send_event(queue, message, True)
        # 使用新的Hash方式设置初始状态
        key = f"{self._app.ep.redis_prefix or 'jettask'}:TASK:{event_id}"
        await self._app.async_redis.hset(key, mapping={
            "status": "pending",
            "created_at": str(time.time())
        })
        await self._app.async_redis.expire(key, 3600)
        return event_id

    def read_pending(
        self,
        queue: str = None,
        asyncio: bool = False,
    ):
        queue = queue or self.queue
        if asyncio:
            return self._get_pending(queue)
        return self._app.ep.read_pending(queue, queue)

    async def _get_pending(self, queue: str):
        return await self._app.ep.read_pending(queue, queue, asyncio=True)