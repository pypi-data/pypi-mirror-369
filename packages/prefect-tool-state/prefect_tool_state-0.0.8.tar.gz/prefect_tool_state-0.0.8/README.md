# Prefect Tool State

A high-throughput tool state publisher for Prefect tools with optimized batching capabilities.

## Features

- **High-frequency publishing**: Optimized for scenarios where tool state updates are sent after each file is processed
- **Batch optimization**: Collects messages over 1-second intervals and publishes them as a single JSON array
- **Background worker**: Non-blocking interface with async background processing
- **Thread-safe**: Safe to use from multiple threads
- **Automatic resource management**: Handles Redis connection lifecycle automatically

## Installation

```bash
pip install prefect-tool-state
```

## Quick Start

```python
# Quick Start updated for state publisher
from prefect_tool_state import get_tool_state_publisher, ToolStatePublisher, ToolState

# Get the global state publisher instance
publisher = get_tool_state_publisher()

# Publish tool state updates (non-blocking)
state_publisher = get_tool_state_publisher()
tool_state = ToolState(
    tool_run_id="tool-123",
    status="processing",
    current_file="example.txt",
    # ... other fields
)
state_publisher.publish_data(tool_state)
```

## Configuration

The publisher requires Redis messaging environment variables:
- `PREFECT_REDIS_MESSAGING_HOST`: Redis host
- `PREFECT_REDIS_MESSAGING_PASSWORD`: Redis password

## How It Works

1. **Queue-based**: Your calls to `publish_data()` are queued in memory (non-blocking)
2. **Batched publishing**: A background worker wakes up every second to process all queued messages
3. **Optimized payload**: All messages are serialized into a single JSON array and published as one Redis message
4. **Consumer compatibility**: The consumer must handle the batch format (array of tool states)

## Performance

- **Before**: 1000 file updates = 1000 Redis operations
- **After**: 1000 file updates = 1 Redis operation per second
- **Latency**: Sub-millisecond for `publish_data()` calls
- **Throughput**: Handles thousands of updates per second

## License

MIT License
