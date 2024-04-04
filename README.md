# AI Autofocus for Digital Microscopes

This project introduces an AI-based solution to automatically adjust the focus of digital microscopes. Utilizing an EfficientNetV2-s model, the system is trained on a custom dataset (consisting of histological images) to recognize five distinct focus levels, enhancing the precision and efficiency of autofocus algorithms.

## Model Information

- **Model Architecture:** EfficientNetV2-s
- **Focus Classification:** Ranges from 1 (least focused) to 5 (most focused)
- **Model Weights:** Available in the file `53_28.02.pth`

The custom dataset used for training is accessible for download via the following [Google Drive link](https://drive.google.com/file/d/1ozBqvRwbN_lpdluTA-vPwruiAeHo07ZK/view?usp=drive_link).

## Prerequisites

For the AI autofocus system to function, the digital microscope must meet the following requirements:

- An **Ethernet port** for network communication.
- An **open interface** for adjusting the z-axis motor.
- A **Linux-based operating system** capable of utilizing `.service` files for automatic startup. *Operating systems meeting the same requirementes can also be used, however, only linux has been tested*.

## Setup Process

### Microscope Configuration

1. Connect the microscope to the inference base using an Ethernet cable.
2. Implement the following components on the microscope's system:
   - `use_focus.py` for initiating the autofocus process.
   - Additional input and start sequence scripts as required by the specific microscope model.

### Inference Base Configuration

1. Setup the inference base with the following files:
   - `effnetv2_pure.py` for running the AI model.
   - Model weights file (`53_28.02.pth`).
   - `focus_receiver` for processing the focus adjustment data.

2. Use `searcher.py` to analyze the incoming image, predict the current focus level, and determine the necessary adjustments. The predictions are sent back to the microscope for real-time focus optimization.

## Automating Startup with systemd

For Linux distributions that support `systemd`, you can automate the startup process of the AI autofocus system using `.service` files.

#### Create and open .service-file

```sudo nano /etc/systemd/system/myserver.service```

#### Specify all requirements

```[Unit]
Description=My Python Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/your/server_script.py
WorkingDirectory=/path/to/your/
StandardOutput=inherit
StandardError=inherit
Restart=always
User=YOUR_USERNAME

[Install]
WantedBy=multi-user.target
```

#### Enable and start the service:

```
sudo systemctl start myserver.service
sudo systemctl enable myserver.service
```

#### Check status

```
sudo systemctl status myserver.service
```

##### *This can be done on both sides*
---

