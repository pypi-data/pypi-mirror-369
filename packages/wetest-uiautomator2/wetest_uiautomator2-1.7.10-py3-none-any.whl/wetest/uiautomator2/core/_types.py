# !/usr/bin/python3
# coding: utf-8

import inspect
import weakref

from enum import Enum
from functools import partial
from dataclasses import dataclass, asdict
from typing import Any, Optional, Dict, List
from abc import ABC, abstractmethod
from adbutils import AdbDevice

from ._const import GET_TAG, POST_TAG


class ConnType(str, Enum):
    HTTP_URL = "url"
    ADBDEVICE = "device"
    SOCKET = "socket"


@dataclass
class ClientIdentifier:
    t: ConnType = ConnType.HTTP_URL
    url: str = ""
    device: AdbDevice = None
    port: int = None


@dataclass
class ErrorMsg:
    error: str
    message: str
    traceback: str


@dataclass
class BaseResp:
    session_id: str = ""
    err: Optional[ErrorMsg] = None
    value: Any = None


class BaseClient(ABC):
    @abstractmethod
    def get(self, api: str, timeout: int = None) -> BaseResp:
        raise NotImplementedError

    @abstractmethod
    def get_without_session(self, api: str, timeout: int = None) -> BaseResp:
        raise NotImplementedError

    @abstractmethod
    def post(self, api: str, data: any = None, timeout: int = None) -> BaseResp:
        raise NotImplementedError

    @abstractmethod
    def post_without_session(self, api: str, data: any = None, timeout: int = None) -> BaseResp:
        raise NotImplementedError

    @abstractmethod
    def _handle_get(
        self,
        resp: BaseResp = None,
        body: Any = None,
        log_body: bool = True,
        stack_depth: int = 1,
        info: str = None,
        prefix: str = GET_TAG,
        suffix: str = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def _handle_post(
        self,
        resp: BaseResp = None,
        body: Any = None,
        log_body: bool = True,
        stack_depth: int = 1,
        info: str = None,
        prefix: str = POST_TAG,
        suffix: str = None,
    ):
        raise NotImplementedError


class BaseElement:
    def __init__(self, id: str, client):
        self.id = id
        self._client: BaseClient = weakref.proxy(client)
        self.logger = client.get_logger()


@dataclass
class BaseGesture:
    x: float
    y: float
    time: float

    def to_json(self):
        return {
            "touch": {"x": self.x, "y": self.y},
            "time": self.time,
        }


@dataclass
class Gesture:
    gesture: List[BaseGesture]

    def to_json(self):
        return [x.to_json() for x in self.gesture]


@dataclass
class AppiumLocator:
    strategy: str
    selector: str
    context: str

    def to_json(self):
        return asdict(self)


@dataclass
class ScheduledStep:
    type: str
    name: str
    payload: Dict[str, any]

    def to_json(self):
        return asdict(self)


class Method(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class PasteboardType(str, Enum):
    PLAIN_TEXT = "plaintext"
    IMAGE = "image"
    URL = "url"


class Selector(str, Enum):
    CLASS_NAME = "class name"
    Id = "id"
    ACCESSIBILITY_ID = "accessibility id"
    XPATH = "xpath"
    UIAUTOMATOR = "-android uiautomator"


@dataclass
class WindowSize:
    width: int
    height: int

    def __str__(self):
        return f"WindowSize(width={self.width}, height={self.height})"


@dataclass
class Rect:
    x: int
    y: int
    width: int
    height: int
