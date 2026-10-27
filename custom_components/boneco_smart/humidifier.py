"""Power, target humidity, and the Boneco's four operating presets."""
from homeassistant.components.humidifier import HumidifierDeviceClass, HumidifierEntity, HumidifierEntityFeature
from .client import PRESETS
from .entity import BonecoEntity

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([BonecoHumidifier(entry.runtime_data)])

class BonecoHumidifier(BonecoEntity, HumidifierEntity):
    _attr_name = None
    _attr_device_class = HumidifierDeviceClass.HUMIDIFIER
    _attr_supported_features = HumidifierEntityFeature.MODES
    _attr_available_modes = list(PRESETS)
    _attr_min_humidity = 30
    _attr_max_humidity = 70
    _attr_target_humidity_step = 5

    def __init__(self, coordinator):
        super().__init__(coordinator, 'humidifier')

    @property
    def is_on(self):
        return self.coordinator.data['1']

    @property
    def current_humidity(self):
        return self.coordinator.data['111']

    @property
    def target_humidity(self):
        return self.coordinator.data['105']

    @property
    def mode(self):
        return self.coordinator.data['104']

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_write({'1': True})

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_write({'1': False})

    async def async_set_humidity(self, humidity):
        await self.coordinator.async_write({'105': humidity})

    async def async_set_mode(self, mode):
        await self.coordinator.async_write({'104': mode})
