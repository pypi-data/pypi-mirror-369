from k_lights_interface.k_serial_manager import KSerialManager
from k_lights_interface.k_logging import set_log_level, logging
import k_lights_interface.proto_protocol as kprot
from time import sleep

def example_use_dac():
    dev_manager = KSerialManager()
    all_connected_devices = dev_manager.connect_to_all()
    #[print(dev) for dev in all_connected_devices]
    assert (len(all_connected_devices) > 0)
    k_device = all_connected_devices[0]
    print(f"Chosen device for tests: {k_device}")
    sleep(0.5)

    channel_map = {
        "RE": 1,
        "GR": 2,
        "BL": 3,
        "AM": 4,
        "CY": 5,
        "LI": 6
    }

    color = channel_map["RE"]

    channels = [0]*6
    channels[color - 1] = 50
    ret = k_device.set_emitter_output_type(kprot.EmitterOutputType.PWM_OUTPUT)
    ret = k_device.set_rgbacl_emitter_channels_without_compensation_unsafe(channels)
    if not ret:
        print("Couldnt set emitter output type")

    

        return False    
    sleep(2)


if __name__ == "__main__":
    example_use_dac()
    #set_cct_mode(2500, 0)
