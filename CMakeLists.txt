cmake_minimum_required(VERSION 3.8.3)
project(ublox_driver)

set(CMAKE_BUILD_TYPE "release")
set(CMAKE_CXX_FLAGS "-std=c++11 ")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -Wall -fPIC")

add_definitions("-Wall -g")

# 查找ament_cmake
find_package(ament_cmake REQUIRED)
# 查找ROS 2组件
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(gnss_comm REQUIRED)

message("${gnss_comm_INCLUDE_DIRS}")

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
find_package(Eigen3 REQUIRED)
find_package(Glog REQUIRED)
find_package(Boost REQUIRED COMPONENTS thread atomic system regex)

include_directories(
  ${EIGEN3_INCLUDE_DIR}
  ${GLOG_INCLUDE_DIR}
  ${PROJECT_SOURCE_DIR}/include/${PROJECT_NAME}/
  ${PROJECT_SOURCE_DIR}/third_party/
  ${Boost_INCLUDE_DIRS}
)

add_executable(${PROJECT_NAME} 
              ${PROJECT_SOURCE_DIR}/src/ublox_driver.cpp 
              ${PROJECT_SOURCE_DIR}/src/ublox_message_processor.cpp
              ${PROJECT_SOURCE_DIR}/src/file_loader.cpp
              ${PROJECT_SOURCE_DIR}/src/file_dumper.cpp
              ${PROJECT_SOURCE_DIR}/src/serial_handler.cpp
              ${PROJECT_SOURCE_DIR}/src/socket_handler.cpp
              ${PROJECT_SOURCE_DIR}/third_party/yaml/Yaml.cpp)
ament_target_dependencies(${PROJECT_NAME}
  rclcpp
  std_msgs
  nav_msgs
  sensor_msgs
  gnss_comm
)
target_link_libraries(${PROJECT_NAME} ${GLOG_LIBRARIES} ${Boost_LIBRARIES})

add_executable(sync_system_time ${PROJECT_SOURCE_DIR}/src/sync_system_time.cpp)
ament_target_dependencies(sync_system_time
  rclcpp
  std_msgs
  nav_msgs
  sensor_msgs
  gnss_comm
)
target_link_libraries(sync_system_time ${GLOG_LIBRARIES} ${Boost_LIBRARIES})

install(
  DIRECTORY include/
  DESTINATION include
)

# Install launch files
install(DIRECTORY
  launch config
  DESTINATION share/${PROJECT_NAME}/
)
  
install(
  TARGETS ${PROJECT_NAME}  sync_system_time DESTINATION lib/${PROJECT_NAME}
  ARCHIVE DESTINATION lib/${PROJECT_NAME}
  LIBRARY  DESTINATION lib/${PROJECT_NAME})

ament_package()