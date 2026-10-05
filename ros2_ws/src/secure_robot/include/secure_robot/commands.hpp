#pragma once

#include <cmath>
#include <string>
#include <geometry_msgs/msg/twist.hpp>
#include <rclcpp/rclcpp.hpp>

namespace secure_robot {
inline rclcpp::NodeOptions node_options()
{
  return rclcpp::NodeOptions().enable_rosout(false)
    .start_parameter_services(false).start_parameter_event_publisher(false);
}

inline geometry_msgs::msg::Twist navigation_command()
{
  geometry_msgs::msg::Twist command;
  command.linear.x = 0.20;
  return command;
}

inline bool finite_command(const geometry_msgs::msg::Twist & c)
{
  return std::isfinite(c.linear.x) && std::isfinite(c.linear.y) &&
    std::isfinite(c.linear.z) && std::isfinite(c.angular.x) &&
    std::isfinite(c.angular.y) && std::isfinite(c.angular.z);
}

// SIMULATION ONLY — NO PHYSICAL MOTOR OUTPUT. Classification is evidence,
// never a security control: Twist has no authenticated publisher identity.
inline std::string command_kind(const geometry_msgs::msg::Twist & c)
{
  if (!finite_command(c)) {return "INVALID";}
  if (c.linear.x == 0.20 && c.angular.z == 0.0) {return "LEGITIMATE_PATTERN";}
  if (c.linear.x == 0.80 && c.angular.z == 1.0) {return "ATTACKER_PATTERN";}
  return "OTHER_PATTERN";
}
}  // namespace secure_robot
