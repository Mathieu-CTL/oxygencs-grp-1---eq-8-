"""
This module contains the App class for managing the sensor hub connection and
handling HVAC actions based on sensor data.
"""

import logging
import json
import time
from signalrcore.hub_connection_builder import HubConnectionBuilder
import requests


class App:
    """Application class to manage sensor hub connection and HVAC actions."""

    def __init__(self):
        """Initialize the App class with default values."""
        self._hub_connection = None
        self.ticks = 10

        # To be configured by your team
        self.host = None  # Setup your host here
        self.token = None  # Setup your token here
        self.t_max = None  # Setup your max temperature here
        self.t_min = None  # Setup your min temperature here
        self.database_url = None  # Setup your database here

    def __del__(self):
        """Destructor to ensure the hub connection is stopped."""
        if self._hub_connection is not None:
            self._hub_connection.stop()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.host}/SensorHub?token={self.token}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )
        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(temperature)
            self.save_event_to_database(timestamp, temperature)
        except KeyError as err:
            print(f"Key error: {err}")
        except TypeError as err:
            print(f"Type error: {err}")
        except ValueError as err:
            print(f"Value error: {err}")
        except requests.exceptions.RequestException as err:
            print(f"Request error: {err}")
        # except Exception as err:  # Log unexpected errors
        #     logging.error("An unexpected error occurred: %s", err)

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.t_max):
            self.send_action_to_hvac("TurnOnAc")
        elif float(temperature) <= float(self.t_min):
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        try:
            response = requests.get(
                f"{self.host}/api/hvac/{self.token}/{action}/{self.ticks}"
            )
            details = json.loads(response.text)
            print(details, flush=True)
        except requests.exceptions.RequestException as err:
            print(f"Request error: {err}")

    def save_event_to_database(self, _timestamp, _temperature):
        """Save sensor data into database."""
        try:
            # To implement saving logic
            pass
        except requests.exceptions.RequestException as err:
            print(f"Request error: {err}")


if __name__ == "__main__":
    app = App()
    app.start()
