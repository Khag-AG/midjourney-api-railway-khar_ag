import asyncio
from collections import deque
from os import getenv
from typing import ParamSpec, Callable, Any, Dict, List, Deque
from loguru import logger
from exceptions import QueueFullError
import threading

P = ParamSpec("P")

class Task:
    def __init__(
        self, func: Callable[P, Any], args: P.args, kwargs: P.kwargs
    ) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    async def __call__(self) -> None:
        if asyncio.iscoroutinefunction(self.func):
            return await self.func(*self.args, **self.kwargs)
        else:
            return self.func(*self.args, **self.kwargs)

    def __repr__(self) -> str:
        return f"{self.func.__name__}({self.args}, {self.kwargs})"

class TaskQueue:
    def __init__(self, concur_size: int, wait_size: int) -> None:
        self._concur_size = concur_size
        self._wait_size = wait_size
        self._wait_queue: Deque[Dict[str, Task]] = deque()
        self._concur_queue: List[str] = []

    def put(
            self,
            trigger_id: str,
            func: Callable[P, Any],
            *args: P.args,
            **kwargs: P.kwargs
    ) -> None:
        if len(self._wait_queue) >= self._wait_size:
            raise QueueFullError(f"Task queue is full: {self._wait_size}")
        self._wait_queue.append({
            trigger_id: Task(func, args, kwargs)
        })
        while self._wait_queue and len(self._concur_queue) < self._concur_size:
            self._exec()

    def pop(self, trigger_id: str) -> None:
        if trigger_id in self._concur_queue:
            self._concur_queue.remove(trigger_id)
        if self._wait_queue:
            self._exec()

    def _exec(self):
        key, task = self._wait_queue.popleft().popitem()
        self._concur_queue.append(key)
        logger.debug(f"Task[{key}] start execution: {task}")
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            def run_in_thread():
                asyncio.run(task())
            thread = threading.Thread(target=run_in_thread, daemon=True)
            thread.start()
            return
        
        tsk = loop.create_task(task())

    def concur_size(self):
        return self._concur_size

    def wait_size(self):
        return self._wait_size

    def clear_wait(self):
        self._wait_queue.clear()

    def clear_concur(self):
        self._concur_queue.clear()

taskqueue = TaskQueue(
    int(getenv("CONCUR_SIZE") or 9999),
    int(getenv("WAIT_SIZE") or 9999),
)
