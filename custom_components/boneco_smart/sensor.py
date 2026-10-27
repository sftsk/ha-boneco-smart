"""Measured humidity, temperature, and the proprietary air-quality level."""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from .entity import BonecoEntity

SENSORS = (
    (SensorEntityDescription(key='humidity', name='Humidity', device_class=SensorDeviceClass.HUMIDITY,
                            native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT), '111', 1),
    (SensorEntityDescription(key='temperature', name='Temperature', device_class=SensorDeviceClass.TEMPERATURE,
                            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                            state_class=SensorStateClass.MEASUREMENT), '12', 10),
    (SensorEntityDescription(key='air_quality_level', name='Air quality level', icon='mdi:air-filter',
                            state_class=SensorStateClass.MEASUREMENT), '118', 1),
)

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([BonecoSensor(entry.runtime_data, description, dp, scale)
                        for description, dp, scale in SENSORS])

class BonecoSensor(BonecoEntity, SensorEntity):
    def __init__(self, coordinator, description, dp, scale):
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._dp = dp
        self._scale = scale

    @property
    def native_value(self):
        value = self.coordinator.data.get(self._dp)
        return value / self._scale if type(value) in (int, float) else None
