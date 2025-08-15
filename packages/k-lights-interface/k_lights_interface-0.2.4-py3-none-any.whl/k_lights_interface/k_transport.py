from typing import Tuple
from abc import ABC, abstractmethod

import betterproto
import k_lights_interface.proto_protocol as light_protocol




class KTransport(ABC):

    @abstractmethod
    def get_transport_type(self) -> str:
        pass

    @abstractmethod
    def get_mac_addr(self) -> str:
        pass
    
    @abstractmethod
    def try_connect(self, force_reconnect: bool) -> bool:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def execute_command(self, message: light_protocol.DriverMessage, with_response: bool = True, num_tries=3) -> Tuple[bool, bytearray]:
        pass

    @abstractmethod
    def execute_command_with_parsing(self, message: light_protocol.DriverMessage, parsing_object, with_response: bool = True, num_tries=3) -> Tuple[bool, betterproto.Message]:
        pass