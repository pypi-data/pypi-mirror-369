
import serial.tools.list_ports
from serial.tools.list_ports_common import ListPortInfo
from typing import Tuple, Set, List
from ordered_set import OrderedSet
import logging

from k_lights_interface.k_singleton import KSingletonMeta
from k_lights_interface.k_device import KDevice
from k_lights_interface.k_serial_transport import KSerialTransport
import k_lights_interface.proto_protocol as kprot

logger = logging.getLogger(__name__)

class KSerialManager(metaclass=KSingletonMeta):
    def __init__(self):
        self.devices: OrderedSet[KDevice] = OrderedSet([])

    def get_first_available_device(self, allowed_names: List[str] = []) -> KDevice | None:
        if len(self.devices) == 0:
            currently_available_boxes = KSerialManager().connect_to_all(True, allowed_names=allowed_names)
            return currently_available_boxes[0] if len(currently_available_boxes) > 0 else None
        return self.devices[0]

    def connect_to_all(self, remove_disconnected : bool = False, allowed_names: List[str] = []) -> OrderedSet[KDevice]:
        """Connect and initialize KDevice objects for all kelvin serial devices connected to the computer.

        Args:
            remove_disconnected (bool, optional): If True, remove disconnected devices from the device list. Defaults to False.
        Returns:
            OrderedSet[KDevice]: A set of KDevice objects
        """
        if remove_disconnected:
            self.__remove_disconnected_devices()
        possible_ports = self.__get_possible_ports()
        for port in possible_ports:
            device = self.connect_to_device(port, allowed_names)
            if not device:
                continue
            mcumgr_conn_string = self.__get_mcumgr_conn_string(port, device.serial_number)
            if mcumgr_conn_string:
                device.mcumgr_conn_string = mcumgr_conn_string

        return self.devices


    def connect_to_device(self, port: ListPortInfo, remove_disconnected : bool = False, allowed_names: List[str] = []) -> KDevice | None:
        """ Try to connect to a kelvin device using a ListPortInfo object 

        Args:
            port (ListPortInfo): You can get this from serial.tools.list_ports
            remove_disconnected (bool, optional): If True, remove disconnected devices from the device list. Defaults to False.

        Returns:
            KDevice | None: Returns a KDevice object if successful, otherwise None
        """
        if remove_disconnected:
            self.__remove_disconnected_devices()
        ret, name, serial_number, fw_version = self.__try_get_device_info(port)
        if not ret:
            return None
        if allowed_names and name not in allowed_names:
            logger.info(f"Device {name} is not in the allowed names list. Skipping connection.")
            return None
        k_transport = KSerialTransport(port)
        device = self.__try_find_k_device(serial_number)
        if device:
            # If we already have a device with this serial number, update the transport
            device.k_transport = k_transport
        else:
            device = KDevice(name, serial_number, fw_version, k_transport)
        self.devices.add(device)
        return device


    def get_devices_with(self, names: List[str] | None, serial_numbers: List[str]| None ) ->  OrderedSet[KDevice]:
        """Get KDevices matching given names and/or serial numbers from the current devices ordered set.

        Args:
            names (List[str] | None): device names to match
            serial_numbers (List[str] | None): serial numbers to match

        Returns:
            OrderedSet[KDevice]: An ordered set of KDevice objects
        """
        if not names and not serial_numbers:
            return self.devices
        new_set = OrderedSet([])
        if names:
            new_set |= OrderedSet([device for device in self.devices if device.name in names])
        if serial_numbers:
            new_set |=  OrderedSet([device for device in self.devices if device.serial_number in serial_numbers])
        return new_set


    def __try_find_k_device(self, serial_number :str) -> KDevice | None:
        for device in self.devices:
            if device.serial_number == serial_number:
                return device
        return None


    def __remove_devices_with(self, name:str, serial_number: str):
        self.devices = OrderedSet([device for device in self.devices if device.name != name and device.serial_number != serial_number])

    def __remove_disconnected_devices(self):
        for device in self.devices:
            ret, name = device.get_device_name()
            if not ret:
                self.devices.remove(device)
                logger.info(f"Removed device {name} from device list because it is disconnected.")


    def __try_get_device_info(self, port: ListPortInfo) -> Tuple[bool, str, str, str]:
        try:
            with KSerialTransport(port) as k_serial_controller:
                # Setting the receive timeout to short timeout to avoid this process
                # taking a lot of time if there many usb devices connected.
                k_serial_controller.receive_data_timeout_s = 0.4
                did_receive, device_id_message = k_serial_controller.execute_command_with_parsing(kprot.DriverMessage(
                    request=kprot.RequestMessage(request_type=kprot.RequestTypes.DEVICE_ID)),kprot.DeviceIdMessage, with_response=True,num_tries=1)
                if not did_receive:
                    return False, None, None, None

                name = device_id_message.name
                did_receive, serial_number_message = k_serial_controller.execute_command_with_parsing(kprot.DriverMessage(
                    request=kprot.RequestMessage(request_type=kprot.RequestTypes.SERIAL_NUMBER)),kprot.SerialNumberMessage, with_response=True,num_tries=1)
                if not did_receive:
                    return False, None, None, None
                serial_number_hex_string = serial_number_message.data.hex()

                ret, version_msg = k_serial_controller.execute_command_with_parsing(kprot.DriverMessage(
                    request=kprot.RequestMessage(request_type=kprot.RequestTypes.VERSION)),kprot.VersionMessage, with_response=True,num_tries=1)
                if not ret:
                    return False, None, None, None
                fw_version_str = str(version_msg.major) + "." + str(version_msg.minor) + "." + str(version_msg.revision) + "+" + str(version_msg.build)
                return True, name, serial_number_hex_string, fw_version_str
        except Exception as e:
            return False, None, None, None
        
    def __get_mcumgr_conn_string(self, api_port: ListPortInfo, serial_number: str) -> str | None:
        all_ports = self.__get_possible_ports()
        for port in all_ports:
            if port.serial_number.lower() == serial_number.lower() and port != api_port:
                return port.device
        return None


    def __get_possible_ports(self) -> List[ListPortInfo]:
        vid_list = [12259, 0xABCD]
        ports = serial.tools.list_ports.comports(include_links=False)
        valid_ports = [port for port in ports if port.vid in vid_list or port.manufacturer == "FTDI"]
        return valid_ports
