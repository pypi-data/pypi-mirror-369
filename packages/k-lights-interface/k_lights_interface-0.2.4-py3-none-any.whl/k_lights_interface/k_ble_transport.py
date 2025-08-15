
import sys
from typing import Tuple
import time
import datetime
import asyncio
from typing import List
import betterproto
from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.characteristic import BleakGATTCharacteristic
import nest_asyncio

import k_lights_interface.k_logging as k_log
import k_lights_interface.proto_protocol as kprot
from k_lights_interface.k_transport import KTransport

logger = k_log.logging.getLogger(__name__)

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"



class RxPacket:
    def __init__(self, bytes :bytearray):
        self.bytes = bytes
        self.timestamp = datetime.datetime.now()

class KBleTransport(KTransport):
    receive_data_timeout_s = 2

    __ble_device: BLEDevice = None
    __bleak_client: BleakClient = None
    __ble_lock : asyncio.Lock = None

    __rx_packets : List[RxPacket] = []

    purge_rx_packets_older_than_s = 5

    def init(self, lock: asyncio.Lock,  device: BLEDevice):
        # Only apply the nest_asyncio patch if this class is used.
        nest_asyncio.apply()
        self.__ble_lock = lock
        self.__ble_device = device

    async def try_connect(self, force_reconnect: bool = False) -> bool:
        async with self.__ble_lock:
            try:
                if self.__bleak_client and self.__bleak_client.is_connected and not force_reconnect:
                    return True
                self.__bleak_client = BleakClient(self.__ble_device,disconnected_callback=self.handle_disconnect)
                did_connect = await self.__bleak_client.connect()
                if not did_connect:
                    logger.error(f"Could not connect to {self.__ble_device.address}")
                    return False
                logger.info(f"Connected to {self.__ble_device.address}")
                await self.__bleak_client.start_notify(UART_RX_CHAR_UUID, self.rx_handler)
                return True
            except Exception as e:
                logger.error(f"Exception in try_connect: {e}")
                return False

    def handle_disconnect(self, bleak_client: BleakClient):
        logger.info(f"Disconnected from {bleak_client.address}")

    def rx_handler(self, gatt_char: BleakGATTCharacteristic, data: bytearray):
        logger.info(f"Received {data} from {gatt_char} with uuid(mac_address??) {gatt_char.uuid}")
        list(filter(lambda obj:  (datetime.datetime.now - obj.timestamp).total_seconds() <  self.purge_rx_packets_older_than_s, self.__rx_packets))
        self.__rx_packets.append(RxPacket(data))

    def get_transport_type(self) -> str:
        return "ble"

    def get_mac_addr(self) -> str:
        if sys.platform == "darwin":
            return self.__ble_device.address.replace("-", "").lower()
        return self.__ble_device.address.lower()

    def is_connected(self) -> bool:
        return self.__bleak_client.is_connected

    def execute_command(self, message: kprot.DriverMessage, with_response: bool = True, num_tries=3) -> Tuple[bool, bytearray]:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                return False, bytearray()
            return loop.run_until_complete(self.__execute_command_once_async(message, with_response))
        except Exception as e:
            logger.info(f"Exception in execute_command: {e}")
            return False, bytearray()

    def execute_command_with_parsing(self, message: kprot.DriverMessage, parsing_object, with_response: bool = True, num_tries=3) -> Tuple[bool, betterproto.Message]:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                return False, None
            return loop.run_until_complete(self.execute_command_with_parsing_async(message, parsing_object, with_response, num_tries))
        except Exception as e:
            logger.info(f"Exception in execute_command: {e}")
            return False, None
        
    async def execute_command_with_parsing_async(self, message: kprot.DriverMessage, parsing_object, with_response: bool = True, num_tries=3) -> Tuple[bool, betterproto.Message]:
        ret, rx_data = await self.execute_command_async(message, with_response, num_tries)
        if not ret or not rx_data or len(rx_data) == 0:
            return False, None
        try:
            parsing_instance = parsing_object()
            return True, parsing_instance.FromString(rx_data)
        except Exception as e:
            logger.info(f"Exception in execute_command_with_parsing: {e}")
            return False, None


    async def execute_command_async(self, message: kprot.DriverMessage, with_response: bool = True, num_tries=3) -> Tuple[bool, bytearray]:
        for i in range(num_tries):
            try:
                ret, bytes_data = await self.__execute_command_once_async(message, with_response)
                if ret:
                    return True, bytes_data
            except Exception as e:
                pass

        return False, bytearray()

    async def __execute_command_once_async(self, message: kprot.DriverMessage, with_response: bool = True) -> Tuple[bool, bytearray]:
        if not self.__bleak_client:
            logger.info("No bleak client. Forgot to connect?")
            return False, bytearray()
                
        if not self.__bleak_client.is_connected:
            logger.info("Bleak client not connected")
            return False, bytearray()
        self.__rx_packets.clear()
        async with self.__ble_lock:
            await self.__bleak_client.write_gatt_char(UART_TX_CHAR_UUID, bytes(message), response=False)
        if not with_response:
            return True, bytearray()
        start_time = time.time()
        while (time.time() - start_time) < self.receive_data_timeout_s:
            if not self.__rx_packets:
                await asyncio.sleep(0.05)
                continue
            rx_packet = self.__rx_packets.pop()
            if self.__is_nack(rx_packet.bytes):
                return False, bytearray()
            return True, rx_packet.bytes
            
        return False, bytearray()


    def __is_nack(self, rx_data: bytearray) -> bool:
        try:
            nack_message =   kprot.NackMessage.FromString(rx_data)
            if nack_message.nack_hack_id and nack_message.nack_hack_id == 0xBEFEADED:
                logger.info("Received NACK")
                return True
        except:
            pass
        return False

    def __del__(self):
        try:
            pass #self.__bleak_client.disconnect()
        except:
            pass