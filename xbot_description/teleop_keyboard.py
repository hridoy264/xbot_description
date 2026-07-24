#!/usr/bin/env python3

import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__("xbot_keyboard_teleop")

        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)

        self.linear_speed = 0.20
        self.angular_speed = 1.00

        self.settings = termios.tcgetattr(sys.stdin)

        self.get_logger().info(
            "\n"
            "XBot keyboard control\n"
            "---------------------\n"
            "W: forward\n"
            "S: backward\n"
            "A: turn left\n"
            "D: turn right\n"
            "Space: stop\n"
            "Q: quit"
        )

    def get_key(self):
        tty.setraw(sys.stdin.fileno())

        ready, _, _ = select.select([sys.stdin], [], [], 0.1)
        key = sys.stdin.read(1) if ready else ""

        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            self.settings,
        )

        return key

    def publish_velocity(self, linear_x=0.0, angular_z=0.0):
        message = Twist()
        message.linear.x = linear_x
        message.angular.z = angular_z
        self.publisher.publish(message)

    def run(self):
        try:
            while rclpy.ok():
                key = self.get_key().lower()

                if key == "w":
                    self.publish_velocity(self.linear_speed, 0.0)

                elif key == "s":
                    self.publish_velocity(-self.linear_speed, 0.0)

                elif key == "a":
                    self.publish_velocity(0.0, self.angular_speed)

                elif key == "d":
                    self.publish_velocity(0.0, -self.angular_speed)

                elif key == " ":
                    self.publish_velocity()

                elif key == "q":
                    break

                rclpy.spin_once(self, timeout_sec=0.0)

        finally:
            self.publish_velocity()

            termios.tcsetattr(
                sys.stdin,
                termios.TCSADRAIN,
                self.settings,
            )


def main(args=None):
    rclpy.init(args=args)

    node = KeyboardTeleop()

    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()