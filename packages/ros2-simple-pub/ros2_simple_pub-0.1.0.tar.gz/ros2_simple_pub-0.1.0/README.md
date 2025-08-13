# ros2_simple_pub

A minimal configurable ROS2 publisher.

## Usage
```python
from ros2_simple_pub import run_publisher

run_publisher(
    msg_type="Int64",
    topic_name="number",
    queue_size=10,
    publish_value=5,
    publish_period=0.5
)
