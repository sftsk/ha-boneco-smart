"""LAN validation, real HA setup/services, and disconnect recovery."""
from unittest.mock import patch

import pytest
from homeassistant.const import ATTR_ENTITY_ID, STATE_UNAVAILABLE
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.boneco_smart.client import BonecoClient, BonecoError


@pytest.mark.parametrize("values", [
    {}, {"1": 1}, {"105": 53}, {"105": True}, {"105": float("nan")},
    {"105": 75}, {"106": 1.5}, {"106": -1}, {"104": "Unknown"}, {"11": True},
])
def test_invalid_commands_never_touch_device(device, credentials, values):
    client = BonecoClient(**credentials)
    with pytest.raises(ValueError):
        client.write(values)
    assert device.commands == []
    assert device.closed == 0


def test_invalid_status_and_socket_cleanup(device, credentials):
    client = BonecoClient(**credentials)
    device.response = {"Error": "Wrong key", "Err": "914"}
    with pytest.raises(BonecoError):
        client.read()
    assert device.closed == 1
    device.fail = True
    with pytest.raises(BonecoError):
        client.read()
    with pytest.raises(BonecoError):
        client.write({"1": False})
    assert device.closed == 3


async def setup_entry(hass, credentials):
    entry = MockConfigEntry(domain="boneco_smart", title="BONECO H700 SMART",
                            unique_id=credentials["device_id"], data=credentials)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_setup_controls_and_recovery(hass, device, credentials):
    entry = await setup_entry(hass, credentials)
    humidifier = "humidifier.boneco_h700_smart"
    function = "select.boneco_h700_smart_function"
    fan = "number.boneco_h700_smart_fan_level"
    state = hass.states.get(humidifier)
    assert state.state == "on"
    assert state.attributes["humidity"] == 50
    assert state.attributes["current_humidity"] == 59
    assert state.attributes["mode"] == "Baby"
    assert state.attributes["target_humidity_step"] == 5
    assert hass.states.get(function).state == "Hybrid"
    assert hass.states.get(fan).state == "0"
    assert hass.states.get("sensor.boneco_h700_smart_temperature").state == "21.7"
    assert hass.states.get("sensor.boneco_h700_smart_humidity").state == "59.0"
    quality = hass.states.get("sensor.boneco_h700_smart_air_quality_level")
    assert quality.state == "0.0"
    assert "device_class" not in quality.attributes
    assert device.commands == []

    async def call(domain, service, entity_id, **data):
        await hass.services.async_call(domain, service, {ATTR_ENTITY_ID: entity_id, **data}, blocking=True)
        await hass.async_block_till_done()

    await call("humidifier", "set_humidity", humidifier, humidity=55)
    await call("humidifier", "set_mode", humidifier, mode="Sleep")
    await call("select", "select_option", function, option="Purifier")
    await call("number", "set_value", fan, value=3)
    await call("humidifier", "turn_off", humidifier)
    await call("humidifier", "turn_on", humidifier)
    assert device.commands == [
        {"105": 55}, {"104": "Sleep"}, {"3": "Purifier"},
        {"104": "Custom", "106": 3}, {"1": False}, {"1": True},
    ]
    assert hass.states.get(humidifier).attributes["mode"] == "Custom"
    assert hass.states.get(fan).state == "3"
    with pytest.raises(ServiceValidationError):
        await call("humidifier", "set_humidity", humidifier, humidity=53)
    assert len(device.commands) == 6

    device.fail = True
    with pytest.raises(HomeAssistantError):
        await call("humidifier", "turn_off", humidifier)
    assert hass.states.get(humidifier).state == STATE_UNAVAILABLE
    device.fail = False
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(humidifier).state == "on"
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_config_flow(hass, device, credentials):
    flow = await hass.config_entries.flow.async_init("boneco_smart", context={"source": "user"})
    assert flow["type"] == FlowResultType.FORM
    bad = {**credentials, "local_key": "short"}
    flow = await hass.config_entries.flow.async_configure(flow["flow_id"], bad)
    assert flow["errors"] == {"base": "invalid_input"}
    device.fail = True
    flow = await hass.config_entries.flow.async_configure(flow["flow_id"], credentials)
    assert flow["errors"] == {"base": "cannot_connect"}
    device.fail = False
    with patch("custom_components.boneco_smart.async_setup_entry", return_value=True):
        flow = await hass.config_entries.flow.async_configure(flow["flow_id"], credentials)
        await hass.async_block_till_done()
    assert flow["type"] == FlowResultType.CREATE_ENTRY
    assert flow["data"] == credentials
    flow = await hass.config_entries.flow.async_init("boneco_smart", context={"source": "user"}, data=credentials)
    assert flow["type"] == FlowResultType.ABORT
    assert flow["reason"] == "already_configured"


async def test_failed_first_poll_retries(hass, device, credentials):
    device.fail = True
    entry = MockConfigEntry(domain="boneco_smart", data=credentials)
    entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state.name == "SETUP_RETRY"
