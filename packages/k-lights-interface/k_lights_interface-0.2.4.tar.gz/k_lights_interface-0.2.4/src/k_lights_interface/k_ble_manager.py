
import asyncio
import logging

from typing import Set, Tuple, List
from ordered_set import OrderedSet
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from k_lights_interface.k_ble_transport import KBleTransport, UART_SERVICE_UUID, UART_TX_CHAR_UUID, UART_RX_CHAR_UUID
from k_lights_interface.k_singleton import KSingletonMeta
from k_lights_interface.k_device import KDevice
import k_lights_interface.k_device_names as kdn
import k_lights_interface.proto_protocol as kprot


logger = logging.getLogger(__name__)


class KAdvertisingInfo:
    def __init__(self, name, mac_address, device: BLEDevice,  adv_data: AdvertisementData):
        self.name = name
        self.mac_address = mac_address
        self.last_received_adv_data = adv_data
        self.last_received_ble_device = device

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, KAdvertisingInfo):
            return self.mac_address == __value.mac_address
        return False

    def __hash__(self) -> int:
        return hash(self.mac_address)

    def __str__(self):
        return f"{self.name} {self.mac_address}"


class KBleManager(metaclass=KSingletonMeta):
    def __init__(self):
        self.k_devices: OrderedSet[KDevice] = OrderedSet([])
        self.__ble_lock = asyncio.Lock()
        self.__scanner = BleakScanner(self.__advertising_callback, [UART_SERVICE_UUID])
        self.__accumulated_advertising_info = OrderedSet([])

    async def scan(self, scan_duration_s: float) -> OrderedSet[KAdvertisingInfo]:
        """Scan for Kelvin devices for a given duration

        Args:
            scan_duration_s (float): How long to scan for

        Returns:
            OrderedSet[KAdvertisingInfo]: A set of KAdvertisingInfo objects
        """
        async with self.__ble_lock:
            self.__accumulated_advertising_info.clear()
            await self.__scanner.start()
            await asyncio.sleep(scan_duration_s)
            await self.__scanner.stop()
            logger.info(f"Finished scanning. Found {len(self.__accumulated_advertising_info)} devices")
            for k_adv_info in self.__accumulated_advertising_info:
                logger.info(f"Found {k_adv_info}")
            return self.__accumulated_advertising_info

    async def connect_to_all(self, scan_duration_s: float = 5, connection_retry_attemps: int = 3) -> OrderedSet[KDevice]:
        """Scan for Kelvin devices and try to connect to each one

        Args:
            scan_duration_s (float, optional): scanning duration in seconds . Defaults to 5.
            connection_retry_attemps (int, optional): number of connection attemps. Defaults to 4.

        Returns:
            OrderedSet[KDevice]: All connected KDevice objects
        """
        await self.scan(scan_duration_s)
        for k_adv_info in self.__accumulated_advertising_info:
            await self.connect_to_device_with_tries(k_adv_info, connection_retry_attemps)
        return self.k_devices
    
    async def connect_to_all_with_names(self, valid_names : List[str],  scan_duration_s: float = 5, connection_retry_attemps: int = 3) -> OrderedSet[KDevice]:
        """Scan for Kelvin devices that advertise a certain name and try to connect to each one

        Args:
            scan_duration_s (float, optional): scanning duration in seconds . Defaults to 5.
            connection_retry_attemps (int, optional): number of connection attemps. Defaults to 4.

        Returns:
            OrderedSet[KDevice]: All connected KDevice objects
        """
        await self.scan(scan_duration_s)
        for k_adv_info in self.__accumulated_advertising_info:
            if k_adv_info.name in valid_names:
                await self.connect_to_device_with_tries(k_adv_info,connection_retry_attemps)
        return self.k_devices

    async def connect_to_device_with_tries(self, k_adv_info: KAdvertisingInfo, num_tries: int = 3) -> KDevice | None:
        """Connect to a device with a specific KAdvertisingInfo object.

        Args:
            k_adv_info (KAdvertisingInfo): The KAdvertisingInfo object to connect to
            num_tries (int, optional): . Defaults to 3.

        Returns:
            KDevice | None: The connected KDevice or None if not connected
        """
        for i in range(num_tries):
            k_device = await self.__connect_to_device(k_adv_info)
            if k_device:
                return k_device
        return None

    async def __connect_to_device(self, k_adv_info: KAdvertisingInfo) -> KDevice | None:
        device = self.__find_k_device_with_uuid(k_adv_info.mac_address)
        if device and device.k_transport.is_connected() == True:
            return device
        elif device and device.k_transport.is_connected() == False:
            logger.info(f"Found {device.name} but it is not connected. Connecting...")
            did_connect = await device.k_transport.try_connect(force_reconnect=True)
            if not did_connect:
                logger.error(f"Could not connect to {device.name}")
                return None
            logger.info(f"Connected to {device.name}")
            return device

        device = k_adv_info.last_received_ble_device
        k_ble_transport = KBleTransport()
        k_ble_transport.init(self.__ble_lock, device)
        did_connect = await k_ble_transport.try_connect()
        if not did_connect:
            logger.error(f"Could not connect to {device.address}")
            return None
        logger.info(f"Connected to {device.address}")
        ret, name, serial_number_hex_string, fw_version = await self.__try_get_device_info(k_ble_transport)
        if not ret:
            logger.error(f"Could not get device info from {device.address}")
            return None
        k_device = KDevice(name, serial_number_hex_string, fw_version, k_ble_transport)
        k_device.mcumgr_conn_string = k_ble_transport.get_mac_addr()
        self.k_devices.add(k_device)
        return k_device

    async def __try_get_device_info(self, k_ble_transport: KBleTransport) -> Tuple[bool, str, str, str]:
        try:
            did_receive, device_id_message = await k_ble_transport.execute_command_with_parsing_async(kprot.DriverMessage(
                request=kprot.RequestMessage(request_type=kprot.RequestTypes.DEVICE_ID)), kprot.DeviceIdMessage, with_response=True, num_tries=1)
            if not did_receive:
                return False, None, None, None
            name = device_id_message.name
            did_receive, serial_number_message = await k_ble_transport.execute_command_with_parsing_async(kprot.DriverMessage(
                request=kprot.RequestMessage(request_type=kprot.RequestTypes.SERIAL_NUMBER)), kprot.SerialNumberMessage, with_response=True, num_tries=1)
            if not did_receive:
                return False, None, None, None
            serial_number_hex_string = serial_number_message.data.hex()

            ret, version_msg = await k_ble_transport.execute_command_with_parsing_async(kprot.DriverMessage(
                    request=kprot.RequestMessage(request_type=kprot.RequestTypes.VERSION)),kprot.VersionMessage, with_response=True,num_tries=1)
            if not ret:
                return False, None, None, None
            fw_version_str = str(version_msg.major) + "." + str(version_msg.minor) + "." + str(version_msg.revision) + "+" + str(version_msg.build)
            return True, name, serial_number_hex_string, fw_version_str
        except Exception as e:
            return False, None, None, None

    def __find_k_device_with_uuid(self, mac_address: str) -> KDevice | None:
        """Find a KDevice with a given mac address

        Args:
            mac_address (str): The mac_address to search for

        Returns:
            KDevice | None: The KDevice with the given mac_address or None if not found
        """
        for device in self.k_devices:
            if device.k_transport.get_mac_addr() == mac_address:
                return device
        return None

    # def __has_k_device_for_adv_info(self, k_adv_info : KAdvertisingInfo) -> bool:
    #     return any([connected_device.k_transport.get_mac_addr() == k_adv_info.mac_address for connected_device in self.k_devices])

    def __advertising_callback(self, device: BLEDevice, advertisement_data: AdvertisementData):
        if device.name in kdn.valid_btle_adv_names:
            logger.info("%s: %r", device.address, advertisement_data)
            index = self.__accumulated_advertising_info.add(KAdvertisingInfo(device.name, device.address, device, advertisement_data))
            self.__accumulated_advertising_info[index].last_received_adv_data = advertisement_data
            self.__accumulated_advertising_info[index].last_received_ble_device = device
