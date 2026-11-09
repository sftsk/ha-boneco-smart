# BONECO H700 SMART for Home Assistant

Control the H700 SMART directly over your home Wi-Fi using Tuya LAN protocol 3.5. Keep its existing BONECO SMART app pairing. No Tuya account, MQTT broker, cloud service, or emulator is used during normal operation.

This is an unofficial community integration, unaffiliated with BONECO. Tested with Home Assistant **2026.10.4**; the HACS package requires Home Assistant 2026.10 or newer.

## Install with HACS

1. In [HACS](https://www.hacs.xyz/), open the menu and choose **Custom repositories**.
2. Add `https://github.com/sftsk/ha-boneco-smart` with type **Integration**.
3. Find **BONECO H700 SMART** in HACS and download it.
4. Restart Home Assistant.
5. Open **Settings → Devices & services → Add integration**, search for **BONECO H700 SMART**, and enter your device's IP address, device ID, and local key.

See the [HACS custom repository instructions](https://www.hacs.xyz/docs/faq/custom_repositories/) if needed. This repository is added manually; it is not part of HACS's default catalog.

For later releases, install the offered update in HACS or Home Assistant's Updates page and restart Home Assistant. Your saved device configuration is retained. GitHub releases select the version HACS offers; future updates are published as new releases.

## Manual install

Download a source archive from [Releases](https://github.com/sftsk/ha-boneco-smart/releases), extract it, and copy `custom_components/boneco_smart` into your Home Assistant configuration directory. The resulting path should be `/config/custom_components/boneco_smart/manifest.json`. Restart Home Assistant and add the integration through Settings as above.

## Device credentials

Setup requires the device's LAN address, Tuya device ID, and **16-byte local key**. The integration checks the connection before saving the entry. Credentials are entered locally in Home Assistant and are never sent to this repository.

The device ID shown by the BONECO app is not the local key. Obtaining the key is a separate setup step; this integration does not extract credentials or provide a cloud login. If preserving your current app pairing matters, do not reset the device or pair it with another app just to obtain a key. Re-pairing may replace its current key and app pairing.

Home Assistant stores the key in its configuration storage. Protect backups and do not post the key or account sessions in GitHub issues. No real device credentials are included in this repository.

## Controls and readings

| Entity | Function |
| --- | --- |
| Humidifier | Power; target humidity 30–70% in steps of 5%; Custom, Auto, Baby, and Sleep presets |
| Function | Humidifier, Purifier, or Hybrid |
| Fan level | Native device level 0–6; changing this also selects Custom preset |
| Humidity | Current relative humidity |
| Temperature | Current temperature in °C |
| Air quality level | BONECO's proprietary 0–8 reading; it is not a standard AQI or PM2.5 measurement |
| Low water | Turns on when the device reports that it is out of water |
| Needs cleaning | Turns on when the device reports its cleaning reminder |

Status refreshes every 30 seconds and immediately after a command. Automatic presets may manage the fan themselves. A command reads back the reported state; the integration does not assume that a requested value was applied.

The integration is intended for the H700 SMART with the attached data-point schema. Other BONECO models have not been tested.

## Connection problems

- Give the device a DHCP reservation in your router so its address stays stable.
- Home Assistant must reach the device on TCP port 6668. VLAN or guest-network isolation can prevent this.
- If setup or commands time out, close the BONECO app and retry. Some Tuya firmware limits simultaneous LAN clients.
- Do not reset or re-pair the device to troubleshoot this integration. If its address or key changes, remove this integration entry and add it again with the updated values.
- The BONECO app can continue to use its existing pairing. This integration does not change the device's own cloud connection or firewall rules.

## Verification and development

Tested on Home Assistant **2026.10.4**, Python **3.14.10**, and TinyTuya **1.20.0**. Automated tests cover setup, service-to-data-point mappings, maintenance alerts, command validation, socket cleanup, offline recovery, and duplicate configuration. GitHub Actions runs the tests, HACS validation, and hassfest on pushes and pull requests.

The client has successfully read a physical H700 SMART and written back its existing humidity target. The device accepted the command and its power, function, preset, fan level, and target remained unchanged. Other physical control changes have not been exercised.

For development, in a separate Python 3.14 virtual environment:

```sh
python -m pip install pytest-homeassistant-custom-component==0.13.375 tinytuya==1.20.0
python -m pytest -q
```

`device-schema.json` contains the verified device schema, and `tests/status.json` contains a sanitized status fixture. The integration uses [TinyTuya](https://github.com/jasonacox/tinytuya) for the encrypted LAN protocol and the [Home Assistant humidifier API](https://contributors.home-assistant.io/core/entities/humidifier/).

To publish an update, change the version in `custom_components/boneco_smart/manifest.json`, run the tests, push the commit, then create a matching GitHub release such as `v0.1.1`. HACS will offer the new release after it refreshes repository information.

## Remove

Remove the integration from **Settings → Devices & services**, then remove its download in HACS and restart Home Assistant. For a manual installation, delete `/config/custom_components/boneco_smart` after removing the integration entry.

## License

[MIT](LICENSE). The included generic integration icon is original project artwork, not the BONECO logo.
