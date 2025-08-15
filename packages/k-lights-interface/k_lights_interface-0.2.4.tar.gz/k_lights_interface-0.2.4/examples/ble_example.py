import asyncio
from k_lights_interface.k_ble_manager import KBleManager
from k_lights_interface.k_logging import set_log_level, logging

async def main():
    set_log_level(logging.INFO)
    ble_manager = KBleManager()
    devices = await ble_manager.connect_to_all_with_names(valid_names=["Epos 300"])
    if len(devices) == 0:
        print("No devices found")
        return
    print(devices)
    ret, device_stats = devices[0].get_device_stats()
    print(device_stats)


if __name__ == "__main__":
    asyncio.run(main())
    print("finished")
