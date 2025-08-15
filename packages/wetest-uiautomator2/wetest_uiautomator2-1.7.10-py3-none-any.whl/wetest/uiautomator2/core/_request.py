# !/usr/bin/python3
# coding: utf-8

import json
import requests

from typing import Dict, Optional, Union
from http.client import HTTPConnection
from requests.exceptions import HTTPError
from adbutils import AdbDevice, Network
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from ._const import *
from ._types import BaseResp, ErrorMsg, Method
from ._logger import Logger
from ._adapter import DeviceUSBConnection


class BaseRequest:
    def __init__(self, method: Method, url: str, headers=None, params=None, body=None):
        self.method = method
        self.url = url
        self.headers = headers if headers else {HEADER_KEY: HEADER_VAL}
        self.params = params
        self._body = body

    def body(self, body):
        if body:
            self._body = json.loads(body) if isinstance(body, str) else body
        return self

    def to_url(self):
        body = json.dumps(self._body) if self._body else ""
        return f"$ curl -X {self.method} -d '{body}' -H '{HEADER_KEY}:{HEADER_VAL}' '{self.url}'"

    def send(self):
        raise NotImplementedError


class HTTPResponseWrapper:
    def __init__(self, content: bytes, status_code: int):
        self.content = content
        self.status_code = status_code

    def json(self):
        return json.loads(self.content)

    @property
    def text(self) -> str:
        return self.content.decode("utf-8")

    def getcode(self) -> int:
        return self.status_code


def fetch(
    url: str,
    conn: Union[HTTPConnection, DeviceUSBConnection],
    method: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, str]] = None,
) -> HTTPResponseWrapper:
    u = urlparse(url)
    existing_params = parse_qs(u.query)
    if params:
        for key, value in params.items():
            existing_params[key] = [value]
    final_query = urlencode(existing_params, doseq=True)
    new_url = urlunparse(u._replace(query=final_query))
    new_u = urlparse(new_url)

    conn.request(
        method,
        new_u.path + "?" + new_u.query if new_u.query else new_u.path,
        body=json.dumps(body),
        headers=headers,
    )
    response = conn.getresponse()
    content = response.read()
    response = HTTPResponseWrapper(content, response.status)
    return response


class HttpRequest(BaseRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send(self, timeout) -> HTTPResponseWrapper:
        u = urlparse(self.url)
        conn = HTTPConnection(u.netloc, timeout=timeout)
        response = fetch(
            self.url,
            conn,
            method=self.method.value,
            headers=self.headers,
            params=self.params,
            body=self._body,
        )
        return response


class DeviceRequest(BaseRequest):
    def __init__(self, device: AdbDevice, device_port: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = device
        self.device_port = device_port

    def send(self, timeout) -> HTTPResponseWrapper:
        sock = self.device.create_connection(Network.TCP, self.device_port)
        conn = DeviceUSBConnection(sock, timeout)
        response = fetch(
            self.url,
            conn,
            method=self.method.value,
            headers=self.headers,
            params=self.params,
            body=self._body,
        )
        sock.close()
        return response


class Constructor:
    class http:
        @staticmethod
        def get(url: str, headers=None, params=None) -> HttpRequest:
            return HttpRequest(Method.GET, url, headers, params)

        @staticmethod
        def post(url: str, headers=None) -> HttpRequest:
            return HttpRequest(Method.POST, url, headers)

        @staticmethod
        def put(url: str, headers=None) -> HttpRequest:
            return HttpRequest(Method.PUT, url, headers)

        @staticmethod
        def delete(url: str, headers=None) -> HttpRequest:
            return HttpRequest(Method.DELETE, url, headers)

        @staticmethod
        def patch(url: str, headers=None) -> HttpRequest:
            return HttpRequest(Method.PATCH, url, headers)

    class device:
        @staticmethod
        def get(device: AdbDevice, url: str, device_port: int, headers=None, params=None) -> DeviceRequest:
            return DeviceRequest(device, device_port, Method.GET, url, headers, params)

        @staticmethod
        def post(device: AdbDevice, url: str, device_port: int, headers=None) -> DeviceRequest:
            return DeviceRequest(device, device_port, Method.POST, url, headers)

        @staticmethod
        def put(device: AdbDevice, url: str, device_port: int, headers=None) -> DeviceRequest:
            return DeviceRequest(device, device_port, Method.PUT, url, headers)

        @staticmethod
        def delete(device: AdbDevice, url: str, device_port: int, headers=None) -> DeviceRequest:
            return DeviceRequest(device, device_port, Method.DELETE, url, headers)

        @staticmethod
        def patch(device: AdbDevice, url: str, device_port: int, headers=None) -> DeviceRequest:
            return DeviceRequest(device, device_port, Method.PATCH, url, headers)


class Requester:
    DEFAULT_REQUEST_TIMEOUT = 15000

    def __init__(self, logger: Logger):
        self._timeout: int = self.DEFAULT_REQUEST_TIMEOUT
        self.logger = logger

    def set_request_timeout(self, timeout: int) -> None:
        self._timeout = timeout

    def send(
        self, request: Union[HttpRequest, DeviceRequest], timeout: Optional[int] = None, debug: bool = False
    ) -> BaseResp:
        timeout = timeout if timeout is not None else self._timeout
        if debug:
            self.logger.info(f"{request.to_url()}")
        try:
            response = request.send(timeout=timeout)
            return self._init_resp(response)
        except (HTTPError, requests.exceptions.RequestException) as e:
            raise Exception(e)

    def _init_resp(self, resp_instance: HTTPResponseWrapper) -> BaseResp:
        response = resp_instance.text
        if "traceback" in response or "stacktrace" in response:
            response = response.replace("stacktrace", "traceback")
            return Requester.init_error_msg(response)
        else:
            try:
                response_dict: dict = json.loads(response)
            except json.JSONDecodeError:
                raise ValueError(f"{response} cannot be deserialized!")
            return BaseResp(session_id=response_dict["sessionId"], value=response_dict["value"])

    @staticmethod
    def init_header() -> Dict[str, str]:
        headers: Dict[str, str] = {"Content-Type": "application/json; charset=utf-8"}
        return headers

    @staticmethod
    def init_error_msg(resp: str) -> BaseResp:
        err_dict: dict = json.loads(resp)
        error_msg_dict = err_dict.get("value", {})
        error_msg = ErrorMsg(**error_msg_dict)
        err = BaseResp(err=error_msg, session_id=err_dict["sessionId"])
        return err
