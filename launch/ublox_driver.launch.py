from launch import LaunchDescription
from launch_ros.actions import Node
# from launch.substitutions import FindPackageShare, PathJoinSubstitution
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # 定义 config_path 参数，使用 FindPackageShare 找到包的路径并拼接配置文件的相对路径
    config_path = os.path.join(get_package_share_directory('ublox_driver'),"config","driver_config.yaml")
    print(f"{config_path} Exists ? :{os.path.exists(config_path)}")
    
    # 创建 LaunchDescription 对象
    ld = LaunchDescription()
    
    # 添加 Node 元素
    ublox_driver_node = Node(
        package='ublox_driver',
        executable='ublox_driver',
        name='ublox_driver',
        output='both',
        parameters=[
            {'config_file': config_path}
        ]
    )
    
    # 将 Node 元素添加到 LaunchDescription 中
    ld.add_action(ublox_driver_node)
    
    return ld