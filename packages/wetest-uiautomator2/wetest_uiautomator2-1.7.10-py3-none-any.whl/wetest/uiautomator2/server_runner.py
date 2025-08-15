# !/usr/bin/python3
# coding: utf-8

from __future__ import annotations

import re
import os
import time
import subprocess
import platform

from typing import Union, Callable, List, Dict
from collections import namedtuple
from adbutils import AdbDevice, Network, AdbError

from .core._const import *
from .core._logger import Logger
from .core._utils import Expectation, execute
from . import utils

logger = Logger("wetest-server-runner")


class ServerRunner:
    def __init__(
        self,
        device: AdbDevice,
        push_path: str = DEFAULT_PUSH_PATH,
        pack_name: str = DEFAULT_PACK_NAME,
        timeout: float = DEFAULT_RUNNER_TIMEOUT,
        forward: int = None,
        show_console: bool = False,
        wa2: bool = None,
        auto_push: bool = None,
        auto_start: bool = None,
        auto_release: bool = None,
        server_path: str = None,
        port_for_check: int = DEFAULT_PORT,
    ) -> None:
        """
        A runner that manage Appium server automatically.
        ServerRunner is fully decoupled with AndroidDriver.

        Usage:
            with ServerRunner(adb.device(), server_path) as runner:
                driver = AndroidDriver(adb.device(), *args)
                ...

        Args:
            device (AdbDevice): The target device,
            push_path (str, optional): Remote path to push server package. Defaults to DEFAULT_PUSH_PATH.
            pack_name (str, optional): Server package name. Defaults to DEFAULT_PACK_NAME.
            timeout (float, optional): Global timeout. Defaults to DEFAULT_RUNNER_TIMEOUT.
            forward (int, optional): AdbForward port (not necessary). Defaults to None.
            show_console (bool, optional): Print device adb shell. Defaults to False.
            wa2 (bool, optional): True for cooperating with WeAutomator2. Defaults to False.
            auto_push (bool, optional): True for automatically pushing server package. Defaults to False.
                NOT RECOMMANDED to automatically pushing server especailly on the cloud.
                Run "adb push ./appium.apk /data/local/tmp/udt/uia2.jar" as a prerequisite in shell instead.
                The arg 'server_path' cannot be None if set to True.
            auto_start (bool, optional): True for automatically starting server. Defaults to True.
            auto_release (bool, optional): True for automatically terminating server. Defaults to True.
            server_path (str): Local appium server apk path. Defaults to None.
            port_for_check (int, optional): Appium server preset port. Defaults to DEFAULT_PORT (6790).
                NOT RECOMMANDED to pass.
        """
        self.d = device

        self._server_path = server_path
        self._push_path = push_path
        self._pack_name = pack_name
        self._timeout = timeout
        self._forward = forward
        self._show_console = show_console
        self._port_for_check = port_for_check

        self._background_shell: subprocess.Popen = None
        self._process_patter = ""
        self._process_keys = ""
        self._process_command = ""
        self._version = None
        self._brand = None

        self.device_version()
        self.device_brand()

        self._compability()

        self.fetch_processes(show_log=False)

        if self._forward and utils.is_unix():
            self.adb_forward(forward, forward, check=True)

        # Detect if the server is already running if none of the corresponding args are passed.
        if wa2 is None and auto_push is None and auto_start is None and auto_release is None:
            logger.info("receive none of life cycle managing args (wa2, auto_push, auto_start, auto_release).")
            wa2 = self.is_alive()
            if wa2:
                logger.info(
                    "a running server process is detected, "
                    + "thus the server life cycle management is automatically disabled."
                )
        else:
            wa2 = wa2 if wa2 is not None else False
        # If the server is already running or using WeAutomator2, give up managing server's life cycle
        if wa2:
            self._auto_push = False
            self._auto_start = False
            self._auto_release = False
        # Else, control the start and release of server by default.
        else:
            self._auto_push = auto_push if auto_push is not None else False
            self._auto_start = auto_start if auto_start is not None else True
            self._auto_release = auto_release if auto_release is not None else True
        logger.info(
            ", ".join(
                [
                    f"life cycle managing status: auto_push = {self._auto_push}",
                    f"auto_start = {self._auto_start}",
                    f"auto_release = {self._auto_release}",
                ]
            )
        )
        if self._auto_push:
            logger.warning(
                "auto push is not recommended! It is better to run 'adb push <APPIUM SERVER PATH> "
                + f"{DEFAULT_PUSH_PATH} as a prerequisite in shell instead."
            )
            if not self._server_path:
                raise ValueError("auto push failed because no 'server_path' was given.")
            self.push_file(self._server_path, self._push_path)
        if self._auto_start:
            self.start()
            time.sleep(1)
        elif not self.is_alive():
            raise ConnectionRefusedError(
                "Appium server is not running and auto_start is False, which is not allowed. "
                + "Please check the ServerRunner init args."
            )
        if not self._auto_release:
            logger.warning("appium server on device WILL NOT BE TERMINATED automatically. ")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self._auto_release:
            self.close()

    def expect(
        self,
        msg: str = None,
        err: Exception = None,
        show_log: bool = False,
        handler: Callable = None,
        *args,
        **kwargs,
    ) -> ServerRunner:
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
            ServerRunner <- Expectation: a wrapped Self.
        """
        return Expectation(self, msg, err, logger, show_log, handler, *args, **kwargs)

    def close(self):
        self.kill(self.fetch_processes())
        if self._background_shell:
            self._background_shell.terminate()
        if self._forward and utils.is_unix():
            self.adb_forward_remove(self._forward)

    @property
    def brand(self) -> str:
        return self._brand

    @property
    def version(self) -> str:
        return self._version

    @property
    def serial(self) -> str:
        return self.d.serial

    @classmethod
    def platform(cls) -> str:
        """
        Get python environment

        Returns:
            str: Platform name in upper class (WINDOWS, LINUX, MACOS...).
        """
        return platform.platform().upper()

    def release_port(self, port: int, user: str = "", pid: int = 0):
        """
        Release port usage by remove adb forward or kill processes.

        Args:
            port (int)
            user (str, optional): Defaults to "".
            pid (int, optional): Defaults to 0.
        """
        return utils.release_port(self.serial, port, user, pid)

    def adb_forward(self, local: int, remote: int, check: bool = False):
        """
        Rewrapped adb forward.

        Args:
            local (int): Local port number.
            remote (int): Remote port number.
            check (bool, optional): Check if the local port is occupied.
        """
        return utils.adb_forward(self.serial, local, remote, check)

    def adb_forward_remove(self, local: int):
        """
        Rewrapped remove adb forward.

        Args:
            local (int): Local port number to remove.
        """
        return utils.adb_forward_remove(self.serial, local)

    def push_dir(
        self,
        source: str,
        target: str,
        excludes: List[str] = None,
        filters: List[str] = None,
        regular: bool = True,
        log: bool = True,
    ):
        """
        Mirroring copy & push everything under a directory to the device.

        Args:
            source (str): The source directory.
            target (str): The target directory on the device.
            device (AdbDevice, optional): Must be provided is used as class method. Defaults to None.
            excludes (List[str], optional): Dirctory patterns to be exclued. Defaults to None.
            filters (List[str], optional): Filename patterns to be filtered. Defaults to None.
            regular (bool, optional):
                True for use regular expression on 'excludes' and 'filters'.
                False for simple string match.
                Defaults to True.
            log (bool, optional): Show more logs of the pushing process. Defaults to True.
        """
        return utils.push_dir(self.serial, source, target, excludes, filters, regular, log)

    def push_file(self, source: str, target: str):
        """
        Push anything to device.

        Args:
            apk_path (str, optional): Local resource path. Defaults to None.
            push_path (str, optional): Push path. Defaults to None.
        """
        return utils.push_file(self.serial, source, target)

    def shell(self, command: str):
        """
        Execute shell commands.

        Args:
            command (str)
        """
        return self.d.shell(command)

    def permission(self, package_name: str, permissions: Union[str, List[str]], give: bool = True) -> str:
        """
        Set permission for a package.

        Args:
            package_name (str)
            permissions (Union[str, List[str]]): Permission name in Android permission manifest.
                Example: READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
            give (bool, optional): True for grant permission. False for revoke permission. Defaults to True.

        Returns:
            str: Shell logs.
        """
        return utils.permission(self.serial, package_name, permissions, give)

    def set_permission(self, package_name: str, give: bool = True):
        """
        Set permission with presets for a package.

        Usage:
            runner.set_permission(pkg_name).readwrite()

        Args:
            package_name (str): _description_
            give (bool, optional): True for grant permission. False for revoke permission. Defaults to True.

        Returns:
            str: Shell logs.
        """
        return utils.set_permission(self.serial, package_name, give)

    def start(self, pack_name: str = None):
        """
        Defaults to start Appium server. Can start any other packages either.

        Args:
            pack_name (str, optional)

        Raises:
            RuntimeError: Raised when times out.
        """
        if not self._check_server_file_exists():
            raise FileNotFoundError(
                " ".join(
                    [
                        f"no appium server file detected on device.",
                        f"run 'adb push <APPIUM SERVER PATH> {DEFAULT_PUSH_PATH} as a prerequisite",
                        "or init ServerRunner with 'server_path' and 'auto_push'",
                    ]
                )
            )
        pack_name = pack_name if pack_name else self._pack_name
        self._background_shell = subprocess.Popen(
            f"adb -s {self.serial} shell CLASSPATH={self._push_path} app_process / {pack_name}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        logger.info(f"starting {pack_name}...")
        # log shell lines
        if self._show_console:
            for line in iter(self._background_shell.stdout.readline, "b"):
                logger.info(line)
                if SERVER_START_NOTICE in str(line):
                    break
        if self._wait_ready(timeout=self._timeout) and self.fetch_processes(pack_name=pack_name, show_log=True):
            logger.info(APPIUM_SERVER_READY)
        else:
            logger.error(APPIUM_SERVER_FAILS)
            self.close()
            raise RuntimeError("Unable to start the Appium server. Connection refused.")

    def is_alive(self, pack_name: str = None) -> bool:
        """
        Check if the appium server is alive.

        Returns:
            bool: Flag for the package process being alive.
        """
        pack_name = pack_name if pack_name else self._pack_name
        if self.fetch_processes(pack_name=pack_name):
            return True
        return False

    def device_version(self) -> int:
        """
        Get device version in Android SDK format.

        Returns:
            int: Android SDK version
        """
        self._version = int(self.d.shell("getprop ro.build.version.sdk"))
        logger.info(f"get device version: {self._version}")
        return self._version

    def device_brand(self) -> str:
        """
        Get device brand

        Returns:
            str: Brand name.
        """
        self._brand = self.d.shell("getprop ro.product.brand")
        logger.info(f"get device brand: {self._brand}")
        return self._brand

    def fetch_processes(self, show_log=False, filters: List[str] = None, pack_name: str = None) -> List[Dict[str, str]]:
        """
        Analyze activating processes from adb shell.

        Args:
            show_log (bool, optional): Log process that found. Defaults to False.
            filters (List[str], optional): Strings for filtering matches from processes found.
                Defaults to None.
            pack_name (str, optional): Target package name. Defaults to None.

        Returns:
            List[Dict[str, str]]: Found processes, each of which is a dict.
                Example: {"user": "root", "pid": "14514", ...}
        """
        # logger.info(f"searching for processes: {self._process_command}")
        pack_name = pack_name if pack_name else self._pack_name
        if filters:
            _filters = filters
        else:
            _filters = ["grep"]
        # Get shell lines by "ps -ef | grep" liked commands
        processes, lines = [], self.d.shell(f"{self._process_command} | grep {pack_name}").splitlines()
        # Use regular expression to analyze the shell lines
        for line in lines:
            vals, is_filterd = re.search(self._process_patter, line).groups(), False
            # Not to add the process into result if it is matched with one of the filters
            for filter in _filters:
                if filter in vals[-1]:
                    is_filterd = True
                    break
            if is_filterd:
                continue
            # Zip the matches and append then into result
            # {"name": "user", "pid": "14514", ...}
            process = dict(zip(self._process_keys, vals))
            processes.append(process)
            # Logging result
            if show_log:
                logger.info(f"found process: {process.get('pid', '0')} {process.get('name', 'null')}")
            else:
                logger.debug(f"found process: {process.get('pid', '0')} {process.get('name', 'null')}")
        # Save to the attribute
        self._processes = processes
        return processes

    def kill(self, processes: List[Dict[str, str]] = None) -> bool:
        """
        Kill processes from give dict/dicts.

        Args:
            processes (List[Dict[str, str]], optional): A dict or list of dicts. Defaults to None.
                Dicts should at least contains 2 keys: "name" and "pid"
                Recommand to use the list of dicts generated from self.fetch_processes()

        Returns:
            bool: Flag for sucessfully killed target processes.
        """
        if not processes:
            return False
        killed = []
        for process in processes:
            pid, name = process.get("pid", "0"), process.get("name", "not found")
            self.d.shell(["kill", pid])
            killed.append(" ".join((str(pid), name)))
        for k in killed:
            logger.info(f"process killed: {k}")
        return True

    def _compability(self):
        """
        Init with Android SDK version.
        """
        if self._version > ANDORID_SDK_IMCOMPATIBLE_VERSION:
            self._process_patter = PROCESS_PATTERN
            self._process_keys = PROCESS_KEYS
            self._process_command = f"ps -ef"
        else:
            # Push busybox to replace the outdated ps shell tool on low ver. Android devices
            path = os.path.join(os.path.dirname(__file__), f"resource/{BUSYBOX_NAME}")
            self.push_file(path, f"{BUSYBOX_PUSH_PATH}/{BUSYBOX_NAME}")
            self.shell(f"chmod 775 {BUSYBOX_PUSH_PATH}/{BUSYBOX_NAME}")
            self._process_patter = PROCESS_PATTERN_BUSYBOX  # Deprecated: PROCESS_PATTERN_LOW_VER
            self._process_keys = PROCESS_KEYS_BUSYBOX  # Deprecated: PROCESS_KEYS_LOW_VER
            self._process_command = f"{BUSYBOX_PUSH_PATH}/{BUSYBOX_NAME} ps -ef"

    def _wait_ready(self, timeout: float = 20) -> bool:
        """
        Wait for the Appium server to be ready.
        """
        deadline, err = time.time() + timeout, None
        print(f"waiting for server (timeout={timeout})...", end="")
        while time.time() < deadline:
            try:
                sock = self.d.create_connection(Network.TCP, self._port_for_check)
                sock.close()
                print("\n", end="")
                return True
            except AdbError as e:
                print(".", end="")
                time.sleep(0.2)
                err = e
        print(err)
        return False

    def _check_server_file_exists(self):
        lines = self.d.shell(
            f"ls {self._push_path.replace('/' + DEFAULT_JAR_FILENAME, '')} | grep {DEFAULT_JAR_FILENAME}"
        ).splitlines()
        for line in lines:
            if line == DEFAULT_JAR_FILENAME:
                return True
        return False
