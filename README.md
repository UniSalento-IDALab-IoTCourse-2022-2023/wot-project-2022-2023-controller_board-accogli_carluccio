# GROUND WORKERS LOCATION AND IDENTIFICATION SYSTEM

This project aims to develop a Proximity Warning System (PWS) using Bluetooth Low energy (BLE) technology in work contexts where mobile machinery and workers on the ground are present.\
\
The system can detect proximity situations between these subjects in real-time, notifying those concerned in case of danger. Additionally, it supports other types of alarms, including general communications and signaling when drivers are away from machinery.\
\
Furthermore, the system offers functionalities for the management of site resources, allows the definition of a daily configuration of active machines with their authorised drivers, and guarantees secure access to the proximity notifications. Thanks to the software and hardware solutions adopted, it is easily extendable and adaptable to specific needs. 
## Architecture
The system architecture is outlined below:

![alt text](images/image.png)

The developed components are:
* the central server\
https://github.com/UniSalento-IDALab-IoTCourse-2022-2023/wot-project-2022-2023-central_server-accogli_carluccio.git
* 🟡(this repo) <b>the machinery controller board </b> 
* android application\
https://github.com/UniSalento-IDALab-IoTCourse-2022-2023/wot-project-2022-2023-app_android-accogli_carluccio.git
* frontend application\
https://github.com/UniSalento-IDALab-IoTCourse-2022-2023/wot-project-2022-2023-app_angular-accogli_carluccio.git

## THIS REPO: Machinery controller board
The repo contains the python code for a script which simulates an electronic board placed on the machinery itself, acting as a central hub for its management.\
This node plays an active role in the processing of alarms, as it converts and forwards the messages received on the MQTT topic of the corresponding machinery, notifying the operator's smartphone connected via BLE. \
It also manages secure access to the machine, ensuring that only operators authorized for that working day can connect to the node via BLE and access the proximity alarm system.\
It is possible to expand the functionalities by adding appropriately configured devices or sensors. Currently, redundant alarm signaling is configured using a passive buzzer, an RGB LED. Moreover an LCD display indicate the BLE connection status.

🔴 <b><i>NOTE: </b> the script was tested and developed on a Raspberry Pi 4 Model B with 8 gb of ram. It also uses GPIO.</i>


## Usage
Check the installation of all the libraries needed and make sure that the local server is up. Then run the script on a Raspberry board with:
```
python main.py
```
Once the <i>'Advertisement register'</i> message is printed, you can proceed with the BLE connection using the appropriate app.
