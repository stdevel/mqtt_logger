#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple application that logs MQTT data into a file
"""

import logging
import argparse
import sys
from datetime import datetime
import os
import yaml
from paho.mqtt import client as mqtt_client

LOGGER = logging.getLogger('mqtt_logger')
"""
logging: Logger instance
"""
LOG_LEVEL = None
"""
logging: Logger level
"""
FILE_PATH = "/tmp"
"""
str: path to write files to
"""


def parse_options():
    """Parses options and arguments."""
    desc = '''%(prog)s is used for subscribing to MQTT topics
    and write them to a file.'''
    epilog = '''Check-out the website for more details:
     http://github.com/stdevel/mqtt_logger'''
    parser = argparse.ArgumentParser(
        description=desc, epilog=epilog
    )

    # define option groups
    gen_opts = parser.add_argument_group("generic arguments")
    conf_opts = parser.add_argument_group("configuration arguments")

    # GENERIC ARGUMENTS
    # -d / --debug
    gen_opts.add_argument(
        "-d", "--debug",
        dest="generic_debug",
        default=False,
        action="store_true",
        help="enable debugging outputs (default: no)"
    )

    # CONFIGURATION ARGUMENTS
    # -c / --config
    conf_opts.add_argument(
        "-c", "--configuration",
        metavar="FILE",
        nargs=1,
        type=str,
        help="configuration file"
    )

    # parse options and arguments
    return parser.parse_args()


def verify_configuration(conf):
    """
    Validates the configuration file
    """
    keys_broker = [
        "hostname",
        "port",
        "username",
        "password",
    ]
    try:
        for key in keys_broker:
            if key not in conf["broker"]:
                LOGGER.error(
                    "Required key NOT found in configuration: %s",
                    key
                )
                return False
        if not conf["topics"]:
            LOGGER.error(
                "No topics have been defined"
            )
            return False
        return True
    except KeyError:
        LOGGER.error("Check brother and topic configuration")


def connect_mqtt(username, password, hostname, port) -> mqtt_client:
    """
    Connect to MQTT broker
    """
    client_id = "mqtt_logger"

    def on_disconnect(client, userdata, return_code):
        LOGGER.error("Connection to MQTT broker lost")

    def on_connect(client, userdata, flags, return_code):
        if return_code == 0:
            LOGGER.info("Connected to MQTT Broker!")
        else:
            LOGGER.error("Failed to connect, return code %d\n", return_code)
    # set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(hostname, port)
    return client


def subscribe(client: mqtt_client, topics):
    """
    This function subscribes to a MQTT topic
    """
    def on_connect(client, userdata, flags, return_code):
        if return_code == 0:
            LOGGER.info("Connected to MQTT Broker and subscribed topics")
            # subscribe to topics again
            client.subscribe(topics)
        else:
            LOGGER.error("Failed to connect, return code %d\n", return_code)


    def on_disconnect(client, userdata, return_code):
        LOGGER.info("Subscription lost")


    def on_message(client, userdata, msg):
        LOGGER.debug(
            "Received '%s' from '%s' topic",
            msg.payload.decode(), msg.topic
            )
        # write to file
        try:
            file_name = FILE_PATH + os.path.sep + msg.topic.replace("/", "_")
            LOGGER.debug("Writing received message to %s", file_name)
            with open(file_name, "a") as topic_file:
                topic_file.write("%s - " % datetime.now())
                topic_file.write(msg.payload.decode())
                topic_file.write("\n")
        except PermissionError as err:
            LOGGER.error("Unable to write to broker file: %s", err)
    # add callback
    client.subscribe(topics)
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect


def load_configuration(options):
    """
    Loads the configuration file
    """
    try:
        with open(options.configuration[0]) as file:
            conf = yaml.load(file)
            LOGGER.debug("Configuration file content: %s", conf)
            if verify_configuration(conf):
                return conf
    except FileNotFoundError as err:
        LOGGER.error("File not found: %s", err)
    return False


def start_subscribe(conf):
    """
    Subscribe all the topics
    """
    # create tuple configuration
    topics = []
    for topic in conf['topics']:
        topics.append((topic, 0))
    # connect to MQTT
    client = connect_mqtt(
        conf['broker']['username'], conf['broker']['password'],
        conf['broker']['hostname'], conf['broker']['port']
        )
    subscribe(client, topics)
    client.loop_forever()


def main(options):
    """
    Main function, starts the logic based on parameters.
    """
    LOGGER.debug("Options: %s", options)
    if not options.configuration:
        LOGGER.error("Please specify a configuration file!")
        sys.exit(1)
    # try to load configuration
    conf = load_configuration(options)
    if conf:
        start_subscribe(conf)
    else:
        LOGGER.error("Configuration seems invalid, bailing out")
        sys.exit(1)


def cli():
    """
    This functions initializes the CLI interface
    """
    global LOG_LEVEL
    options = parse_options()

    # set logging level
    logging.basicConfig()
    if options.generic_debug:
        LOG_LEVEL = logging.DEBUG
    else:
        LOG_LEVEL = logging.INFO
    LOGGER.setLevel(LOG_LEVEL)

    main(options)


if __name__ == "__main__":
    cli()
