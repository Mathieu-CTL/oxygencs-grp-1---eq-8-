import unittest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.main import App, Base, HVAC_Temperature, HVAC_Events

class TestUnitaire(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def test_take_action_turn_on_ac(self):
        # Test pour temperature > T_MAX
        self.app.T_MAX = 30
        self.app.send_action_to_hvac = MagicMock()

        self.app.take_action(31)

        self.app.send_action_to_hvac.assert_called_once_with("TurnOnAc")

    def test_take_action_turn_on_heater(self):
        # Test pour temperature < T_MIN
        self.app.T_MIN = 18
        self.app.send_action_to_hvac = MagicMock()

        self.app.take_action(17)

        self.app.send_action_to_hvac.assert_called_once_with("TurnOnHeater")

    def test_take_action_no_action(self):
        # Test pour temperature dans le range acceptable
        self.app.send_action_to_hvac = MagicMock()

        self.app.take_action(25)

        self.app.send_action_to_hvac.assert_not_called()

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Initialise App
        self.app = App()
        self.app.SessionLocal = self.SessionLocal

    def test_save_event_to_database(self):
        # Simuler timestamp dans le bon format
        edt = pytz.timezone("US/Eastern")
        timestamp = datetime.now().astimezone(edt).strftime("%Y-%m-%d %H:%M:%S")
        temperature = "28.5"

        self.app.save_event_to_database(timestamp, temperature)

        session = self.SessionLocal()
        try:
            temp_data = session.query(HVAC_Temperature).filter_by(temperature="28.5").first()
            event_data = session.query(HVAC_Events).filter_by(event="NoAction").first()
            
            self.assertIsNotNone(temp_data)
            self.assertIsNotNone(event_data)
        finally:
            session.close()

    def tearDown(self):
        # Clean up
        Base.metadata.drop_all(self.engine)

if __name__ == "__main__":
    unittest.main()
