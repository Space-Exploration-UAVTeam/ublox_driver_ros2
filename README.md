# ublox_driver for ROS2
[**The original README file of this project is here.**](README_old.md)

**All changes made are shown in bold or pre-stated.**

**Additional records in Chinese while debuging this repo and the F9P receivers is provided [here(through Tencent Docs)](https://docs.qq.com/doc/DVkF6d3RYVWtGQXBG)**

**Authors/Maintainers:** CAO Shaozu (shaozu.cao AT gmail.com)

The *ublox_driver* provides essential functionalities for u-blox GNSS receivers. This package is originally designed for [u-blox ZED-F9P module](https://www.u-blox.com/en/product/zed-f9p-module) according to the specification [UBX-18010854](https://www.u-blox.com/en/docs/UBX-18010854), but should also be compatible to other 8-series or 9-series u-blox receivers as long as the interface is the same.

The following diagram shows all possible input and output options supported by *ublox_driver*.

![ublox_driver diagram!](/figures/ublox_driver_diagram.svg "ublox_driver_diagram")

## 1. Prerequisites

### 1.1 C++11 Compiler
This package requires some features of C++11.

### 1.2 ROS
This package is developed under **[ROS2 Galactic](https://docs.ros.org/en/galactic/index.html)** environment.

### 1.3 Eigen
We use [Eigen 3.3.3](https://gitlab.com/libeigen/eigen/-/archive/3.3.3/eigen-3.3.3.zip) for matrix manipulation.

### 1.4 Boost
Our software utilizes [Boost](https://www.boost.org/) library for serial and socket manipulation. Using command `sudo apt-get install libboost-all-dev` to install *Boost*.

### 1.5 **gnss_comm_interfaces & gnss_comm(all changed)**
This package also requires [gnss_comm_interfaces](https://github.com/Space-Exploration-UAVTeam/gnss_comm_interfaces) for ROS2 message definitions and [gnss_comm(ros2 version)](https://github.com/Space-Exploration-UAVTeam/gnss_comm) for some utility functions. Follow the instructions in [gnss_comm(ros2 version)](https://github.com/Space-Exploration-UAVTeam/gnss_comm##1-prerequisites) to build the two packages.

## 2. Build ublox_driver
Clone the repository to your colcon workspace (for example `~/colcon_ws/`). Make sure gnss_comm and gnss_comm_interfaces are placed under `~/colcon_ws` and successfully built and sourced:
```
cd ~/colcon_ws/src/
git clone https://github.com/Space-Exploration-UAVTeam/ublox_driver_ros2.git "./ublox_driver"
```
Then build the package with:
```
cd ~/colcon_ws/
colcon build --symlink-install --packages-select ublox_driver
source ~/colcon_ws/install/setup.bash
```
## 3. Run with your u-blox receiver **(changed)**
Our software can take the serial stream from the u-blox receiver as an input source. 

Before running the package, you need to configure your receiver using [u-center](https://www.u-blox.com/en/product/u-center) to output at least `UBX-RXM-RAWX`, `UBX-RXM-SFRBX` and `UBX-NAV-PVT` messages to a specific serial port (a sample config used in our system can be found at *config/ucenter_config_f9p_gvins.txt*). In u-center, you have to 
+ click `View` -> `Message View` to enable the three message 
+ click `View` -> `Configuration View` -> `CFG(configuration)` -> `Save current configuration` -> `select all the four devices` -> `Send`

to finish the configuration.

Then connecting your computer(Linux) with the receiver, make sure the serial port appears as a file in the `/dev/` directory. Then add your account to `dialout` group to obtain permission on serial r/w operation via (no need to substitute $USER):
```
sudo usermod -aG dialout $USER
```
Open *config/driver_config.yaml*, set `online` and `to_ros` to 1, and adjust `input_serial_port` and `serial_baud_rate` according to your setting. Run the package with:
```
ros2 launch ublox_driver ublox_driver.launch.py
```

Open another terminal, echo the ROS message by:
```
ros2 topic echo /ublox_driver/receiver_pvt
```
or
```
ros2 topic echo /ublox_driver/receiver_pvt
```
If everything goes smoothly, there should be some ROS messages coming out. Note that some ROS topics remain inactive until the receiver gets GNSS signals. 

Besides the ROS message, you can record the serial stream to a file(`to_file` option) or forward the stream to another serial port(`to_serial` option). All output options can be turned on simultaneously.

### 3.1 Obtain RTK Solution (Optional) **Not fully Tested**
**The RTK system we use is a combination of the moving receiver and the GNSS base station and the RTCM is already configured. So we don't do the following `forward` procedures, while the system is in fix status, the field `carr_soln` in `/ublox_driver/receiver_pvt` message becomes 2.**

If your receiver owns an internal RTK engine (for example, ZED-F9P), you can input RTCM messages from the GNSS base station to the receiver in order to obtain the cm-level accurate RTK localization result. Our software can forward the RTCM stream from a local socket to the receiver's serial port. Nowadays many GNSS stations distribute their RTCM streams via [NTRIP protocol](https://en.wikipedia.org/wiki/Networked_Transport_of_RTCM_via_Internet_Protocol) and you can easily fetch the NTRIP data and map it to a local socket via [RTKLIB](http://www.rtklib.com/). Following those commands to build RTKLIB and setup the RTCM stream:
```
git clone https://github.com/tomojitakasu/RTKLIB.git
cd RTKLIB/
git checkout rtklib_2.4.3
cd app/consapp/str2str/gcc/
make
./str2str -in ntrip://${NTRIP_SITE}:${NTRIP_PORT}/${MOUNT_POINT} -out tcpsvr://:3503
```
Then set the `input_rtcm` option to `1` in *config/driver_config.yaml* and launch the ros node with:
```
roslaunch ublox_driver ublox_driver.launch
```
If the field `carr_soln` in `/ublox_driver/receiver_pvt` message becomes `2`, the RTK is in fix status. If you find the location of the GNSS base station reported in the RTCM message is somehow biased, you can apply correction via the variable `rtk_correction_ecef` in the config file.

## 4. Playback Log Files (**Not tested yet**)

Our package can also take an log file as the input. The log file can be recorded via [u-center](https://www.u-blox.com/en/product/u-center), RTKLIB or our package itself. To playback the log file, you need to set `online` to `0` and point `ubx_filepath` to your log file in the config file. Then launch the ros node with:
```
roslaunch ublox_driver ublox_driver.launch
```
Similar to the online receiver manner, all three output options are also supported in the playback mode. Note that the playback speed is controlled by the `serial_baud_rate` variable in the config file.


## 5. Synchronize System Time (**Not tested yet**)
In addition to message parsing and delivery, *ublox_driver* can also synchronize the local system time to the global time without the need of internet connection. Note that such synchronization is only in a coarse level and the accuracy is not guaranteed. To perform such synchronization, you need to set `UTC_OFFSET` macro in `src/sync_system_time.cpp` according to your timezone. Recompile and launch the driver with:
```
roslaunch ublox_driver ublox_driver.launch
```
Then open another terminal and run commands:
```
sudo su
source /opt/ros/kinetic/setup.bash
source ${YOUR_CATKIN_WORKSPACE}/devel/setup.bash
rosrun ublox_driver sync_system_time
```
The system time will be synchronized to the global time when the receiver gets a valid PVT solution.

## 6. Todo List

- [ ] Config u-blox receiver when the driver gets launched
- [ ] Infer timezone from geodetic location when sync time
- [ ] Optimize time-sync function to improve precision

## 7. Acknowledgements
Many of the ephemeris parsing functions in our package are adapted from [RTKLIB](http://www.rtklib.com/). We use [mini-yaml](https://github.com/jimmiebergmann/mini-yaml) for config parsing.

**Alomst all the code in this package are from [HKUST-Aerial-Robotics/ublox_driver](https://github.com/HKUST-Aerial-Robotics/ublox_driver).**

## 8. License
The source code is released under [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html) license.

