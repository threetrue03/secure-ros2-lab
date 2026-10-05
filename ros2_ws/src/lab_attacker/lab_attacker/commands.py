"""Pure helpers also testable on a host without ROS."""
COMMAND = (0.80, 1.00)


def validate_scope(environment):
    if environment.get('LAB_SCOPE') != 'secure-ros2-lab-isolated':
        raise RuntimeError('Run only through the isolated lab Compose attacker service')
    if environment.get('ROS_DOMAIN_ID') != '42':
        raise RuntimeError('The controlled participant is restricted to lab domain 42')


def populate_command(message):
    message.linear.x, message.angular.z = COMMAND
    return message
