from setuptools import setup

setup(
    name='lab_attacker', version='0.1.0', packages=['lab_attacker'],
    data_files=[('share/ament_index/resource_index/packages', ['resource/lab_attacker']),
                ('share/lab_attacker', ['package.xml'])],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='Secure ROS2 Lab contributors', maintainer_email='maintainer@example.invalid',
    description='Isolated local lab command publisher', license='MIT',
    tests_require=['pytest'],
    entry_points={'console_scripts': ['attacker_node = lab_attacker.attacker_node:main']},
)
