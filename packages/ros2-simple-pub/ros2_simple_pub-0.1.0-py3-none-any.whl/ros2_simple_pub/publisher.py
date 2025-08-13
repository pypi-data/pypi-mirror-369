#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int64, Float64, String

# Supported message mappings
MESSAGE_TYPES = {
    "Int64": Int64,
    "Float64": Float64,
    "String": String
}

def run_publisher(msg_type="Int64", topic_name="number", queue_size=10, publish_value=0, publish_period=1.0):
    """Run a ROS2 publisher with given settings."""
    rclpy.init()

    msg_class = MESSAGE_TYPES.get(msg_type)
    if msg_class is None:
        raise ValueError(f"Unsupported message type: {msg_type}")

    node = rclpy.create_node(f"{topic_name}_publisher")
    pub = node.create_publisher(msg_class, topic_name, queue_size)

    msg = msg_class()
    msg.data = publish_value

    def timer_callback():
        pub.publish(msg)
        node.get_logger().info(f"Publishing: {msg.data}")

    node.create_timer(publish_period, timer_callback)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
