"""
Unit and integration tests for the App class in src.main module.
"""

import unittest
from unittest.mock import MagicMock
from datetime import datetime
import sys
import os
import pytz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# pylint: disable=C0413
from src.main import App, Base, HvacTemperature, HvacEvents


class TestUnitaire(unittest.TestCase):
    """Unit tests for the App class."""

    def setUp(self):
        """Set up the test environment."""
        self.app = App()
        self.app.host = os.getenv("HOST")
        self.app.token = os.getenv("TOKEN")
        self.app.database_url = os.getenv("DATABASE_URL")

    def test_take_action_turn_on_ac(self):
        """Test if AC is turned on when temperature is above T_MAX."""
        self.app.t_max = 30
        self.app.send_action_to_hvac = MagicMock()

        self.app.take_action(31)

        self.app.send_action_to_hvac.assert_called_once_with("TurnOnAc")

    def test_take_action_turn_on_heater(self):
        """Test if heater is turned on when temperature is below T_MIN."""
        self.app.t_min = 18
        self.app.send_action_to_hvac = MagicMock()

        self.app.take_action(17)

        self.app.send_action_to_hvac.assert_called_once_with("TurnOnHeater")

    def test_take_action_no_action(self):
        """Test if no action is taken when temperature is within range."""
        self.app.send_action_to_hvac = MagicMock()

        self.app.take_action(25)

        self.app.send_action_to_hvac.assert_not_called()


class TestIntegration(unittest.TestCase):
    """Integration tests for the App class."""

    def setUp(self):
        """Set up the test environment."""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session_local = sessionmaker(bind=self.engine)

        # Initialise App
        self.app = App()
        self.app.session_local = self.session_local
        self.app.database_url = "sqlite:///:memory:"

    def test_save_event_to_database(self):
        """Test saving events to the database."""
        # Simulate timestamp in the correct format
        edt = pytz.timezone("US/Eastern")
        timestamp = datetime.now().astimezone(edt).strftime("%Y-%m-%d %H:%M:%S")
        temperature = "28.5"

        self.app.save_event_to_database(timestamp, temperature)

        session = self.session_local()
        try:
            temp_data = (
                session.query(HvacTemperature).filter_by(temperature="28.5").first()
            )
            event_data = session.query(HvacEvents).filter_by(event="NoAction").first()

            self.assertIsNotNone(temp_data)
            self.assertIsNotNone(event_data)
        finally:
            session.close()

    def tearDown(self):
        """Clean up the test environment."""
        Base.metadata.drop_all(self.engine)


if __name__ == "__main__":
    unittest.main()
