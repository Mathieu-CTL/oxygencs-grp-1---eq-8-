"""
This module contains the App class for managing the sensor hub connection and
handling HVAC actions based on sensor data.
"""

import logging
import json
import time
import os
from datetime import datetime

import pytz
from dateutil.parser import parse as parse_date
from dotenv import load_dotenv
from signalrcore.hub_connection_builder import HubConnectionBuilder
import requests
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLAlchemy base
Base = declarative_base()


class HvacTemperature(Base):
    """
    SQLAlchemy model for HVAC temperature data.
    """

    __tablename__ = "HVAC_Temperature"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    temperature = Column(String, index=True)


class HvacEvents(Base):
    """
    SQLAlchemy model for HVAC events data.
    """

    __tablename__ = "HVAC_Events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    event = Column(String, index=True)


# Load environment variables from the .env file
load_dotenv()


class App:
    """
    Application class to manage sensor hub connection and HVAC actions.
    """

    def __init__(self):
        """
        Initialize the App class with default values.
        """
        self._hub_connection = None
        self.ticks = 10

        # To be configured by your team
        self.host = os.getenv("HOST", "http://localhost")
        self.token = os.getenv("TOKEN", "default_token")
        self.t_max = 30
        self.t_min = 18
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///:memory:")

        # Initialize database connection
        self.engine = create_engine(self.database_url)
        self.session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def __del__(self):
        """
        Destructor to ensure the hub connection is stopped.
        """
        if self._hub_connection is not None:
            self._hub_connection.stop()

    def start(self):
        """
        Start Oxygen CS.
        """
        self.setup_sensor_hub()
        self._hub_connection.start()
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """
        Configure hub connection and subscribe to sensor data events.
        """
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
        self._hub_connection.on("ReceiveSensorData",
                                self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """
        Callback method to handle sensor data on reception.
        """
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
        except Exception as err:  # Log unexpected errors
            logging.error(
                "An unexpected error occurred: %s", err
            )  # pylint: disable=W0703

    def take_action(self, temperature):
        """
        Take action to HVAC depending on current temperature.
        """
        if float(temperature) >= float(self.t_max):
            self.send_action_to_hvac("TurnOnAc")
        elif float(temperature) <= float(self.t_min):
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """
        Send action query to the HVAC service.
        """
        try:
            response = requests.get(
                f"{self.host}/api/hvac/{self.token}/{action}/{self.ticks}"
            )
            details = json.loads(response.text)
            print(details, flush=True)
        except requests.exceptions.RequestException as err:
            print(f"Request error: {err}")

    def save_event_to_database(self, timestamp, temperature):
        """
        Save sensor data into database.
        """
        session = self.session_local()
        try:
            # Convert timestamp to the correct timezone
            edt = pytz.timezone("US/Eastern")

            timestamp_str = (
                parse_date(timestamp).astimezone(edt).strftime(
                    "%Y-%m-%d %H:%M:%S")
            )

            timestamp_temp = datetime.strptime(timestamp_str,
                                               "%Y-%m-%d %H:%M:%S")

            timestamp_events = datetime.now().astimezone(edt)

            # Save temperature data (Table "HVAC_Temperature")
            temp_record = HvacTemperature(
                timestamp=timestamp_temp, temperature=str(temperature)
            )
            session.add(temp_record)

            # Save event data (Table "HVAC_Events")
            if float(temperature) >= float(self.t_max):
                event_record = HvacEvents(timestamp=timestamp_events,
                                          event="TurnOnAc")
            elif float(temperature) <= float(self.t_min):
                event_record = HvacEvents(
                    timestamp=timestamp_events, event="TurnOnHeater"
                )
            else:
                event_record = HvacEvents(timestamp=timestamp_events,
                                          event="NoAction")
            session.add(event_record)

            # Commit the transaction
            session.commit()
        except requests.exceptions.RequestException as err:
            print(f"Request error: {err}")
            session.rollback()
        except Exception as err:
            print(f"Error saving to database: {err}")  # pylint: disable=W0703
            session.rollback()
        finally:
            session.close()


if __name__ == "__main__":
    app = App()
    app.start()
