# Kelvin lights interface

This is a python package to interface with Kelvin lights using  usb (serial) or bluetooth (experimental). This package is available on PyPI and can be installed with pip.
To use it in your project, simply run:

    pip install "python4yahdlc@git+https://x-token-auth:ATCTT3xFfGN0ehp5bAN5THYpRflG9MfmPsQODeO_e3B7bUpfvbX8QzITTwh583tovdBv9n3yCQFUfMoZ0sJBO5YyDXY8CDgGoo4T7qEioLbbiRTpHaruRuTYbvcdzwSGSXXFJUukSplZJDbv8fRu3BSp1F1TtNzriPGYzmosQAu2czU2ix19u7Y=B197A1B4@bitbucket.org/riftlabs/python4yahdlc.git@feature/fix_unsized_arrays" k_lights_interface

The official python4yahdlc package causes a segmentation fault on mac/linux which is why this fork must be used.

## Features

- Control Kelvin devices. Set brightness, CCT and Duv, RGB, HSI, read out temperatures, voltages, and more. 
- Supports Usb (serial) communication using the pyserial package
- Experimental support of BLE communication using the bleak package. Check bleak for hardware requirements.

## Interface overview
Light | Usb    | Bluetooth |
------ | -------- | ------- |
Play and Play Pro| Yes  | Yes    |
Epos 300| No   | Yes    |
Epos 600| Yes | Yes     |


## Usage

### Logging
Set your desired log level using the set_log_level function

```python
from k_lights_interface.k_logging import set_log_level, logging
set_log_level(logging.INFO)
```
### Serial usage:

```python
from k_lights_interface.k_serial_manager import KSerialManager
from k_lights_interface.k_logging import set_log_level, logging

set_log_level(logging.INFO)
dev_manager = KSerialManager()
devices = dev_manager.connect_to_all()
[print(dev) for dev in devices]
if (len(devices) == 0):
    logging.error("No devices found. Make sure its connected via usb")
    exit(1)
# Just use the first device for this example
try:
    dev = devices[0]
    dev.set_intensity(10)
    dev.set_cct(6500, 0)
except Exception as e:
    logging.error(f"Failed to set CCT: {e}")
```

### BLE usage (THIS IS VERY EXPERIMENTAL):

```python
import asyncio
from k_lights_interface.k_ble_manager import KBleManager
from k_lights_interface.k_logging import set_log_level, logging

async def main():
    set_log_level(logging.INFO)
    ble_manager = KBleManager()
    devices = await ble_manager.connect_to_all()
    if len(devices) == 0:
        print("No devices found")
        return
    print(devices)
    ret, device_stats = devices[0].get_device_stats()
    print(device_stats)

if __name__ == "__main__":
    asyncio.run(main())
    print("finished")
```
