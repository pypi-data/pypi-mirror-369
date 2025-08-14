import rclpy
from rclpy.node import Node
import importlib
import time

TYPE_MAP = {
    "String": "std_msgs.msg",
    "Int32": "std_msgs.msg",
    "Float32": "std_msgs.msg",
    "Float64": "std_msgs.msg",
    "Bool": "std_msgs.msg",
    "Image": "sensor_msgs.msg",
}

received_value = None  # Global to store latest received message


def guess_mode_from_type(dtype):
    if dtype.lower() == "image":
        return "image"
    elif dtype.lower() == "string":
        return "string"
    elif dtype.lower().startswith(("float", "int")) or dtype.lower() == "bool":
        return "number"
    return "string"


class GenericSubscriber(Node):
    def __init__(self, datatype, topic_name, mode, queue, delay, node_name):
        super().__init__(node_name)
        self.delay = delay
        self.last_time = 0

        if mode is None:
            mode = guess_mode_from_type(datatype)
            self.get_logger().info(f"Auto-detected mode: {mode}")

        if "." in datatype:
            module_name, class_name = datatype.rsplit(".", 1)
        else:
            class_name = datatype
            module_name = TYPE_MAP.get(class_name)
            if not module_name:
                self.get_logger().error(f"Unknown datatype '{datatype}'")
                rclpy.shutdown()
                return

        msg_module = importlib.import_module(module_name)
        self.msg_class = getattr(msg_module, class_name)

        self.subscription = self.create_subscription(
            self.msg_class,
            topic_name,
            self.listener_callback,
            queue
        )

        self.mode = mode
        self.get_logger().info(
            f"Subscribed to '{topic_name}' with type '{module_name}.{class_name}'"
        )

    def listener_callback(self, msg):
        global received_value
        now = time.time()
        if now - self.last_time < self.delay:
            return
        self.last_time = now

        if self.mode in ["number", "string"]:
            received_value = msg.data
            self.get_logger().info(f"Received: {received_value}")
        elif self.mode in ["image", "video"]:
            from cv_bridge import CvBridge
            bridge = CvBridge()
            received_value = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            self.get_logger().info("Received [Image frame]")


def run_subscriber(datatype, topic_name, mode=None, queue=10, delay=1.0, node_name="generic_subscriber"):
    rclpy.init()
    node = GenericSubscriber(datatype, topic_name, mode, queue, delay, node_name)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


def metadata(**kwargs):
    run_subscriber(
        datatype=kwargs.get("datatype", "String"),
        topic_name=kwargs.get("topic_name", "chatter"),
        mode=kwargs.get("mode", None),
        queue=kwargs.get("queue", 10),
        delay=kwargs.get("delay", 1.0),
        node_name=kwargs.get("node_name", "generic_subscriber")
    )


def main():
    """
    This allows running:
        python3 subscriber.py
    or
        ros2 run aksub subscriber
    """
    import argparse

    parser = argparse.ArgumentParser(description="Generic ROS2 Subscriber")
    parser.add_argument("--datatype", type=str, default="String", help="Message type (e.g. String, Int32, Image)")
    parser.add_argument("--topic", type=str, default="chatter", help="Topic name")
    parser.add_argument("--mode", type=str, default=None, help="Mode (string, number, image, video)")
    parser.add_argument("--queue", type=int, default=10, help="Queue size")
    parser.add_argument("--delay", type=float, default=1.0, help="Processing delay in seconds")
    parser.add_argument("--node-name", type=str, default="generic_subscriber", help="ROS2 node name")

    args = parser.parse_args()

    run_subscriber(
        datatype=args.datatype,
        topic_name=args.topic,
        mode=args.mode,
        queue=args.queue,
        delay=args.delay,
        node_name=args.node_name
    )


if __name__ == "__main__":
    main()
