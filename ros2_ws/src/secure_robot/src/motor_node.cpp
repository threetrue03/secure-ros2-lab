#include <memory>
#include <std_msgs/msg/string.hpp>
#include "secure_robot/commands.hpp"

// SIMULATION ONLY — NO PHYSICAL MOTOR OUTPUT. No device APIs are used.
class Motor : public rclcpp::Node {
public:
  Motor() : Node("motor_node", secure_robot::node_options())
  {
    RCLCPP_INFO(get_logger(), "[MOTOR] SIMULATION ONLY — NO PHYSICAL MOTOR OUTPUT");
    commands_ = create_subscription<geometry_msgs::msg::Twist>("/cmd_vel", 10,
      [this](const geometry_msgs::msg::Twist & command) {
        RCLCPP_INFO(get_logger(),
          "[MOTOR] command received linear.x=%.2f angular.z=%.2f kind=%s",
          command.linear.x, command.angular.z, secure_robot::command_kind(command).c_str());
      });
    status_ = create_subscription<std_msgs::msg::String>("/lab/attacker/status", 10,
      [this](const std_msgs::msg::String & status) {
        RCLCPP_INFO(get_logger(), "[MOTOR] lab status received: %s", status.data.c_str());
      });
  }
private:
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr commands_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr status_;
};
int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Motor>());
  rclcpp::shutdown();
}
