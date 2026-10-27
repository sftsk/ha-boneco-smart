"""Shared Home Assistant device identity."""
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

class BonecoEntity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, key):
        super().__init__(coordinator)
        self._attr_unique_id = f'{coordinator.device_id}_{key}'
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_id)}, manufacturer='BONECO',
            model='H700 SMART', name='BONECO H700 SMART',
        )
