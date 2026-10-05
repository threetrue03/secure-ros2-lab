from types import SimpleNamespace
import pytest
from lab_attacker.commands import populate_command, validate_scope


def test_conflicting_command():
    message = SimpleNamespace(linear=SimpleNamespace(x=0.0), angular=SimpleNamespace(z=0.0))
    assert populate_command(message) is message
    assert (message.linear.x, message.angular.z) == (0.8, 1.0)


@pytest.mark.parametrize('environment', [{}, {'LAB_SCOPE': 'secure-ros2-lab-isolated'},
    {'LAB_SCOPE': 'secure-ros2-lab-isolated', 'ROS_DOMAIN_ID': '0'}])
def test_scope_rejects_other_environment(environment):
    with pytest.raises(RuntimeError):
        validate_scope(environment)


def test_scope_accepts_lab():
    validate_scope({'LAB_SCOPE': 'secure-ros2-lab-isolated', 'ROS_DOMAIN_ID': '42'})
