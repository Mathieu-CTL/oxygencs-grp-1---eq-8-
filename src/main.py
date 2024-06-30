from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz
from dateutil.parser import parse as parse_date

from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
import requests
import json
import time
from dotenv import load_dotenv
import os

# SQLAlchemy base
Base = declarative_base()


# Définition des modèles
class HVAC_Temperature(Base):
    __tablename__ = "HVAC_Temperature"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    temperature = Column(String, index=True)


class HVAC_Events(Base):
    __tablename__ = "HVAC_Events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    event = Column(String, index=True)


# Charger les variables d'environnement depuis le fichier .env
load_dotenv()


class App:
    def __init__(self):
        self._hub_connection = None
        self.TICKS = 10

        # To be configured by your team
        self.HOST = os.getenv("HOST")
        self.TOKEN = os.getenv("TOKEN")
        self.T_MAX = 30  # Setup your max temperature here
        self.T_MIN = 18  # Setup your min temperature here
        self.DATABASE_URL = os.getenv("DATABASE_URL")

        # Initialize database connection
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def __del__(self):
        if self._hub_connection != None:
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
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
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
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(temperature)
            self.save_event_to_database(timestamp, temperature)
        except Exception as err:
            print(err)

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.T_MAX):
            self.send_action_to_hvac("TurnOnAc")
        elif float(temperature) <= float(self.T_MIN):
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{self.TICKS}")
        details = json.loads(r.text)
        print(details, flush=True)

    def save_event_to_database(self, timestamp, temperature):
        """Save sensor data into database."""
        session = self.SessionLocal()
        try:
            # Convert timestamp to datetime object
            edt = pytz.timezone("US/Eastern")
            timestamp_temp = (
                parse_date(timestamp).astimezone(edt).strftime("%Y-%m-%d %H:%M:%S")
            )
            timestamp_events = (
                datetime.now().astimezone(edt).strftime("%Y-%m-%d %H:%M:%S")
            )

            # Save temperature data (Table "HVAC_Temperature")
            temp_record = HVAC_Temperature(
                timestamp=timestamp_temp, temperature=str(temperature)
            )
            session.add(temp_record)

            # Save event data (Table "HVAC_Events")
            if float(temperature) >= float(self.T_MAX):
                event_record = HVAC_Events(timestamp=timestamp_events, event="TurnOnAc")
            elif float(temperature) <= float(self.T_MIN):
                event_record = HVAC_Events(
                    timestamp=timestamp_events, event="TurnOnHeater"
                )
            else:
                event_record = HVAC_Events(timestamp=timestamp_events, event="NoAction")
            session.add(event_record)

            # Commit the transaction
            session.commit()

        except Exception as e:
            session.rollback()
            print(f"Error saving to database: {e}")
        finally:
            session.close()


if __name__ == "__main__":
    app = App()
    app.start()
