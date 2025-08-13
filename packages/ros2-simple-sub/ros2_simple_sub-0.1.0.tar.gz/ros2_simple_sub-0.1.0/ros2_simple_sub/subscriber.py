import rclpy
from example_interfaces.msg import Int64, Float64, String

# Default configuration — user can edit these before importing/running
NODE_NAME = "number_subscriber"
MSG_TYPE = "Int64"
TOPIC_NAME = "number"
QUEUE_SIZE = 10

MESSAGE_TYPES = {
    "Int64": Int64,
    "Float64": Float64,
    "String": String,
}

def run_subscriber(
    node_name=NODE_NAME,
    msg_type=MSG_TYPE,
    topic_name=TOPIC_NAME,
    queue_size=QUEUE_SIZE,
    storage=None,
):
    rclpy.init()
    node = rclpy.create_node(node_name)

    msg_class = MESSAGE_TYPES.get(msg_type)
    if msg_class is None:
        raise ValueError(f"Unsupported message type: {msg_type}")

    if storage is None:
        storage = []

    def callback(msg):
        storage.append(msg.data)
        node.get_logger().info(f"Received: {msg.data}")

    node.create_subscription(msg_class, topic_name, callback, queue_size)
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

    return storage
