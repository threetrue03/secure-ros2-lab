"""Simulation-only publication, no scanning, targeting, or hardware access."""
import os
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

from .commands import populate_command, validate_scope


class LabAttacker(Node):
    def __init__(self):
        super().__init__('attacker_node', enable_rosout=False, start_parameter_services=False)
        self.status = self.create_publisher(String, '/lab/attacker/status', 10)
        self.started = time.monotonic()
        self.publisher = None
        self.attempted = False
        self.status_timer = self.create_timer(1.0, self.report_status)
        self.command_timer = self.create_timer(0.2, self.attempt_command)

    def report_status(self):
        self.status.publish(String(data='lab participant active'))
        self.get_logger().info('[LAB ATTACKER] permitted status heartbeat published')

    def attempt_command(self):
        # Allow the permitted heartbeat to match first. A denial must not be
        # confused with an identity failure or a dead attacker container.
        if time.monotonic() - self.started < 5.0:
            return
        if not self.attempted:
            self.attempted = True
            self.get_logger().info('[LAB ATTACKER] attempting unauthorized /cmd_vel publication')
            self.get_logger().info(f'[LAB ATTACKER] discovered nodes: {self.get_node_names()}')
            self.get_logger().info(f'[LAB ATTACKER] discovered topics: {self.get_topic_names_and_types()}')
            try:
                self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
            except Exception as error:
                # Print the actual middleware exception, never a fabricated denial.
                self.get_logger().error(f'[LAB ATTACKER] publisher creation failed: {error}')
                return
        if self.publisher is not None:
            try:
                self.publisher.publish(populate_command(Twist()))
                self.get_logger().info('[LAB ATTACKER] publish API returned linear.x=0.80 angular.z=1.00')
            except Exception as error:
                self.get_logger().error(f'[LAB ATTACKER] publish API failed: {error}')
                self.command_timer.cancel()


def main(args=None):
    validate_scope(os.environ)
    rclpy.init(args=args)
    node = None
    try:
        node = LabAttacker()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
