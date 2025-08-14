import rclpy
from rclpy.node import Node
import importlib

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

class GenericPublisher(Node):
    def __init__(self, mode, datatype, node_name, topic_name, value, queue, delay, video_source):
        super().__init__(node_name)

        if mode is None:
            mode = guess_mode_from_type(datatype)
            self.get_logger().info(f"Auto-detected mode: {mode}")
        self.mode = mode
        self.value = value
        self.datatype = datatype

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

        self.publisher_ = self.create_publisher(self.msg_class, topic_name, queue)
        self.timer = self.create_timer(delay, self.timer_callback)

        self.cap = None
        self.bridge = None
        if self.mode in ["image", "video"]:
            from cv_bridge import CvBridge
            import cv2
            self.cv2 = cv2
            self.bridge = CvBridge()
            if self.mode == "video":
                if video_source is None:
                    self.get_logger().error("You must define 'video_source' in config for video mode")
                    rclpy.shutdown()
                    return
                self.cap = cv2.VideoCapture(video_source)

        self.get_logger().info(f"Publishing on '{topic_name}' with type '{module_name}.{class_name}'")

    def timer_callback(self):
        msg = None
        if self.mode in ["number", "float", "string"]:
            msg = self.msg_class()
            if hasattr(msg, 'data'):
                msg.data = self.value
                self.get_logger().info(f"Publishing → {self.value}")
            else:
                self.get_logger().error(f"Message type {self.datatype} has no 'data' field.")
                return
        elif self.mode == "image":
            if self.value is None:
                self.get_logger().error("No image frame provided")
                return
            msg = self.bridge.cv2_to_imgmsg(self.value, encoding="bgr8")
        elif self.mode == "video":
            if not self.cap:
                self.get_logger().error("Video capture not initialized")
                return
            ret, frame = self.cap.read()
            if not ret:
                self.get_logger().info("End of video or camera error")
                rclpy.shutdown()
                return
            msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")

        if msg:
            self.publisher_.publish(msg)

def run_publisher(mode=None, datatype="Float64", node_name="num_publisher",
                  topic_name="number", value=42.5, queue=10, delay=1.0, video_source=None):
    rclpy.init()
    node = GenericPublisher(mode, datatype, node_name, topic_name, value, queue, delay, video_source)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.cap:
            node.cap.release()
        node.destroy_node()
        rclpy.shutdown()
