"""Exercise the integration in Home Assistant without contacting hardware."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

pytest_plugins = ["pytest_homeassistant_custom_component"]


@pytest.fixture
def device(monkeypatch):
    class FakeDevice:
        def __init__(self):
            self.response = json.loads(Path(__file__).with_name("status.json").read_text())
            self.commands = []
            self.closed = 0
            self.fail = False

        def status(self):
            if self.fail:
                raise OSError("Device offline")
            return deepcopy(self.response)

        def set_multiple_values(self, values):
            if self.fail:
                return {"Error": "Connection failed", "Err": "901"}
            self.commands.append(values)
            self.response["dps"].update(values)
            return {"dps": deepcopy(values)}

        def close(self):
            self.closed += 1

    fake = FakeDevice()
    monkeypatch.setattr("tinytuya.Device", lambda *args, **kwargs: fake)
    return fake


@pytest.fixture
def credentials():
    return {"host": "192.0.2.1", "device_id": "test_boneco", "local_key": "0123456789abcdef"}


@pytest.fixture(autouse=True)
def load_custom_component(hass, enable_custom_integrations):
    """Let Home Assistant discover the custom_components package in this project."""
