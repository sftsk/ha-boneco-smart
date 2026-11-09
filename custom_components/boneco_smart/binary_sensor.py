"""Water and cleaning alerts from the H700 SMART status bitmaps."""
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from .entity import BonecoEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([
        BonecoAlert(entry.runtime_data, 'low_water', 'Low water', '22', 1 << 4),
        BonecoAlert(entry.runtime_data, 'needs_cleaning', 'Needs cleaning', '108', 1 << 2),
    ])


class BonecoAlert(BonecoEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, key, name, dp, mask):
        super().__init__(coordinator, key)
        self._attr_name = name
        self._dp = dp
        self._mask = mask

    @property
    def is_on(self):
        value = self.coordinator.data.get(self._dp)
        if type(value) is int and value >= 0:
            return bool(value & self._mask)
        return None
