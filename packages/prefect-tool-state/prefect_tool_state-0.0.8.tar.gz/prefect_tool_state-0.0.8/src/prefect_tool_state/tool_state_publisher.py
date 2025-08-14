import json
import asyncio
from dataclasses import asdict
from typing import Dict, Any, Optional
import os
import threading
from .tool_state import ToolState
from datetime import datetime, timezone

# Prefect/Redis environment detection
_PREFECT_AVAILABLE = False
try:
    from prefect.logging import get_logger
    from prefect_redis.client import get_async_redis_client
    _PREFECT_AVAILABLE = True
except ImportError:
    import logging
    from rich.logging import RichHandler
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                markup=True,
                show_time=True,
                show_level=True,
                show_path=True,
            )
        ]
        )
    def get_logger(name):                    
        return logging.getLogger(name)

logger = get_logger("tool_state_publisher")


class ToolStatePublisher:
    """
    Publishes tool state updates to Redis in the background, batching for efficiency.
    Ensures all messages are published before process exit.
    """
    def __init__(self, topic_name: str = "progress", flush_interval: int = 1, batch_size: int = 20):
        self.topic_name = topic_name
        self.flush_interval = flush_interval
        self.batch_size = batch_size
        self._queue = asyncio.Queue(maxsize=10000)
        self._started = threading.Event()
        self._redis_enabled = (
            _PREFECT_AVAILABLE and os.environ.get("PREFECT_REDIS_MESSAGING_HOST") and os.environ.get("PREFECT_REDIS_MESSAGING_PASSWORD")
        )
        if self._redis_enabled:
            self._start_worker()            
        else:
            logger.warning("Redis messaging not configured or not running in Prefect environment; tool state updates will be logged instead of published.")
    
    def publish_data(self, tool_state: ToolState) -> None:
        self.publish_dict(asdict(tool_state))
        
    def publish_dict(self, tool_state: dict) -> None:
        """Enqueue a tool state update for background publishing or log if not configured."""
        if not self._redis_enabled or not self._started.is_set():
            logger.info(f"ToolState (fallback): {tool_state}")
            return
        try:
            self._queue.put_nowait(tool_state)
        except asyncio.QueueFull:
            logger.warning("Tool state queue is full. Dropping message.")
        except Exception as exc:
            logger.error(f"Failed to queue tool state for publishing: {exc}")

    def shutdown(self):        
        logger.info("Flushing tool state publisher queue and shutting down worker")
        # stop accepting new messages
        if not self._started.is_set():
            return
        self._started.clear()
        try:
            # Signal the worker to stop by putting a sentinel value
            self._queue.put_nowait(None)
        except asyncio.QueueFull:
            pass
        # wait briefly for the worker thread to exit
        self._worker_thread.join(timeout=10)
    
    def _start_worker(self):
        """Start a background thread to run the async worker."""
        if self._started.is_set():
            return
        def run_loop():
            asyncio.run(self._worker())
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
        self._worker_thread = thread
        self._started.set()

    async def _worker(self):
        """Background task that batches and publishes queued messages to Redis."""
        if not self._redis_enabled:
            return
        logger.info("Tool state publisher worker started.")
        running = True
        try:
            while running:
                # Wait for flush_interval or publish early when batch_size reached
                if self._queue.qsize() < self.batch_size:
                    await asyncio.sleep(self.flush_interval)
                batch, running = self._collect_batch()
                if not batch:
                    continue
                await self._publish_batch(batch)
                for _ in batch:
                    self._queue.task_done()
        except asyncio.CancelledError:
            logger.info("Tool state publisher worker cancelled.")
        except Exception:
            logger.error("Tool state publisher worker crashed.", exc_info=True)
        finally:
            # Drain any remaining items in queue before exit
            batch, _ = self._collect_batch()
            while batch:
                await self._publish_batch(batch)
                for _ in batch:
                    self._queue.task_done()
                batch, _ = self._collect_batch()
            logger.info("Tool state publisher worker stopped.")

    def _collect_batch(self):
        """Collects a batch of tool state updates from the queue. Returns (batch, running)."""
        batch = []
        running = True
        # collect up to batch_size items to respect batch limits
        while not self._queue.empty():
            try:
                item = self._queue.get_nowait()
                if item is None:
                    # sentinel: signal shutdown and mark task done
                    running = False
                    self._queue.task_done()
                    break
                batch.append(item)
            except asyncio.QueueEmpty:
                break
        return batch, running

    async def _publish_batch(self, batch):
        """Asynchronously publish a batch of tool state updates to Redis or log as fallback."""
        if not batch:
            return
        logger.info(f"Publishing batch of {len(batch)} tool state updates.")
        if self._redis_enabled:
            try:
                client = get_async_redis_client()
                body = {
                    "schema": "PythonTool", 
                    "data": batch        
                }
                await client.xadd(
                    self.topic_name,
                    {
                        "data": json.dumps(body),
                        "attributes": json.dumps({
                            "event_type": "tool",
                            "count": len(batch),
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })                        
                    }
                )
            except Exception as exc:
                logger.error(f"Failed to publish batch: {exc}")
                for tool_state in batch:
                    logger.info(f"ToolState (fallback): {tool_state}")
        else:
            for tool_state in batch:
                logger.info(f"ToolState (fallback): {tool_state}")


# Global singleton
_tool_state_publisher: Optional[ToolStatePublisher] = None
_lock = threading.Lock()


def get_tool_state_publisher(topic_name: str = "progress", flush_interval: int = 1, batch_size: int = 20) -> ToolStatePublisher:
    """Returns a global ToolStatePublisher, creating it once."""
    global _tool_state_publisher
    if _tool_state_publisher is None:
        with _lock:
            if _tool_state_publisher is None:
                _tool_state_publisher = ToolStatePublisher(topic_name=topic_name, flush_interval=flush_interval, batch_size=batch_size)
    return _tool_state_publisher
