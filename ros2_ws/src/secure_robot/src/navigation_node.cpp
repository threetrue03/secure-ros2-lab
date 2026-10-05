#include <memory>
#include <geometry_msgs/msg/point_stamped.hpp>
#include "secure_robot/commands.hpp"

class Navigation : public rclcpp::Node {
public:
  Navigation() : Node("navigation_node", secure_robot::node_options())
  {
    publisher_ = create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
    subscription_ = create_subscription<geometry_msgs::msg::PointStamped>("/perception/target", 10,
      [this](const geometry_msgs::msg::PointStamped & target) {
        if (!std::isfinite(target.point.x) || !std::isfinite(target.point.y)) {return;}
        publisher_->publish(secure_robot::navigation_command());
        RCLCPP_INFO(get_logger(), "[NAVIGATION] publishing /cmd_vel linear.x=0.20 angular.z=0.00");
      });
  }
private:
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  rclcpp::Subscription<geometry_msgs::msg::PointStamped>::SharedPtr subscription_;
};
int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Navigation>());
  rclcpp::shutdown();
}
