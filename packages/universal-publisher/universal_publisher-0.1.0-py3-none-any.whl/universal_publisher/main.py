#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64, Int32, Bool, Float64MultiArray
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import time
import math
import random

class UniversalPublisher(Node):
    def __init__(self, mode, data_type, nodename, topic_name, queue_size, delay_period):
        super().__init__(nodename)
        self.bridge = CvBridge()
        self.mode = mode
        self.data_type = data_type

        # Decide publisher type based on mode
        if self.mode in ["image", "video"]:
            self.publisher_ = self.create_publisher(Image, topic_name, queue_size)
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.get_logger().error("Could not open webcam for image/video mode.")
                exit(1)

        elif self.mode == "text":
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
            ret, frame = self.cap.read()
            if not ret:
                self.get_logger().warning("Failed to grab frame")
                return
            ros_image = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            self.publisher_.publish(ros_image)

        elif self.mode == "text":
            msg = String()
            msg.data = "Hello from Universal Publisher!"
            self.publisher_.publish(msg)

        elif self.mode == "number":
            if self.data_type == "float":
                msg = Float64()
                msg.data = time.time() % 100
            else:
                msg = Int32()
                msg.data = int(time.time() % 100)
            self.publisher_.publish(msg)

        elif self.mode == "bool":
            msg = Bool()
            msg.data = int(time.time()) % 2 == 0
            self.publisher_.publish(msg)

        elif self.mode == "multi_float":
            msg = Float64MultiArray()
            latitude = 12.9716 + random.uniform(-0.001, 0.001)
            longitude = 77.5946 + random.uniform(-0.001, 0.001)
            altitude = 900 + random.uniform(-5, 5)
            roll = math.sin(time.time()) * 0.1
            pitch = math.cos(time.time()) * 0.1
            yaw = math.sin(time.time() / 2) * 0.1
            msg.data = [latitude, longitude, altitude, roll, pitch, yaw]
            self.publisher_.publish(msg)

    def destroy_node(self):
        if self.mode in ["image", "video"]:
            self.cap.release()
        super().destroy_node()


def unipub(mode, data_type, nodename, topic_name, queue_size=10, delay_period=0.033):
    rclpy.init()
    node = UniversalPublisher(mode, data_type, nodename, topic_name, queue_size, delay_period)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
