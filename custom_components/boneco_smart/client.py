"""The H700 SMART's verified Tuya 3.5 LAN interface."""
import math
import tinytuya

FUNCTIONS = ('Humidifier', 'Purifier', 'Hybrid')
PRESETS = ('Custom', 'Auto', 'Baby', 'Sleep')
REQUIRED_DPS = {'1', '3', '12', '104', '105', '106', '111'}

class BonecoError(Exception):
    """The device could not be reached or returned an incompatible response."""

def validate_commands(values):
    """Reject unsupported controls and values before touching the device."""
    if not isinstance(values, dict) or not values:
        raise ValueError('No settings were provided.')
    normalized = {}
    for dp, value in values.items():
        if dp == '1':
            if type(value) is not bool:
                raise ValueError('Power must be on or off.')
        elif dp in ('3', '104'):
            choices = FUNCTIONS if dp == '3' else PRESETS
            if value not in choices:
                raise ValueError('Unsupported Boneco mode.')
        elif dp in ('105', '106'):
            minimum, maximum, step = (30, 70, 5) if dp == '105' else (0, 6, 1)
            if (type(value) not in (int, float) or not math.isfinite(value)
                    or value != int(value) or not minimum <= value <= maximum
                    or (value - minimum) % step):
                raise ValueError(f'This setting requires whole steps of {step}, from {minimum} to {maximum}.')
            value = int(value)
        else:
            raise ValueError('Unsupported Boneco setting.')
        normalized[dp] = value
    return normalized

class BonecoClient:
    """Use one caller at a time; each request releases its LAN socket."""
    def __init__(self, host, device_id, local_key):
        if not host or not device_id or len(local_key.encode('utf-8')) != 16:
            raise ValueError('Enter a host, device ID, and a 16-byte local key.')
        self._device = tinytuya.Device(
            device_id, host, local_key, version=3.5,
            connection_timeout=4, connection_retry_limit=1, connection_retry_delay=0,
        )

    def read(self):
        try:
            response = self._device.status()
        except Exception as exc:
            raise BonecoError('Could not read the Boneco over Wi-Fi.') from exc
        finally:
            self._device.close()
        if not isinstance(response, dict) or 'Error' in response or 'Err' in response:
            raise BonecoError('The Boneco did not return a valid LAN status.')
        dps = response.get('dps')
        if not isinstance(dps, dict) or not REQUIRED_DPS.issubset(dps):
            raise BonecoError('This device did not return the H700 SMART data points.')
        try:
            validate_commands({dp: dps[dp] for dp in ('1', '3', '104', '105', '106')})
            if any(type(dps[dp]) not in (int, float) for dp in ('12', '111')):
                raise ValueError('Invalid sensor value.')
        except ValueError as exc:
            raise BonecoError('The H700 SMART returned incompatible data.') from exc
        return dps

    def write(self, values):
        values = validate_commands(values)
        try:
            response = self._device.set_multiple_values(values)
            if isinstance(response, dict) and ('Error' in response or 'Err' in response):
                raise BonecoError('The Boneco rejected the command.')
        except BonecoError:
            raise
        except Exception as exc:
            raise BonecoError('Could not send the Boneco command over Wi-Fi.') from exc
        finally:
            self._device.close()
        return self.read()
