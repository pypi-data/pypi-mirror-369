# !/usr/bin/python3
# coding: utf-8

from __future__ import annotations

import re
import json
import time
import inspect
import xml.etree.ElementTree as ET

from base64 import b64decode, b64encode
from typing import Any, Dict, List, Tuple, Union, Optional, Callable
from adbutils import AdbDevice, adb

from .core._selector import AttrSelector
from .core._xpath import make_xpath
from .core._const import *
from .core._types import BaseResp, BaseClient
from .core._types import (
    WindowSize,
    Gesture,
    ScheduledStep,
    AppiumLocator,
    Selector,
    ConnType,
    ClientIdentifier,
    Rect,
)
from .core._utils import Expectation
from .core._logger import Logger
from .core._request import Constructor, Requester
from .core._exceptions import AppiumAndroidException
from .android_element import AndroidElement


def url(*urls) -> str:
    return "/".join([u.strip("/") for u in urls if u])


def default_url() -> str:
    return f"{DEFAULT_URL}:{DEFAULT_PORT}"


class AndroidDriver(BaseClient):
    """
    Client of uiautomator2 server

    Server offical document:
    https://github.com/appium/appium-uiautomator2-driver
    """

    FIND_ELEMENT_INTERVAL = 1000
    FIND_ELEMENT_RETRY = 5

    def __init__(
        self,
        identifer: Union[str, AdbDevice],
        session_id: str = None,
        timeout=Requester.DEFAULT_REQUEST_TIMEOUT,
        capbilities=None,
        debug: bool = False,
        traceback: bool = False,
        port: int = DEFAULT_PORT,
    ):
        """
        Init AndroidDriver

        Args:
            identifer (Union[str, AdbDevice]): Http address/ AbdDevice/ device serial.
            session_id (str): Pass if you have already created a session on server. Defaults to None.
            timeout (_type_, optional): Request timeout. Defaults to RespHandler.DEFAULT_REQUEST_TIMEOUT.
            capbilities (dict, optional): Appium server capability args. Defaults to {}.
            debug (bool, optional): True for generating equivalent curl links for requests. Defaults to False.
            traceback (bool, optional): True for logging tracebacks of response errors. Defaults to False.
            port(int, optional): ADBDevice socket port number that matches the server. Default to 6790.
        """
        self.session_id = ""
        self.size = None
        self.logger = Logger()
        self.requester = Requester(self.logger)

        self._id = ClientIdentifier()
        self._device = None
        self._debug = debug
        self._traceback = traceback

        self.set_identifier(identifer, port)
        self.requester.set_request_timeout(timeout)
        if not session_id:
            self.new_session(capbilities if capbilities else {})
        else:
            self.session_id = session_id

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def close(self):
        self.close_session()

    def expect(
        self,
        msg: str = None,
        err: Exception = None,
        show_log: bool = True,
        handler: Callable = None,
        *args,
        **kwargs,
    ) -> AndroidDriver:
        """
        Usage: android_driver.expect().method(*args, **kwargs).

        The internal exception handler.
        It can be elegantly combined with interfaces that need try-catch a lot.
        It transmits all method calls to the instance, and automatically skip or raise exceptions.
        It supports printing messages, raising custom exception and call function with args.
        When an exception is skipped, an NothingType instance will be returned.
        NothingType responses and then ignores any method call to prevent error caused by chaining.
        Inspired by expect() method in Rust.

        Args:
            msg (str, optional): The message to be printed when error catched. Defaults to None.
            err (Exception, optional):
                Raise err instead of the actual catched one. Defaults to None.
                Return a NothingType if err is None. Nothing type ignores any method calls without errors.
            show_log (bool, optional): True for print logs for debugging. Defaults to False.
            handler (Callable, optional):
                Function to be called when error catched.
                    Defaults to None.
                Especially, if handler() takes the argument "exception", the function call will be:
                    handler(exception=e, *args, **kwargs), where e is the exception that catched.
                Otherwise, the function call will be:
                    handler(*args, **kwargs).
            *args, **kwargs: The arguments to be passed to handler.

        Returns:
            AndroidDriver <- Expectation: a wrapped Self.
        """
        return Expectation(self, msg, err, self.logger, show_log, handler, *args, **kwargs)

    @property
    def e(self):
        return self.expect()

    @property
    def debug(self):
        """
        Set or get the flag for generating equivalent curl links for requests.
        """
        return self._debug

    @debug.setter
    def debug(self, val: bool):
        self._debug = val

    @property
    def traceback(self):
        """
        Set or get the flag for logging tracebacks of response errors.
        """
        return self._traceback

    @traceback.setter
    def traceback(self, val: bool):
        self._traceback = val

    def enable_log(self):
        """
        Enable the logger.
        """
        self.logger.enable_log()

    def disable_log(self):
        """
        Disable the logger.
        """
        self.logger.disable_log()

    def set_identifier(self, identifer: Union[str, AdbDevice], port: int):
        """
        Set the identifier of the client.

        Args:
            identifer (Union[str, AdbDevice]): Http address/AbdDevice/device serial.
            port (int): The port to connect to. Defaults to DEFAULT_PORT.

        Returns:
            ClientIdentifier: The client identifier object.

        Raises:
            ValueError: If the identifier args has wrong class.
        """
        # Create from url. For example: "http://localhost:6790"
        if isinstance(identifer, str) and identifer.startswith("http://"):
            self._remote_url = identifer
            self._id = ClientIdentifier(t=ConnType.HTTP_URL, url=identifer, device=None, port=port)
            self.logger.info(f"{INIT_TAG} client created from {self._id.t.value.upper()} : {self._id.url}")
            return self._id
        # Create from AdbDevice()
        if isinstance(identifer, AdbDevice):
            self._device = identifer
        # Create from device serial
        elif adb.device(identifer):
            self._device = adb.device(identifer)
        else:
            raise ValueError("Client identifier must be a url string, an AdbDevice or a device serial.")
        self._remote_url = default_url()
        self._id = ClientIdentifier(t=ConnType.ADBDEVICE, url=default_url(), device=identifer, port=port)
        self.logger.info(
            f"{INIT_TAG} client created from {self._id.t.value.upper()} : {self._id.device.serial}"
            + f", to port {self._id.port}"
        )
        return self._id

    """ ===========================================================================
        NOTE: Global GET and POST methods HERE

        EXAMPLES:
            resp = self.get("api")
            return self.handle_get(resp, "message")

            data = {key: value, ...}
            resp = self.post("/api", data)
            return self.handle_post(resp, "message", data)
        ===========================================================================
    """

    def _base_get(self, api: str, timeout: int = None) -> BaseResp:
        if self._id.t is ConnType.HTTP_URL:
            return self.requester.send(Constructor.http.get(api), timeout, debug=self._debug)
        if self._id.t is ConnType.ADBDEVICE:
            return self.requester.send(
                Constructor.device.get(self._id.device, api, self._id.port), timeout, debug=self._debug
            )
        return None

    def _base_post(self, api: str, data: any = None, timeout: int = None) -> BaseResp:
        if self._id.t is ConnType.HTTP_URL:
            return self.requester.send(Constructor.http.post(api).body(json.dumps(data)), timeout, debug=self._debug)
        if self._id.t is ConnType.ADBDEVICE:
            return self.requester.send(
                Constructor.device.post(self._id.device, api, self._id.port).body(json.dumps(data)),
                timeout,
                debug=self._debug,
            )
        return None

    def get(self, api: str, timeout: int = None) -> BaseResp:
        """
        Basic http get method.

        Args:
            api (str): Methods for the url.
            timeout (int, optional): Request timeout. Defaults to None.

        Returns:
            BaseResp: Http response.
        """
        api = url(self._id.url, "session", self.session_id, (api if api else ""))
        return self._base_get(api, timeout)

    def post(self, api: str, data: any = None, timeout: int = None) -> BaseResp:
        """
        Basic http post method.

        Args:
            api (str): Methods for the url.
            data (any): Anything that can be serialized.
            timeout (int, optional): Request timeout. Defaults to None.

        Returns:
            BaseResp: Http response.
        """
        api = url(self._id.url, "session", self.session_id, (api if api else ""))
        return self._base_post(api, data, timeout)

    def get_without_session(self, api: str, timeout: int = None) -> BaseResp:
        """
        Basic http get method without passing sessionid.

        Args:
            api (str): Methods for the url.
            timeout (int, optional): Request timeout. Defaults to None.

        Returns:
            BaseResp: Http response.
        """
        api = url(self._id.url, (api if api else ""))
        return self._base_get(api, timeout)

    def post_without_session(self, api: str, data: any = None, timeout: int = None) -> BaseResp:
        """
        Basic http post method without passing sessionid.

        Args:
            api (str): Methods for the url.
            data (any): Anything that can be serialized.
            timeout (int, optional): Request timeout. Defaults to None.

        Returns:
            BaseResp: Http response.
        """
        api = url(self._id.url, (api if api else ""))
        return self._base_post(api, data, timeout)

    """ ===========================================================================
        NOTE: log and handle response methods HERE
        ===========================================================================
    """

    def raise_err_with_traceback(self, resp: BaseResp):
        """
        Raise error from Baseresp

        Args:
            resp (BaseResp): Response from get() and post()

        Raises:
            AppiumAndroidException: Response message. Server traceback message if self._traceback.
        """
        info = resp.err.message + (":\n" + resp.err.traceback) if self._traceback else ""
        raise AppiumAndroidException(info)

    def __handle_and_log(self, info: str, resp: BaseResp, body: Any, log_body: bool):
        if resp.err is None:
            self.logger.info(f"{info} succeeded" + (f": {str(body)}" if log_body else "."))
        else:
            self.logger.error(f"{info} failed.")
            self.raise_err_with_traceback(resp)

    def _handle_get(
        self,
        resp: BaseResp = None,
        body: Any = None,
        log_body: bool = True,
        stack_depth: int = 1,
        info: str = None,
        prefix: str = GET_TAG,
        suffix: str = None,
    ) -> None:
        """
        Handle response from self.get() and record it into logs.
        Logger format: '<prefix> <caller_name / info> <suffix>: <body>'

        Args:
            resp (BaseResp, optional): Response from self.get(). Defaults to None.
            body (Any, optional): The <body>. Defaults to resp.value.
            log_body (bool, optional): True for logging body and False for not. Defaults to True.
            stack_depth (int, optional):
                The stack depth of Python inspect module to get the <caller_name>.
                Defaults to 1.
            info (str, optional): The info string, replacing the <caller_name>. Defaults to None.
            prefix (str, optional): The <prefix>. Defaults to GET_TAG.
            suffix (str, optional): The <suffix>. Defaults to None.

        Returns:
            None
        """
        body = body if body else resp.value
        info = f"{prefix} {info if info else inspect.stack()[stack_depth].function + '()'}{(' ' + suffix) if suffix else ''}"
        return self.__handle_and_log(info, resp, body, log_body)

    def _handle_post(
        self,
        resp: BaseResp = None,
        body: Any = None,
        log_body: bool = True,
        stack_depth: int = 1,
        info: str = None,
        prefix: str = POST_TAG,
        suffix: str = None,
    ) -> None:
        """
        Handle response from self.post() and record it into logs.
        Logger format: '<prefix> <caller_name / info> <suffix>: <body>'

        Args:
            resp (BaseResp, optional): Response from self.get(). Defaults to None.
            body (Any, optional): The <body>. Defaults to None.
            log_body (bool, optional): True for logging body and False for not. Defaults to True.
            stack_depth (int, optional):
                The stack depth of Python inspect module to get the <caller_name>.
                Defaults to 1.
            info (str, optional): The info string, replacing the <caller_name>. Defaults to None.
            prefix (str, optional): The <prefix>. Defaults to POST_TAG.
            suffix (str, optional): The <suffix>. Defaults to None.

        Returns:
            None
        """
        info = f"{prefix} {info if info else inspect.stack()[stack_depth].function + '()'}{(' ' + suffix) if suffix else ''}"
        return self.__handle_and_log(info, resp, body, log_body)

    """ ===========================================================================
        NOTE: other methods HERE
        ===========================================================================
    """

    def parse_element_id(self, d: dict) -> str:
        """
        Parse response from Appium server into element id.

        Args:
            d (dict): Data body of the response returned.

        Returns:
            str: The element id.
        """
        identifier = [LEGACY_WEB_ELEMENT_IDENTIFIER, WEB_ELEMENT_IDENTIFIER]
        for i in identifier:
            result = d.get(i, "")
            if result:
                return result
        return ""

    def get_logger(self):
        return self.logger

    def new_session(self, capabilities: Dict):
        """
        Create new session and save the session id.
        Note that appium server only support ONE SESSION at a time, for now.

        Args:
            capabilities (Dict): Startup capability settings.
        """
        data = {"capabilities": capabilities}
        resp = self.post_without_session("/session", data)
        if not resp.err and resp.value["sessionId"]:
            self.session_id = resp.value["sessionId"]
            self.logger.info(f"{INIT_TAG} start session successful!")
            self.logger.info(f"{INIT_TAG} session : {self.session_id}")
        else:
            self.logger.error(f"{INIT_TAG} start session failed.")
            self.logger.error(f"{INIT_TAG} cause: {resp.err.message}")
            self.raise_err_with_traceback(resp)

    def close_session(self):
        """
        Close current session.
        """
        self._check_session_id()
        api = self._id.url + "/session/" + self.session_id
        if self._id.t is ConnType.HTTP_URL:
            return self.requester.send(Constructor.http.delete(api), debug=self._debug)
        if self._id.t is ConnType.ADBDEVICE:
            return self.requester.send(
                Constructor.device.delete(self._id.device, api, self._id.port), debug=self._debug
            )
        self.logger.info("close session successful!")

    def _check_session_id(self):
        if not self.session_id:
            self.logger.error("sessionId not found.")
            raise AppiumAndroidException("sessionId not found.")

    def set_default_find_element_interval(self, retry: int = None, interval: int = None):
        """
        Set default find element interval.

        Args:
            retry (int, optional): Retry times. Defaults to not change.
            interval (int, optional): Retry interval. Defaults to not change.
        """
        if retry is not None:
            self.FIND_ELEMENT_RETRY = retry
        if interval is not None:
            self.FIND_ELEMENT_INTERVAL = interval

    """ ===========================================================================
        NOTE: POST API HERE
        ===========================================================================
    """

    """ 
    Deprecated: Incompatible with Python version < 3.8

    from typing import Unpack
    from .core._selector import InnerSelectorTypeHint

    def find(
        self, retry: int = None, interval: int = None, **kwargs: Unpack[InnerSelectorTypeHint]
    ) -> AndroidElement:
        selector = InnerSelector(**kwargs)
        print(selector)
        return self.find_element(Selector.XPATH, make_xpath(selector), retry=retry, interval=interval)

    def finds(
        self, retry: int = None, interval: int = None, **kwargs: Unpack[InnerSelectorTypeHint]
    ) -> List[AndroidElement]:
        selector = InnerSelector(**kwargs)
        return self.find_elements(Selector.XPATH, make_xpath(selector), retry=retry, interval=interval)
    """

    def inspect(
        self,
        timeout: int = 10000,
        interval: int = 1000,
        selector: AttrSelector = None,
        text: Union[str, List[str]] = None,
        text_contains: Union[str, List[str]] = None,
        text_matches: Union[str, List[str]] = None,
        text_startswith: Union[str, List[str]] = None,
        text_endswith: Union[str, List[str]] = None,
        classname: Union[str, List[str]] = None,
        package: Union[str, List[str]] = None,
        id: Union[str, List[str]] = None,
        content_desc: Union[str, List[str]] = None,
        checkable: bool = None,
        checked: bool = None,
        clickable: bool = None,
        long_clickable: bool = None,
        focused: bool = None,
        focusable: bool = None,
        scrollable: bool = None,
        enabled: bool = None,
        selected: bool = None,
        password: bool = None,
        displayed: bool = None,
        **kwargs,
    ) -> bool:
        """
        Inspect if elements with given conditions exist.
        Optional conditions:
            * str: text, classname, package, id, resource_id, content_desc
            * bool:
                checkable, checked, clickable, long_clickable, focused, focusable, scrollable, enabled,
                selected, password, displayed
            * magic args:
                All arguments can be combined with '_contains', '_startswith', '_endswith' and '_matches'!
                XPath 2.0 supported grammar will be generated automatically.
                For instance, driver.inspect(classname_startswith="android.widget", id_contains="android:id")
        Args:
            timeout (int, optional): The inspection timeout. Defaults to 10000ms.
            interval (int, optional): The interval for inspection request. Defaults to 1000ms.

        Returns:
            bool: Flag for the existance of the target elements.
        """
        if not selector:
            d = {
                k: v
                for k, v in locals().items()
                if v is not None and k not in ("self", "timeout", "interval", "selector", "kwargs")
            }
            d.update(kwargs)
            selector = AttrSelector(**d)
        data = {"strategy": Selector.XPATH, "selector": make_xpath(selector)}
        deadline = time.time() + timeout / 1000
        while time.time() < deadline if timeout > 0 else True:
            resp = self.post("/element", data)
            if not resp.err and self.parse_element_id(resp.value):
                self.logger.info(f"{FIND_TAG} inspect element {data} successful.")
                return True
            time.sleep(interval / 1000)
        self.logger.warning(f"{FIND_TAG} inspect element {data} failed.")
        return False

    def find(
        self,
        retry: int = None,
        interval: int = None,
        selector: AttrSelector = None,
        text: Union[str, List[str]] = None,
        text_contains: Union[str, List[str]] = None,
        text_matches: Union[str, List[str]] = None,
        text_startswith: Union[str, List[str]] = None,
        text_endswith: Union[str, List[str]] = None,
        classname: Union[str, List[str]] = None,
        package: Union[str, List[str]] = None,
        id: Union[str, List[str]] = None,
        content_desc: Union[str, List[str]] = None,
        checkable: bool = None,
        checked: bool = None,
        clickable: bool = None,
        long_clickable: bool = None,
        focused: bool = None,
        focusable: bool = None,
        scrollable: bool = None,
        enabled: bool = None,
        selected: bool = None,
        password: bool = None,
        displayed: bool = None,
        **kwargs,
    ) -> AndroidElement:
        """
        Find the first element with given conditions.
        Optional conditions:
            * str: text, classname, package, id, resource_id, content_desc
            * bool:
                checkable, checked, clickable, long_clickable, focused, focusable, scrollable, enabled,
                selected, password, displayed
            * magic args:
                All arguments can be combined with '_contains', '_startswith', '_endswith' and '_matches'!
                XPath 2.0 supported grammar will be generated automatically.
                For instance, driver.find(classname_startswith="android.widget", id_contains="android:id")

        Args:
            retry (int, optional): Find retry times. Defaults to class setting (5 if not changed).
            interval (int, optional): Find retry interval ms. Defaults to class setting (1000ms if not changed).

        Raises:
            AppiumAndroidException: When element cannot be found.

        Returns:
            AndroidElement: The target element.
        """
        if not selector:
            d = {
                k: v
                for k, v in locals().items()
                if v is not None and k not in ("self", "retry", "interval", "selector", "kwargs")
            }
            d.update(kwargs)
            selector = AttrSelector(**d)
        interval = interval if interval else self.FIND_ELEMENT_INTERVAL
        retry = retry if retry else self.FIND_ELEMENT_RETRY
        return self.find_element(Selector.XPATH, make_xpath(selector), retry=retry, interval=interval)

    def finds(
        self,
        retry: int = None,
        interval: int = None,
        selector: AttrSelector = None,
        text: Union[str, List[str]] = None,
        text_contains: Union[str, List[str]] = None,
        text_matches: Union[str, List[str]] = None,
        text_startswith: Union[str, List[str]] = None,
        text_endswith: Union[str, List[str]] = None,
        classname: Union[str, List[str]] = None,
        package: Union[str, List[str]] = None,
        id: Union[str, List[str]] = None,
        content_desc: Union[str, List[str]] = None,
        checkable: bool = None,
        checked: bool = None,
        clickable: bool = None,
        long_clickable: bool = None,
        focused: bool = None,
        focusable: bool = None,
        scrollable: bool = None,
        enabled: bool = None,
        selected: bool = None,
        password: bool = None,
        displayed: bool = None,
        **kwargs,
    ) -> List[AndroidElement]:
        """
        Find the elements with given conditions.
        Optional conditions:
            * str: text, classname, package, id, resource_id, content_desc
            * bool:
                checkable, checked, clickable, long_clickable, focused, focusable, scrollable, enabled,
                selected, password, displayed
            * magic args:
                All arguments can be combined with '_contains', '_startswith', '_endswith' and '_matches'!
                XPath 2.0 supported grammar will be generated automatically.
                For instance, driver.finds(classname_startswith="android.widget", id_contains="android:id")

        Args:
            retry (int, optional): Find retry times. Defaults to class setting (5 if not changed).
            interval (int, optional): Find retry interval ms. Defaults to class setting (1000ms if not changed).

        Raises:
            AppiumAndroidException: When elements cannot be found.

        Returns:
            List[AndroidElement]: A list of the target elements.
        """
        if not selector:
            d = {
                k: v
                for k, v in locals().items()
                if v is not None and k not in ("self", "retry", "interval", "selector", "kwargs")
            }
            d.update(kwargs)
            selector = AttrSelector(**d)
        interval = interval if interval else self.FIND_ELEMENT_INTERVAL
        retry = retry if retry else self.FIND_ELEMENT_RETRY
        return self.find_elements(Selector.XPATH, make_xpath(selector), retry=retry, interval=interval)

    def find_element(self, selector: str, value: str, retry: int = None, interval: int = None) -> AndroidElement:
        """
        A rawer, lower-level interface for finding element by selector and value.
        Recommend to use self.find().

        Args:
            selector (Selector): find by CLASS_NAME, Id, ACCESSIBILITY_ID, XPATH, UIAUTOMATOR
            value (str): The keyword for element search.
            retry (int, optional): Retry times. Defaults to 5 (editable).
            interval (int, optional): Retry interval. Defaults to 1000ms (editable).

        Raises:
            AppiumAndroidException: When element cannot be found.

        Returns:
            AndroidElement: The target element.
        """
        itv = interval if interval else self.FIND_ELEMENT_INTERVAL
        rty = retry if retry else self.FIND_ELEMENT_RETRY
        target, wait, err_msg, data = None, 0, "", {"strategy": selector, "selector": value}
        while wait < rty:
            wait += 1
            resp = self.post("/element", data)
            # No error
            if not resp.err:
                id = self.parse_element_id(resp.value)
                if id:
                    target = AndroidElement(id, self)
                    self.logger.info(f"{FIND_TAG} find element {data} successful. id = {target.id}")
                    break
                # Cannot parse element
                self.logger.error(
                    f"{FIND_TAG} parse element id {resp.value} failed. retry in {itv} ms.",
                )
                continue
            # Error
            err_msg = resp.err.message
            self.logger.error(
                f"{FIND_TAG} find element {data} failed: {err_msg}. retried {wait} times. retry in {itv} ms.",
            )
            time.sleep(itv / 1000 if wait < rty else 0)
        if not target:
            self.logger.error(f"{FIND_TAG} No element found: {err_msg}")
            raise AppiumAndroidException(err_msg)
        return target

    def find_elements(self, selector: str, value: str, retry: int = None, interval: int = None) -> List[AndroidElement]:
        """
        A rawer, lower-level interface for finding elements by selector and value.
        Recommend to use self.finds().

        Args:
            selector (Selector): find by CLASS_NAME, Id, ACCESSIBILITY_ID, XPATH, UIAUTOMATOR
            value (str): The keyword for element search.
            retry (int, optional): Retry times. Defaults to 5 (editable).
            interval (int, optional): Retry interval. Defaults to 1000ms (editable).

        Raises:
            AppiumAndroidException: When elements cannot be found.

        Returns:
            List[AndroidElement]: A list of the target elements..
        """
        itv = interval if interval else self.FIND_ELEMENT_INTERVAL
        rty = retry if retry else self.FIND_ELEMENT_RETRY
        targets, wait, data, err_msg = [], 0, {"strategy": selector, "selector": value}, ""
        while wait < rty:
            wait += 1
            resp = self.post("/elements", data)
            # No error
            if not resp.err:
                for element in resp.value:
                    id = self.parse_element_id(element)
                    if id:
                        targets.append(AndroidElement(id, self))
                        continue
                    # Cannot parse element
                    self.logger.error(f"{FIND_TAG} parse element id {element} failed.")
                    continue
                break
            # Error
            err_msg = resp.err.message
            self.logger.error(
                f"{FIND_TAG} find elements {data} failed: {err_msg}. retried {wait} times. retry in {itv} ms."
            )
            if wait < rty:
                time.sleep(itv / 1000)
        if targets:
            self.logger.info(
                f"{FIND_TAG} find {len(targets)} elements {data} successful. ids = {[target.id for target in targets]}"
            )
        else:
            self.logger.error(f"{FIND_TAG} No elements found.")
            raise AppiumAndroidException(err_msg)
        return targets

    def tap(self, x: float, y: float) -> bool:
        """
        Send a simple tap.

        Args:
            x (float): Coordinate in x direction (by pixel).
            y (float): Coordinate in y direction (by pixel).
        """
        data = {"x": x, "y": y}
        resp = self.post("/appium/tap", data)
        self._handle_post(resp, body=data)
        return True

    def long_press(self, x: float, y: float, duration_ms: float) -> bool:
        """
        Send a long press

        Args:
            x (float): Coordinate in x direction (by pixel).
            y (float): Coordinate in y direction (by pixel).
            duration_ms (float): Long press time.
        """
        touch_event_params = {"x": x, "y": y, "duration": duration_ms}
        data = {"params": touch_event_params}
        resp = self.post("/touch/longclick", data)
        self._handle_post(resp, body=data)
        return True

    def swipe(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        duration_ms: Union[int, float],
    ) -> bool:
        """
        Send a swipe from point to point.

        Args:
            start (Tuple[float, float]): Start point with x and y coordinate.
            end (Tuple[float, float]): End point with x and y coordinate.
            duration_ms (Union[int, float]): Swipe duration.
        """
        steps = int(duration_ms / 5) if duration_ms else 100
        data = {"startX": start[0], "startY": start[1], "endX": end[0], "endY": end[1], "steps": steps}
        resp = self.post("/touch/perform", data)
        self._handle_post(resp, body=data)
        return True

    def set_orientation(self, value: str) -> bool:
        """
        Set screen orientation

        Args:
            value (str): "LANDSCAPE" or "PORTRAIT"

        Raises:
            ValueError: Value not supported.
        """
        if value.upper() not in ALL_ORIENTATION:
            raise ValueError(f"set orientation only support {', '.join(ALL_ORIENTATION)}")
        data = {"orientation": value}
        resp = self.post("/orientation", data)
        self._handle_post(resp, body=data)
        return True

    def set_rotation(self, value: int) -> bool:
        """
        Set screent rotation

        Args:
            value (int): 0, 90, 180, 270

        Raises:
            ValueError: Value not supported.
        """
        if value not in ALL_ROTATION:
            raise ValueError(f"set rotation only support {', '.join(ALL_ROTATION)}")
        data = {"z": value}
        resp = self.post("/rotation", data)
        self._handle_post(resp, body=data)
        return True

    def press_back(self) -> bool:
        """
        Send the 'back' command.
        """
        resp = self.post("/back")
        self._handle_post(resp, log_body=False)
        return True

    def open_notification(self) -> bool:
        """
        Open notification.
        """
        resp = self.post("/appium/device/open_notifications")
        self._handle_post(resp, log_body=False)
        return True

    def _send_keycode(self, api: str, keycode: int, meta_state: int = None, flags: int = None) -> bool:
        data = {"keycode": keycode}
        if meta_state:
            data["metastate"] = meta_state
        if flags:
            data["flags"] = flags
        resp = self.post(api, data)
        self._handle_post(resp, body=data, stack_depth=2)
        return True

    def press_key(self, keycode: int, meta_state: int = None, flags: int = None) -> bool:
        """
        Send keycode to server's focus.
        See: https://github.com/appium/appium-uiautomator2-driver/tree/master#arguments-38

        Args:
            keycode (int): A valid Android key code.
            meta_state (int, optional): An integer where each bit set to 1 represents a pressed meta key. Defaults to None.
            flags (int, optional): Flags for the particular key event.. Defaults to None.
        """
        return self._send_keycode("/appium/device/press_keycode", keycode, meta_state, flags)

    def long_press_key(self, keycode: int, meta_state: int = None, flags: int = None) -> bool:
        """
        Send keycode to server's focus with a long press.
        See: https://github.com/appium/appium-uiautomator2-driver/tree/master#arguments-38

        Args:
            keycode (int): A valid Android key code.
            meta_state (int, optional): An integer where each bit set to 1 represents a pressed meta key. Defaults to None.
            flags (int, optional): Flags for the particular key event.. Defaults to None.
        """
        return self._send_keycode("/appium/device/long_press_keycode", keycode, meta_state, flags)

    def _alert(self, button_label, type, timeout: float = None, nonstop: bool = False) -> bool:
        data, resp = {"buttonLabel": button_label}, BaseResp("")
        if not timeout:
            resp = self.post(f"/alert/{type}", data)
            self._handle_post(resp, body=data, stack_depth=2)
            return True
        else:
            deadline, is_done = time.time() + timeout, False
            while time.time() < deadline:
                try:
                    resp = self.post(f"/alert/{type}", data)
                    self._handle_post(resp, body=data, stack_depth=2)
                    is_done = True
                    if not nonstop:
                        return True
                except AppiumAndroidException:
                    pass
                time.sleep(1)
        if is_done:
            return True
        self.raise_err_with_traceback(resp)

    def accept_alert(self, button_label: str = None, timeout: float = None, nonstop: bool = False) -> bool:
        """
        Accept pop-up alert windows.

        Args:
            button_label (str, optional): The lable on the button for acceptance. Defaults to None.
            timeout (float, optional): The time to wait. Defaults to None.
            nonstop (bool, optional): True for keep accepting alerts before timeout. Defaults to False.
        """
        return self._alert(button_label, "accept", timeout, nonstop)

    def dismiss_alert(self, button_label: str = None, timeout: float = None, nonstop: bool = False) -> bool:
        """
        Dismiss pop-up alert windows.

        Args:
            button_label (str, optional): The lable on the button for dismission. Defaults to None.
            timeout (float, optional): The time to wait. Defaults to None.
            nonstop (bool, optional): True for keep dismissing alerts before timeout. Defaults to False.
        """
        return self._alert(button_label, "dismiss", timeout, nonstop)

    def touch_down(self, x: float, y: float, duration: float = 1000) -> bool:
        """
        Send a touch down event.

        Args:
            x (float): Coordinate in x direction.
            y (float): Coordinate in y direction.
            duration (float, optional): Duration for the event to complete. Defaults to 1000ms.
        """
        touch_event_params = {"x": x, "y": y, "duration": duration}
        data = {"params": touch_event_params}
        resp = self.post("/touch/down", data)
        self._handle_post(resp, body=data)
        return True

    def touch_up(self, x: float, y: float, duration: float = 1000) -> bool:
        """
        Send a touch up event. (Requires a down event first)

        Args:
            x (float): Coordinate in x direction.
            y (float): Coordinate in y direction.
            duration (float, optional): Duration for the event to complete. Defaults to 1000ms.
        """
        touch_event_params = {"x": x, "y": y, "duration": duration}
        data = {"params": touch_event_params}
        resp = self.post("/touch/up", data)
        self._handle_post(resp, body=data)
        return True

    def touch_move(self, x: float, y: float, duration: float = 1000) -> bool:
        """
        Move the current touch event. (Requires a down event first)

        Args:
            x (float): Coordinate in x direction.
            y (float): Coordinate in y direction.
            duration (float, optional): Duration for the event to complete. Defaults to 1000ms.
        """
        touch_event_params = {"x": x, "y": y, "duration": duration}
        data = {"params": touch_event_params}
        resp = self.post("/touch/move", data)
        self._handle_post(resp, body=data)
        return True

    def w3c_actions(self, action: Union[str, List[str]]) -> bool:
        """
        Perform W3C actions
        See: https://w3c.github.io/webdriver/#actions

        Args:
            action (Union[str, List[str]]): Actions to be excuted.

        Raises:
            ValueError: Action is not a string or list of string.
        """
        if isinstance(action, str):
            action_list = [action]
        elif isinstance(action, list):
            action_list = action
        else:
            raise ValueError("action must be string or a list of strings")
        data = {"actions": action_list}
        resp = self.post("/actions", data)
        self._handle_post(resp, body=data)
        return True

    def send_keys_to_focus(self, text: str, replace: bool = False) -> bool:
        """
        Send keys to server's focus element.

        Args:
            text (str): String to be send.
            replace (bool, optional): True for replace contents in the focus. Defaults to False.
        """
        data = {"text": text, "replace": replace}
        resp = self.post("/keys", data)
        self._handle_post(resp, body=data)
        return True

    def drag(
        self,
        start_element: AndroidElement = None,
        dest_element: AndroidElement = None,
        start: Tuple[float, float] = None,
        end: Tuple[float, float] = None,
        duration_ms: Union[int, float] = None,
    ) -> bool:
        """
        Perform a drag action.

        Args:
            start_element (AndroidElement): The element to start drag.
            dest_element (AndroidElement): The element to end drag.
            start (Tuple[float, float]): The start point.
            end (Tuple[float, float]): The end point.
            duration_ms (Union[int, float], optional):
        """
        steps = int(duration_ms / 5) if duration_ms else 100
        data = {
            "elementId": start_element.id,
            "destElId": dest_element.id,
            "startX": start[0],
            "startY": start[1],
            "endX": end[0],
            "endY": end[1],
            "steps": steps,
        }
        resp = self.post("/touch/drag", data)
        self._handle_post(resp, body=data)
        return True

    def _flick(self, speed: int, element: AndroidElement, xoffset: int, yoffset: int, xspeed: int, yspeed: int) -> bool:
        data = {
            "speed": speed,
            "xoffset": xoffset,
            "yoffset": yoffset,
            "xspeed": xspeed,
            "yspeed": yspeed,
        }
        if isinstance(element, AndroidElement):
            data["element"] = element.id
        resp = self.post("/touch/flick", data)
        self._handle_post(resp, body=data, stack_depth=2)
        return True

    def flick_by_offset(self, speed: int, element: AndroidElement, xoffset: int = 0, yoffset: int = 0) -> bool:
        """
        Perform flick near an element.

        Args:
            speed (int): Flick speed.
            element (AndroidElement): An element to locate.
            xoffset (int, optional): offset to the element in x direction. Defaults to 0.
            yoffset (int, optional): offset to the element in y direction. Defaults to 0.

        Raises:
            ValueError: element is None.
        """
        if not element:
            raise ValueError("flick element cannot be a Nonetype")
        return self._flick(speed, element, xoffset, yoffset, 0, 0)

    def flick_by_xyspeed(self, speed: int, xspeed: int, yspeed: int) -> bool:
        """
        Perform flick by xyspeed

        Args:
            speed (int): An element to locate.
            xspeed (int): Speed in x direction.
            yspeed (int): Speed in y direction.
        """
        return self._flick(speed, None, 0, 0, xspeed, yspeed)

    def scroll_to(
        self,
        max_swipes: int,
        dest: Optional[AndroidElement] = None,
        strategy: Optional[Selector] = None,
        selector: Optional[str] = None,
    ) -> bool:
        """
        Scroll an scrollable element identified by strategy and selector.
        See: https://github.com/appium/appium-uiautomator2-driver/tree/master#mobile-scroll

        Args:
            max_swipes (int): The maximum number of swipes to perform
                on the target scrollable view in order to reach the destination element.
            dest (Optional[AndroidElement], optional): The identifier of the scrollable element.
                It is required this element is a valid scrollable container.
                If this is not provided then the first available scrollable view will be selected.
                Defaults to None.
            strategy (Optional[Selector], optional): The following strategies are supported:
                accessibility id (UiSelector().description),
                class name (UiSelector().className),
                -android uiautomator (UiSelector).
                Defaults to None.
            selector (Optional[str], optional): The corresponding lookup value for selected strategy.
                Defaults to None.

        Raises:
            ValueError: _description_
        """
        if not (dest or strategy):
            raise ValueError("scroll to should provide at least one of element and stratagy")
        if dest:
            return dest.scroll_to(max_swipes)
        if not strategy:
            strategy = Selector.ACCESSIBILITY_ID
        params = {"strategy": strategy, "selector": selector, "maxSwipes": max_swipes}
        origin = {"element": self.id}
        data = {"params": params, "origin": origin}
        resp = self.post("/touch/scroll", data)
        self._handle_post(resp, body=data)
        return True

    def set_appium_settings(self, settings: dict) -> bool:
        """
        Set appium settings.

        Args:
            settings (dict): A dict contains all settings to be send. Same as launch compability.
        """
        data = {"settings": settings}
        resp = self.post("/appium/settings", data)
        self._handle_post(resp, body=data)
        return True

    def network_connection(self, type: int) -> bool:
        """
        Set network connection.

        Args:
            type (int): Represents different types.
                * 0: NONE
                * 1: AIRPLANE
                * 2: WIFI
                * 4: DATA
                * 6: ALL
                * default: IN_VALID
        """
        data = {"type": type}
        resp = self.post("/network_connection", data)
        self._handle_post(resp, body=data)
        return True

    def get_clipboard(self, type: str = "PLAINTEXT") -> str:
        """
        Get device clipboard

        Args:
            type (str, optional): Defaults to "PLAINTEXT".

        Returns:
            str: The contents from the clipboard.
        """
        data = {"contentType": type.upper()}
        resp = self.post("/appium/device/get_clipboard", data)
        self._handle_post(resp)
        return resp.value

    def set_clipboard(self, content: str, type: str = "PLAINTEXT") -> bool:
        """
        Set device clipboard

        Args:
            content (str): Content string.
            type (str, optional): Defaults to "PLAINTEXT".
        """
        _encode: bool = False  # Unused args
        if _encode:
            data = {"content": b64encode(content.encode()).decode(), "contentType": type.upper()}
        else:
            data = {"content": content, "contentType": type.upper()}
        resp = self.post("/appium/device/set_clipboard", data)
        self._handle_post(resp, body=data)
        return True

    def multi_pointer_gesture(self, gestures: Union[Gesture, List[Gesture]]) -> bool:
        """
        Perform multi point gesture.

        Args:
            gestures (Union[Gesture, List[Gesture]]): A single Gesture or a list of Gesture.
                A list of Gestures represents multi touch, each Gesture for a independent pointer.
                Gesture represents a series of touch movements.
                Gesture type:
                    List[BaseGesture]
                BaseGesture type:
                    x: float
                    y: float
                    time: float
        """
        if isinstance(gestures, Gesture):
            gestures = [gestures]
        elif isinstance(gestures, list) and all(isinstance(i, Gesture) for i in gestures):
            pass
        else:
            raise ValueError(
                f"gestures must be a Gesture class or a list of Gestures. Now is {gestures.__class__.__name__}"
            )

        data = {"actions": [x.to_json() for x in gestures]}
        resp = self.post("/touch/multi/perform", data)
        self._handle_post(resp, body=data)
        return True

    def schedule_action(
        self,
        steps: List[ScheduledStep],
        name: str,
        times: int = None,
        interval_ms: int = None,
        max_history_items: int = None,
        max_pass: int = None,
        max_fail: int = None,
    ) -> bool:
        """
        Schedule actions. See:
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/scheduled-actions.md

        Args:
            steps (List[ScheduledStep]): Actions. The formats are sealed into a dataclass:
                ScheduledStep:
                    "steps": list
                        dicts:
                            "type": str
                            "name": str
                            "payload": dict{}[str, Any]
            name (str): The unique name of the action.
            times (int, optional): How many times the action must be executed itself. Defaults to None.
            interval_ms (int, optional):
                How long the interval in milliseconds between the next action reschedule should be.
                Defaults to None.
            max_history_items (int, optional): See documents. Defaults to None.
            max_pass (int, optional): See documents. Defaults to None.
            max_fail (int, optional): See documents. Defaults to None.
        """
        data = {"name": name, "steps": [x.to_json() for x in steps]}
        if times:
            data["times"] = times
        if interval_ms:
            data["intervalMs"] = interval_ms
        if max_history_items:
            data["maxHistoryItems"] = max_history_items
        if max_pass:
            data["maxPass"] = max_pass
        if max_fail:
            data["maxFail"] = max_fail
        resp = self.post("/appium/schedule_action", data)
        self._handle_post(resp, body=data)
        return True

    def unschedule_action(self, name: str) -> bool:
        data = {"name": name}
        resp = self.post("/appium/unschedule_action", data)
        self._handle_post(resp, body=data)
        return True

    def action_history(self, name: str) -> list:
        data = {"name": name}
        resp = self.post("/appium/action_history", data)
        self._handle_post(resp, body=data)
        return resp.value

    """ ===========================================================================
        NOTE: appium.uiautomator2.handler API HERE
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md
        ===========================================================================
    """

    def appium_drag(
        self, element: AndroidElement, start_point: Tuple[float, float], end_point: Tuple[float, float], speed: int
    ) -> bool:
        """
        Drag with Appium interface.

        Args:
            element (AndroidElement)
            start_point (Tuple[float, float])
            end_point (Tuple[float, float])
            speed (int)
        """
        data = {
            "origin": {"element": element.id},
            "speed": speed,
            "start": {"x": start_point[0], "y": start_point[1]},
            "end": {"x": end_point[0], "y": end_point[1]},
        }
        resp = self.post("/appium/gestures/drag", data)
        self._handle_post(resp, body=data)
        return True

    def appium_fling(
        self,
        element: AndroidElement,
        left_top_width_height: Tuple[float, float, float, float],
        direction: str,
        speed: int,
    ) -> bool:
        """
        Fling with Appium interface.

        Args:
            element (AndroidElement):
            left_top_width_height (Tuple[float, float, float, float])
            direction (str)
            speed (int)

        Raises:
            ValueError: direction not supported.

        Alias:
            self.fling()
        """
        if direction.upper() not in ALL_FLING:
            raise ValueError(f"appium fling direction only support {', '.join(ALL_FLING)}")
        l, t, w, h = left_top_width_height
        data = {
            "origin": {"element": element.id if element else None},
            "speed": speed,
            "direction": direction,
            "area": {"top": t, "left": l, "width": w, "height": h},
        }
        resp = self.post("/appium/gestures/fling", data)
        self._handle_post(resp, body=data)
        return True

    def _appium_click_model(
        self,
        api: str,
        element: AndroidElement,
        locator: AppiumLocator,
        offset: Tuple[float, float],
        duration: float = None,
    ) -> bool:
        data = {}
        if isinstance(element, AndroidElement):
            data["origin"] = element.id
        if locator:
            data["locator"] = {"strategy": locator.strategy, "selector": locator.selector, "context": locator.context}
        if offset:
            data["offset"] = {"x": offset[0], "y": offset[1]}
        if not data:
            raise ValueError("At least one param should be passed to appium cliker")

        if duration:
            data["duration"] = duration
        resp = self.post(f"/appium/gestures/{api}", data)
        self._handle_post(resp, body=data, stack_depth=2)
        return True

    def appium_click(
        self,
        element: Optional[AndroidElement] = None,
        locator: Optional[AppiumLocator] = None,
        offset: Optional[Tuple[float, float]] = None,
    ) -> bool:
        """
        Click with Appium interface.

        Args:
            element (Optional[AndroidElement], optional): Defaults to None.
            locator (Optional[Locator], optional): Defaults to None.
            offset (Optional[Tuple[float, float]], optional): Defaults to None.
        """
        return self._appium_click_model("click", element, locator, offset)

    def appium_long_click(
        self,
        element: Optional[AndroidElement] = None,
        locator: Optional[AppiumLocator] = None,
        offset: Optional[Tuple[float, float]] = None,
        duration: float = 1.0,
    ) -> bool:
        """
        Long click with Appium interface.

        Args:
            element (Optional[AndroidElement], optional): Defaults to None.
            locator (Optional[Locator], optional): Defaults to None.
            offset (Optional[Tuple[float, float]], optional): Defaults to None.
            duration (float, optional): Defaults to 1.0.

        Alias:
            self.long_click()
        """
        return self._appium_click_model("long_click", element, locator, offset, duration)

    def appium_double_click(
        self,
        element: Optional[AndroidElement] = None,
        locator: Optional[AppiumLocator] = None,
        offset: Optional[Tuple[float, float]] = None,
    ) -> bool:
        """
        Double click with Appium interface.

        Args:
            element (Optional[AndroidElement], optional): Defaults to None.
            locator (Optional[Locator], optional): Defaults to None.
            offset (Optional[Tuple[float, float]], optional): Defaults to None.

        Alias:
            self.double_click()
        """
        return self._appium_click_model("double_click", element, locator, offset)

    def _appium_ltwh_model(
        self,
        api: str,
        element: AndroidElement,
        left_top_width_height: Optional[Union[Tuple[float, float, float, float], Rect]],
        percent: float,
        speed: int,
        direction: str = None,
    ) -> bool:
        if not element and not left_top_width_height:
            raise ValueError("element or area not provided")
        data = {
            "origin": {"element": element.id if element else None},
            "speed": speed,
            "percent": percent,
        }
        if left_top_width_height:
            if isinstance(left_top_width_height, tuple):
                l, t, w, h = left_top_width_height
            elif isinstance(left_top_width_height, Rect):
                tmp = left_top_width_height
                l, t, w, h = tmp.x, tmp.y, tmp.width, tmp.height
            data["area"] = {"top": t, "left": l, "width": w, "height": h}
        if direction:
            data["direction"] = direction
        resp = self.post(f"/appium/gestures/{api}", data)
        self._handle_post(resp, body=data, stack_depth=2)
        return True

    def appium_pinch_in(
        self,
        percent: float,
        element: AndroidElement = None,
        area: Union[Tuple[float, float, float, float], Rect] = None,
        speed: int = None,
    ) -> bool:
        """
        Pinch in (closing) with the Appium interface.

        Args:
            percent (float): Pinch distance relative to element or area size. 0.5 = 50%, for example.
            element (AndroidElement, optional): The target element. Defaults to None.
            area (Union[Tuple[float, float, float, float], Rect], optional) The target area. Defaults to None.
                The tuple members represent left, top, width, height.
            speed (int, optional): Action excuting speed. Defaults to None.

        Raises:
            ValueError: When both 'element' and 'area' are not provided.

        Alias:
            self.pinch_in()
        """
        return self._appium_ltwh_model("pinch_close", element, area, percent, speed)

    def appium_pinch_out(
        self,
        percent: float,
        element: AndroidElement = None,
        area: Union[Tuple[float, float, float, float], Rect] = None,
        speed: int = None,
    ) -> bool:
        """
        Pinch out (opening) with the Appium interface.

        Args:
            percent (float): Pinch distance relative to element or area size. 0.5 = 50%, for example.
            element (AndroidElement, optional): The target element. Defaults to None.
            area (Union[Tuple[float, float, float, float], Rect], optional) The target area. Defaults to None.
                The tuple members represent left, top, width, height.
            speed (int, optional): Action excuting speed. Defaults to None.

        Raises:
            ValueError: When both 'element' and 'area' are not provided.

        Alias:
            self.pinch_out()
        """
        return self._appium_ltwh_model("pinch_open", element, area, percent, speed)

    def appium_scroll(
        self,
        percent: float,
        direction: str,
        element: AndroidElement = None,
        area: Union[Tuple[float, float, float, float], Rect] = None,
        speed: int = None,
    ) -> bool:
        """
        Scroll with the Appium interface.

        Args:
            percent (float): Pinch distance relative to element or area size. 0.5 = 50%, for example.
            direction (str): Supports 'up', 'down', 'left' and 'right'.
            element (AndroidElement, optional): The target element. Defaults to None.
            area (Union[Tuple[float, float, float, float], Rect], optional) The target area. Defaults to None.
                The tuple members represent left, top, width, height.
            speed (int, optional): Action excuting speed. Defaults to None.
        Raises:
            ValueError: When both 'element' and 'area' are not provided.
        """
        return self._appium_ltwh_model("scroll", element, area, percent, speed, direction)

    def appium_swipe(
        self,
        percent: float,
        direction: str,
        element: AndroidElement = None,
        area: Union[Tuple[float, float, float, float], Rect] = None,
        speed: int = None,
    ) -> bool:
        """
        Swipe with the Appium interface.

        Args:
            percent (float): Pinch distance relative to element or area size. 0.5 = 50%, for example.
            direction (str): Supports 'up', 'down', 'left' and 'right'.
            element (AndroidElement, optional): The target element. Defaults to None.
            area (Union[Tuple[float, float, float, float], Rect], optional) The target area. Defaults to None.
                The tuple members represent left, top, width, height.
            speed (int, optional): Action excuting speed. Defaults to None.
        Raises:
            ValueError: When both 'element' and 'area' are not provided.
        """
        return self._appium_ltwh_model("swipe", element, area, percent, speed, direction)

    """ ===========================================================================
        NOTE: GET API HERE
        ===========================================================================
    """

    def status(self) -> Tuple[bool, str]:
        """
        Get server status.

        Returns:
            Tuple[bool, str]: is ready, status message.
        """
        resp = self.get_without_session("/status")
        self._handle_get(resp)
        return (resp.value["ready"], resp.value["message"])

    def packages(self, with_session_id: bool = True):
        """
        Get device packages.

        Args:
            with_session_id (bool, optional): Send request with/without session ID. Defaults to True.

        Returns:
            str
        """
        if with_session_id:
            resp = self.get("/appium/device/apps")
        else:
            resp = self.get_without_session("/appium/device/apps")
        self._handle_get(resp, log_body=False)
        return resp.value

    def sessions(self):
        """
        Get running sessions

        Returns:
            str
        """
        resp = self.get_without_session("/sessions")
        self._handle_get(resp)
        return resp.value

    def session_details(self) -> dict:
        """
        Get current session details.

        Returns:
            dict
        """
        resp = self.get("")
        self._handle_get(resp)
        return resp.value

    def orientation(self) -> str:
        """
        Get device orientation

        Returns:
            str
        """
        resp = self.get("/orientation")
        self._handle_get(resp)
        return resp.value

    def rotation(self) -> Tuple[float, float, float]:
        """
        Get device rotation

        Returns:
            str
        """
        resp = self.get("/rotation")
        self._handle_get(resp)
        return float(resp.value["x"]), float(resp.value["y"]), float(resp.value["z"])

    def active_element(self) -> dict:
        """
        Get the current active element (focus).

        Returns:
            dict: A dict of element id.
                For example:
                {'ELEMENT': '00000000-0000-017b-ffff-ffff00000011', ...}
                Use self.parse_element_id() to handle the dict
        """
        resp = self.get("/element/active")
        self._handle_get(resp)
        return resp.value

    def system_bars(self) -> dict:
        """
        Get system status bar.

        Returns:
            dict: Example: {'statusBar': 66}
        """
        resp = self.get("/appium/device/system_bars")
        self._handle_get(resp)
        return resp.value

    def battery_info(self) -> dict:
        """
        Get battery info.

        Returns:
            dict
        """
        resp = self.get("/appium/device/battery_info")
        self._handle_get(resp)
        return resp.value

    def get_appium_settings(self) -> dict:
        """
        Get Appium settings.

        Returns:
            dict
        """
        resp = self.get("/appium/settings")
        self._handle_get(resp)
        return resp.value

    def pixel_ratio(self) -> float:
        """
        Get pixel ratio.

        Returns:
            float
        """
        resp = self.get("/appium/device/pixel_ratio")
        self._handle_get(resp)
        return float(resp.value)

    def alert_text(self) -> str:
        """
        Get alert text.

        Returns:
            str
        """
        resp = self.get("/alert/text")
        self._handle_get(resp)
        return resp.value

    def device_info(self) -> dict:
        """
        Get device info.

        Returns:
            dict
        """
        resp = self.get("/appium/device/info")
        self._handle_get(resp)
        return resp.value

    def display_density(self) -> int:
        """
        Get display density

        Returns:
            int
        """
        resp = self.get("/appium/device/display_density")
        self._handle_get(resp)
        return int(resp.value)

    def screenshot(self, save_path: Optional[str]) -> bytes:
        """
        Get screenshot and save to path.

        Args:
            save_path (Optional[str]): Image save path. Defaults to None for no saving.

        Returns:
            bytes: Raw, decoded bytes data.
        """
        resp = self.get("/screenshot", timeout=60000)
        self._handle_get(resp, log_body=False)
        if save_path:
            with open(save_path, "wb") as img:
                img.write(b64decode(resp.value))
                self.logger.info(f"screenshot saved to path {save_path}")
        return b64decode(resp.value)

    def window_size(self) -> WindowSize:
        """
        Get window size

        Returns:
            WindowSize
        """
        if self.size is None:
            resp = self.get("/window/:windowHandle/size")
            self._handle_get(resp)
            self.size = WindowSize(width=resp.value["width"], height=resp.value["height"])
        return self.size

    def page_source(self) -> str:
        """
        Dump the xml tree of the page source.

        Returns:
            str: Page source string (warning: could be extremely long)
        """
        resp = self.get("/source")
        self._handle_get(resp, log_body=False)
        return resp.value

    def package_bounds(self, pkg_name: str, class_name: str = None) -> List[Rect]:
        """
        Get actual frame bounds for a certain running package.

        Args:
            pkg_name (str)
            class_name (str, optional): Element 'class' property. Defaults to None.
                Example: android.widget.FrameLayout, android.widget.LinearLayout

        Returns:
            List[Rect]
        """

        def recur(node: ET.Element) -> List[ET.Element]:
            """
            Find the top node that meets the give args
            """
            # If node meets the condition return an one-item list
            if "package" in node.attrib and "class" in node.attrib:
                if not class_name:
                    if pkg_name in node.attrib["package"]:
                        return [node]
                else:
                    if pkg_name in node.attrib["package"] and class_name in node.attrib["class"]:
                        return [node]
            # Else recur to search child nodes
            found = []
            for child in node:
                found += recur(child)
            return found

        pattern = "\\[([0-9]*),([0-9]*)\\]\\[([0-9]*),([0-9]*)\\]"
        root = ET.fromstring(self.page_source())
        """
        Deprecated: the class name is probabaly not a fixed class type
        if class_name:
            cls_prop = f"[@class='{class_name}']"
        for e in root.findall(f"*[@package='{pkg_name}']{cls_prop if class_name else ''}"):
            bounds: str = e.get("bounds")
            vals = re.search(pattern, bounds).groups()
            ret.append(vals)
        """
        ret: List[Rect] = []
        window = self.window_size()
        for e in recur(root):
            bounds: str = e.get("bounds")
            vals = tuple([int(x) for x in re.search(pattern, bounds).groups()])
            w, h = vals[2] - vals[0], vals[3] - vals[1]
            if w < window.width * 0.8 or h < window.height * 0.8:
                continue
            # ret.append((vals[:2], vals[2:]))
            ret.append(Rect(vals[0], vals[1], vals[2], vals[3]))
        if not ret:
            cls_prop = f"[@class='{class_name}']"
            xpath = f"*[@package='{pkg_name}']{cls_prop if class_name else ''}"
            raise AppiumAndroidException(f"Cannot find any element meets '{xpath}'")
        # return ret
        self.logger.info(f"get package bounds: {ret}. return the top node.")
        return ret

    def package_displayID(self, pkg_name: str) -> int:
        """
        Get display id through package name.

        Args:
            pkg_name (str)

        Returns:
            int
        """
        resp = self.get_without_session(f"/appium/{pkg_name}/display_id")
        self._handle_get(resp, info=f"display id of package {pkg_name}")
        return int(resp.value)

    def displayIDs(self) -> List[int]:
        """
        Get all available display ids

        Returns:
            List[int]
        """
        resp = self.get_without_session("/appium/device/display_ids")
        self._handle_get(resp)
        return resp.value

    def display_window_info(self, display_id: int) -> Tuple[Rect, str, Tuple[float, float]]:
        """
        Use the interface to get:
        1. Current window position
        2. Current package name
        3. Current screen resolution

        Args:
            display_id (int): The display ID represents where the the message you want to get from

        Returns:
            Tuple[Rect, str, Tuple[float, float]]: bound rect, package name, and a tuple of width and height
        """
        resp = self.get_without_session(f"/appium/display/{display_id}/focused_window")
        self._handle_get(resp)
        b, p, h, w = (
            resp.value["bounds"],
            resp.value["packageName"],
            resp.value["screen_height"],
            resp.value["screen_width"],
        )
        return Rect(x=b["x"], y=b["y"], width=b["width"], height=b["height"]), p, (float(w), float(h))

    """ ===========================================================================
        NOTE: ALIASES HERE
        ===========================================================================
    """

    fling = appium_fling
    long_click = appium_long_click
    double_click = appium_double_click
    pinch_in = appium_pinch_in
    pinch_out = appium_pinch_out
