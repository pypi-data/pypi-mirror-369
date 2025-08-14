#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64, Int32, Bool, Float64MultiArray
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class UniversalPublisher(Node):
    def __init__(self, mode, data_type, nodename, topic_name, queue_size, delay_period, value=None):
        super().__init__(nodename)
        self.bridge = CvBridge()
        self.mode = mode
        self.data_type = data_type
        self.value = value

        # Decide publisher type based on mode
        if self.mode in ["image", "video"]:
            self.publisher_ = self.create_publisher(Image, topic_name, queue_size)
            if self.value is None:  # use camera if no image provided
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    self.get_logger().error("Could not open webcam for image/video mode.")
                    exit(1)

        elif self.mode == "string":
            self.publisher_ = self.create_publisher(String, topic_name, queue_size)

        elif self.mode == "number":
            if self.data_type == "float":
                self.publisher_ = self.create_publisher(Float64, topic_name, queue_size)
            else:
                self.publisher_ = self.create_publisher(Int32, topic_name, queue_size)

        elif self.mode == "bool":
            self.publisher_ = self.create_publisher(Bool, topic_name, queue_size)

        elif self.mode == "multi_float":
            self.publisher_ = self.create_publisher(Float64MultiArray, topic_name, queue_size)

        else:
            self.get_logger().error(f"Unknown mode: {self.mode}")
            exit(1)

        period = delay_period if delay_period is not None else 0.1
        self.timer = self.create_timer(period, self.timer_callback)
        self.get_logger().info(f"Publisher started in '{self.mode}' mode on /{topic_name}")

    def timer_callback(self):
        if self.mode in ["image", "video"]:
            if self.value is not None:  # publish given image frame
                frame = self.value
            else:  # capture from webcam
                ret, frame = self.cap.read()
                if not ret:
                    self.get_logger().warning("Failed to grab frame")
                    return
            ros_image = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            self.publisher_.publish(ros_image)

        elif self.mode == "string":
            if self.value is not None:
                msg = String()
                msg.data = str(self.value)
                self.publisher_.publish(msg)
            else:
                self.get_logger().warning("No value provided for string mode.")

        elif self.mode == "number":
            if self.value is not None:
                if self.data_type == "float":
                    msg = Float64()
                    msg.data = float(self.value)
                else:
                    msg = Int32()
                    msg.data = int(self.value)
                self.publisher_.publish(msg)
            else:
                self.get_logger().warning("No value provided for number mode.")

        elif self.mode == "bool":
            if self.value is not None:
                msg = Bool()
                msg.data = bool(self.value)
                self.publisher_.publish(msg)
            else:
                self.get_logger().warning("No value provided for bool mode.")

        elif self.mode == "multi_float":
            if self.value is not None:
                msg = Float64MultiArray()
                msg.data = list(map(float, self.value))
                self.publisher_.publish(msg)
            else:
                self.get_logger().warning("No value provided for multi_float mode.")

    def destroy_node(self):
        if self.mode in ["image", "video"] and self.value is None:
            self.cap.release()
        super().destroy_node()


def unipub(mode, data_type="none", nodename="universal_publisher", topic_name="my_topic",
           queue_size=10, delay_period=0.033, value=None):
    rclpy.init()
    node = UniversalPublisher(mode, data_type, nodename, topic_name, queue_size, delay_period, value)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


__all__ = ["unipub"]
