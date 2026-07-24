import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory("xbot_description")
    ros_gz_sim_share = get_package_share_directory("ros_gz_sim")

    xacro_file = os.path.join(package_share, "urdf", "xbot.xacro")
    bridge_config = os.path.join(
        package_share,
        "config",
        "ros_gz_bridge_gazebo.yaml",
    )

    robot_description = xacro.process_file(xacro_file).toxml()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                ros_gz_sim_share,
                "launch",
                "gz_sim.launch.py",
            )
        ),
        launch_arguments={
            "gz_args": "-r -v 4 empty.sdf",
        }.items(),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": True,
            }
        ],
    )

    spawn_robot = TimerAction(
        period=3.0,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="create",
                output="screen",
                arguments=[
                    "-topic",
                    "/robot_description",
                    "-name",
                    "xbot",
                    "-allow_renaming",
                    "false",
                    "-x",
                    "0.0",
                    "-y",
                    "0.0",
                    "-z",
                    "0.05",
                    "-Y",
                    "0.0",
                ],
            )
        ],
    )

    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="ros_gz_bridge",
        output="screen",
        parameters=[
            {
                "config_file": bridge_config,
                "use_sim_time": True,
            }
        ],
    )

    return LaunchDescription(
        [
            SetEnvironmentVariable(
                "LIBGL_ALWAYS_SOFTWARE",
                "1",
            ),
            gazebo,
            robot_state_publisher,
            ros_gz_bridge,
            spawn_robot,
        ]
    )