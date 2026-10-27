"""The device's native fan-level control."""
from homeassistant.components.number import NumberEntity, NumberMode
from .entity import BonecoEntity

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([BonecoFanLevel(entry.runtime_data)])

class BonecoFanLevel(BonecoEntity, NumberEntity):
    _attr_name = 'Fan level'
    _attr_icon = 'mdi:fan'
    _attr_native_min_value = 0
    _attr_native_max_value = 6
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator):
        super().__init__(coordinator, 'fan_level')

    @property
    def native_value(self):
        return self.coordinator.data['106']

    async def async_set_native_value(self, value):
        # Manual fan control belongs to the Custom operating preset.
        await self.coordinator.async_write({'104': 'Custom', '106': value})
