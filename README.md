# mqtt_logger

A simple application that logs MQTT data into a file.

## Requirements

The following Python modules are required:

- [PyYAML](https://pypi.org/project/PyYAML/)
- [paho-mqtt](https://pypi.org/project/paho-mqtt/)

## Installation

Install required modules - e.g. using your distribtion package manger:

```shell
# apt-get install python3-yaml python3-paho-mqtt
```

Alternatively you can use `pip` instead:

```shell
$ pip install -r requirements.txt
```

If you want to use this as systemd unit, copy the software to a directory such as `/opt`:

```shell
# cp mqtt_logger.py /opt
# chmod +x /opt/mqtt_logger.py
```

Edit [`mqtt_logger.service`](mqtt_logger.service) and specify a valid configuration, e.g.:

```ini
...
[Service]
ExecStart=/opt/mqtt_logger.py -c /opt/homelab.yml
```

Finally, copy the configuration and systemd unit file before enabling it:

```shell
# cp homelab.yml /opt
# cp mqtt_logger.service /etc/systemd/system
# systemctl daemon-reload
# systemctl enable --now mqtt_logger.service
```
