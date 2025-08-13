ros2_simple_sub

A simple, configurable ROS2 subscriber Python package.

Usage:

from ros2_simple_sub import run_subscriber

received_messages = []

# Run subscriber with defaults
run_subscriber(storage=received_messages)

print("Received messages:", received_messages)

You can override defaults:

run_subscriber(
    node_name="custom_node",
    msg_type="Float64",
    topic_name="sensor_data",
    queue_size=5,
    storage=received_messages,
)
