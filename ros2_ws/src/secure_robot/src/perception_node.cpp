#include <memory>
#include <std_msgs/msg/string.hpp>
#include <geometry_msgs/msg/point_stamped.hpp>
#include "secure_robot/commands.hpp"

class Perception : public rclcpp::Node {
public:
  Perception() : Node("perception_node", secure_robot::node_options())
  {
    publisher_ = create_publisher<geometry_msgs::msg::PointStamped>("/perception/target", 10);
    subscription_ = create_subscription<std_msgs::msg::String>("/camera/frame_meta", 10,
      [this](const std_msgs::msg::String & frame) {
        if (frame.data.find("object_detected=true") == std::string::npos) {return;}
        geometry_msgs::msg::PointStamped target;
        target.header.stamp = now();
        target.header.frame_id = "synthetic_camera";
        target.point.x = 1.2;
        target.point.y = 0.4;
        publisher_->publish(target);
        RCLCPP_INFO(get_logger(), "[PERCEPTION] target detected x=1.20 y=0.40");
      });
  }
private:
  rclcpp::Publisher<geometry_msgs::msg::PointStamped>::SharedPtr publisher_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};
int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Perception>());
  rclcpp::shutdown();
}
