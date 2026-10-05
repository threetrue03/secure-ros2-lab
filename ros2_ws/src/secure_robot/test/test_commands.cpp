#include <limits>
#include <gtest/gtest.h>
#include "secure_robot/commands.hpp"

TEST(Navigation, RecognizableCommand)
{
  const auto command = secure_robot::navigation_command();
  EXPECT_DOUBLE_EQ(command.linear.x, 0.20);
  EXPECT_DOUBLE_EQ(command.angular.z, 0.0);
  EXPECT_DOUBLE_EQ(command.linear.y, 0.0);
  EXPECT_EQ(secure_robot::command_kind(command), "LEGITIMATE_PATTERN");
}
TEST(Motor, RecordsConflictingCommandWithoutFilteringIt)
{
  auto command = secure_robot::navigation_command();
  command.linear.x = 0.80;
  command.angular.z = 1.0;
  EXPECT_EQ(secure_robot::command_kind(command), "ATTACKER_PATTERN");
  command.linear.x = 0.35;
  EXPECT_EQ(secure_robot::command_kind(command), "OTHER_PATTERN");
  command.angular.y = std::numeric_limits<double>::quiet_NaN();
  EXPECT_FALSE(secure_robot::finite_command(command));
  EXPECT_EQ(secure_robot::command_kind(command), "INVALID");
}
