#include <chrono>
#include <memory>
#include <string>
#include <std_msgs/msg/string.hpp>
#include "secure_robot/commands.hpp"

class Camera : public rclcpp::Node {
public:
  Camera() : Node("camera_node", secure_robot::node_options())
  {
    publisher_ = create_publisher<std_msgs::msg::String>("/camera/frame_meta", 10);
    timer_ = create_wall_timer(std::chrono::milliseconds(1000), [this]() {
      std_msgs::msg::String message;
      message.data = "frame_id=" + std::to_string(++frame_) +
        " object_detected=true confidence=0.93";
      publisher_->publish(message);
      RCLCPP_INFO(get_logger(), "[CAMERA] published %s", message.data.c_str());
    });
  }
private:
  unsigned long frame_{0};
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};
int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Camera>());
  rclcpp::shutdown();
}
