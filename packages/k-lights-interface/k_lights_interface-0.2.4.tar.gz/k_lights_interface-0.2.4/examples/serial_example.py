from time import sleep
from k_lights_interface.k_serial_manager import KSerialManager
from k_lights_interface.k_logging import set_log_level, logging

def example_connect_and_get_power_state():
    set_log_level(logging.INFO)
    dev_manager = KSerialManager()
    all_connected_devices = dev_manager.connect_to_all()
    if len(all_connected_devices) == 0:
        print("No devices found")
        return
    device = all_connected_devices[0]
    ret, power_state_msg = device.get_power_state()
    if not ret:
        print("Couldnt read power state")
    print(power_state_msg)


def example_connect_and_get_info():
    set_log_level(logging.INFO)
    dev_manager = KSerialManager()
    all_connected_devices = dev_manager.connect_to_all()
    if len(all_connected_devices) == 0:
        print("No devices found")
        return
    device = all_connected_devices[0]
    fail_counter = 0
    success_counter = 0
    while True:
        ret, temp_msg = device.get_device_temperatures()
        if not ret:
            fail_counter += 1
            print(f"fails: {fail_counter}, successes {success_counter}")
        else:
            success_counter+=1


        sleep(0.001)

def example_connect_and_get_device_stats():
    set_log_level(logging.INFO)
    dev_manager = KSerialManager()
    all_connected_devices = dev_manager.connect_to_all()
    if len(all_connected_devices) == 0:
        print("No devices found")
        return
    device = all_connected_devices[0]
    ret, stats = device.get_device_stats()
    if not ret:
        print("Couldnt read stats")
        return False
    print(stats)
#example_connect_and_get_info()
#example_connect_and_get_power_state()
example_connect_and_get_device_stats()