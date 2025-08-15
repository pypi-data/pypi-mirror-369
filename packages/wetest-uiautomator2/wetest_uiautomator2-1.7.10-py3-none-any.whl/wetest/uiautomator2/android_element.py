# !/usr/bin/python3
# coding: utf-8

from __future__ import annotations

import base64
import json

from typing import Callable, Tuple

from .core._utils import Expectation
from .core._types import BaseElement, BaseClient, Rect, Selector


class AndroidElement(BaseElement):
    def __init__(self, id: str, client: BaseClient):
        """
        Generate an AndroidElement.

        Args:
            id (str): Element id.
            client (AndroidDriver): A weakref to AndroidDriver for request.
        """
        super().__init__(id, client)

    def expect(
        self,
        msg: str = None,
        err: Exception = None,
        show_log: bool = True,
        handler: Callable = None,
        *args,
        **kwargs,
    ) -> AndroidElement:
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
            AndroidElement <- Expectation: a wrapped Self.
        """
        return Expectation(self, msg, err, self.logger, show_log, handler, *args, **kwargs)

    @property
    def text(self) -> str:
        """
        The text of the element.

        Returns:
            str: Text.
        """
        return self.get_text()

    @property
    def location(self) -> Tuple[int, int]:
        """
        The location of the element.

        Returns:
            Tuple[int, int]: (x, y)
        """
        return self.get_location()

    @property
    def size(self) -> Tuple[int, int]:
        """
        The size of the element.

        Returns:
            Tuple[int, int]: (height, width)
        """
        return self.get_size()

    @property
    def rect(self) -> Rect:
        """
        The bounds of the element.

        Returns:
            Rect
        """
        return self.get_rect()

    @property
    def name(self) -> str:
        """
        The name of the element.

        Returns:
            str
        """
        return self.get_name()

    def get_unique_identifiers(self) -> str:
        return self.id

    def _log_suffix(self) -> str:
        return f"(element {self.id})"

    def click(self):
        """
        Click the element.
        """
        resp = self._client.post(f"/element/{self.id}/click")
        self._client._handle_post(resp, suffix=self._log_suffix(), log_body=False)

    def send_keys(self, text: str, replace: bool = False):
        """
        Send keys to the element.

        Args:
            text (str)
            replace (bool, optional): True for replace contents in the element. Defaults to False.
        """
        data = {"text": text, "replace": replace}
        resp = self._client.post(f"/element/{self.id}/value", data)
        self._client._handle_post(resp, suffix=self._log_suffix(), body=data)

    def clear(self):
        """
        Clear the element.
        """
        resp = self._client.post(f"/element/{self.id}/clear")
        self._client._handle_post(resp, suffix=self._log_suffix(), log_body=False)

    def get_text(self) -> str:
        """
        Get text of the element.

        Returns:
            str: Text.
        """
        resp = self._client.get(f"/element/{self.id}/text")
        self._client._handle_get(resp, suffix=self._log_suffix())
        return resp.value

    def get_location(self) -> Tuple[int, int]:
        """
        Get the location of the element.

        Returns:
            Tuple[int, int]: (x, y)
        """
        resp = self._client.get(f"/element/{self.id}/location")
        self._client._handle_get(resp, suffix=self._log_suffix())
        return resp.value["x"], resp.value["y"]

    def get_size(self) -> Tuple[int, int]:
        """
        Get the size of the element.

        Returns:
            Tuple[int, int]: (height, width)
        """
        resp = self._client.get(f"/element/{self.id}/size")
        self._client._handle_get(resp, suffix=self._log_suffix())
        return resp.value["height"], resp.value["width"]

    def get_attribute(self, name: str) -> str:
        """
        Get attributes of the element.

        Args:
            name (str): Attribute name.

        Returns:
            str
        """
        resp = self._client.get(f"/element/{self.id}/attribute/{name}")
        self._client._handle_get(resp, suffix=self._log_suffix())
        return resp.value

    def get_rect(self) -> Rect:
        """
        Get the bounds of the element.

        Returns:
            Rect
        """
        resp = self._client.get(f"/element/{self.id}/rect")
        rect = resp.value if isinstance(resp.value, dict) else json.loads(resp.value)
        element_rect = Rect(**rect)
        self._client._handle_get(resp, suffix=self._log_suffix(), body=element_rect)
        return element_rect

    def get_name(self) -> str:
        """
        Get the name of the element.

        Returns:
            str
        """
        resp = self._client.get(f"/element/{self.id}/name")
        self._client._handle_get(resp, suffix=self._log_suffix())
        return resp.value

    def screenshot(self, save_path: str = None) -> bytes:
        """
        Get screenshot of the element and save to path.

        Args:
            save_path (Optional[str]): Image save path. Defaults to None for no saving.

        Returns:
            bytes: Raw, decoded bytes data.
        """
        resp = self._client.get(f"/element/{self.id}/screenshot", timeout=60000)
        self._client._handle_get(resp, suffix=self._log_suffix(), log_body=False)
        if save_path:
            with open(save_path, "wb") as img:
                img.write(base64.b64decode(resp.value))
                self.logger.info(f"screenshot {self._log_suffix()} saved to path {save_path}")
        return base64.b64decode(resp.value)

    def scroll_to(self, max_swipes: int, strategy: Selector = Selector.ACCESSIBILITY_ID, selector: str = ""):
        """
        Scroll to the element.
        See: https://github.com/appium/appium-uiautomator2-driver/tree/master#mobile-scroll

        Args:
            max_swipes (int)
            strategy (Selector, optional): Defaults to Selector.ACCESSIBILITY_ID.
            selector (str, optional): Defaults to "".
        """
        params = {"strategy": strategy, "selector": selector, "maxSwipes": max_swipes}
        origin = {"element": self.id}
        data = {"params": params, "origin": origin}
        resp = self._client.post(f"/touch/scroll", data)
        self._client._handle_post(resp, suffix=self._log_suffix(), body=data)

    def first_visible_view(self):
        """
        Get the first visible view of the element.
        """
        resp = self._client.get(f"/appium/element/{self.id}/first_visible")
        self._client._handle_get(resp, suffix=self._log_suffix())
        return resp.value
