FROM ros:jazzy-ros-base AS build
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential openssl python3-colcon-common-extensions python3-pytest \
    ros-jazzy-ament-cmake-gtest ros-jazzy-rmw-fastrtps-cpp \
    ros-jazzy-sros2 ros-jazzy-geometry-msgs && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/lab/ros2_ws
COPY ros2_ws/src src
RUN source /opt/ros/jazzy/setup.bash && colcon build --event-handlers console_direct+
COPY scripts /opt/lab/scripts
COPY tests /opt/lab/tests
COPY security/policies /opt/lab/security/policies
COPY security/scripts /opt/lab/security/scripts
COPY config /opt/lab/config
RUN useradd --uid 10001 --create-home lab && chown -R lab:lab /opt/lab
ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
    ROS_DOMAIN_ID=42 \
    FASTRTPS_DEFAULT_PROFILES_FILE=/opt/lab/config/fastdds.xml \
    RCUTILS_LOGGING_BUFFERED_STREAM=0 \
    PYTHONDONTWRITEBYTECODE=1
USER 10001:10001
ENTRYPOINT ["/bin/bash", "/opt/lab/scripts/entrypoint.sh"]
CMD ["ros2", "run", "secure_robot", "camera_node"]
