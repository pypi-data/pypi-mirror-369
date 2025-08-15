import socket

from adbutils import Network, adb
from http.client import HTTPConnection
from typing import Union

from ._exceptions import ADBDeviceException, ADBDeviceNotFoundException


class DeviceUSBConnection(HTTPConnection):
    def __init__(self, identifier: Union[socket.socket, str], timeout=60):
        super(DeviceUSBConnection, self).__init__("127.0.0.1", timeout=timeout)
        self.timeout = timeout
        self.identifier = identifier
        self.sock = None
        self.udid = None

    def connect(self):
        if isinstance(self.identifier, socket.socket):
            self.sock = self.identifier
            self.sock.settimeout(self.timeout)
            return
        if isinstance(self.identifier, str):
            devices = adb.device_list()
            if not devices:
                raise ADBDeviceException("no device connected.")
            for d in devices:
                if d.serial == self.identifier:
                    self.sock = d.create_connection(Network.TCP, 6790)
                    self.sock.settimeout(self.timeout)
                    return
            raise ADBDeviceNotFoundException(f"cannot find devices with serial udid {self.identifier}")
        raise ValueError("identifier must be a socket or a string of udid")

    def __enter__(self) -> HTTPConnection:
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
