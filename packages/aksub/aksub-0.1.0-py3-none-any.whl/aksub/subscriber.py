import rclpy
from rclpy.node import Node
import importlib

# Global so __init__.py can expose it
from . import received_value as _received_value

TYPE_MAP = {
    "String": "std_msgs.msg",
    "Int32": "std_msgs.msg",
    "Float32": "std_msgs.msg",
    "Float64": "std_msgs.msg",
    "Bool": "std_msgs.msg",
    "Image": "sensor_msgs.msg",
}

def guess_mode_from_type(dtype):
    if dtype.lower() == "image":
        return "image"
    elif dtype.lower() == "string":
        return "string"
    elif dtype.lower().startswith(("float", "int")) or dtype.lower() == "bool":
        return "number"
    return "string"

class GenericSubscriber(Node):
    def __init__(self, mode, datatype, node_name, topic_name, queue, delay):
        super().__init__(node_name)

        if mode is None:
            mode = guess_mode_from_type(datatype)
            self.get_logger().info(f"Auto-detected mode: {mode}")
        self.mode = mode

        # Load message class
        if "." in datatype:
            module_name, class_name = datatype.rsplit('.', 1)
        else:
            class_name = datatype
            module_name = TYPE_MAP.get(class_name)
            if not module_name:
                self.get_logger().error(
                    f"Unknown datatype '{datatype}'. Please specify full path like 'pkg.msg.TypeName'"
                )
                rclpy.shutdown()
                return

        msg_module = importlib.import_module(module_name)
        self.msg_class = getattr(msg_module, class_name)

        # Create subscriber
        self.subscription = self.create_subscription(
            self.msg_class,
            topic_name,
            self.listener_callback,
            queue
        )
        self.subscription  # prevent unused variable warning

        self.bridge = None
        if self.mode in ["image", "video"]:
            from cv_bridge import CvBridge
            self.bridge = CvBridge()

        self.get_logger().info(f"Subscribed to '{topic_name}' with type '{module_name}.{class_name}'")

    def listener_callback(self, msg):
        global _received_value

        if self.mode in ["number", "float", "string"]:
            if hasattr(msg, 'data'):
                _received_value = msg.data
                self.get_logger().info(f"Received: {msg.data}")
        elif self.mode == "image":
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            _received_value = frame
            self.get_logger().info(f"Received [Image frame]")
        else:
            _received_value = msg
            self.get_logger().info(f"Received message object")

def run_subscriber(mode=None, datatype="Float64", node_name="num_subscriber",
                   topic_name="number", queue=10, delay=1.0):
    rclpy.init()
    node = GenericSubscriber(mode, datatype, node_name, topic_name, queue, delay)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
