# !/usr/bin/python3
# coding: utf-8

from __future__ import annotations

import re
import os
import platform
import functools
import subprocess

from typing import Union, Tuple, List
from collections import namedtuple

from .core._const import *
from .core._logger import Logger
from .core._utils import execute


logger = Logger("wetest-utils")


def launch_app(serial: str, package: str, mode: int = 1):
    execute(f"adb -s {serial} shell monkey -p {package} {mode}")
    logger.info(f"{package} launched")


def kill_app(serial: str, package: str):
    execute(f"adb -s {serial} shell am force-stop {package}")
    logger.info(f"{package} forced-stopped")


def is_unix() -> bool:
    """
    Check if the platfrom is based on UNIX

    Returns:
        bool
    """
    return "MACOS" in platform.platform().upper() or "LINUX" in platform.platform().upper()


def port_is_occupied(port: int) -> Tuple[bool, str, int]:
    """
    Check if the port is occupied.

    Args:
        port (int)

    Returns:
        Tuple[bool, str, int]: occupied or not, port using user, port using pid.
    """
    assert is_unix(), "not a MacOS or Linux platform"
    try:
        # out = subprocess.check_output(f"lsof -P -i tcp:{port}", shell=True).decode("utf-8").splitlines()
        out = execute(f"lsof -P -i tcp:{port}").splitlines()
        vals = re.search(LSOF_PATTERN, out[-1]).groups()
        print("vals: ", vals)
        user, pid, _ = vals
        logger.info(f"port {port} has been used by: {out[-1]}")
        return True, user, int(pid)
    except subprocess.CalledProcessError:
        logger.info(f"port {port} is available")
    return False, None, None


def adb_forward_remove(serial, local: int):
    """
    Rewrapped remove adb forward.

    Args:
        serial (str): The device serial.
        local (int): Local port number to remove.
    """
    execute(f"adb -s {serial} forward --remove tcp:{local}")
    logger.info(f"adb -s {serial} forward tcp:{local} removed from listening")


def release_port(serial, port: int, user: str = "", pid: int = 0):
    """
    Release port usage by remove adb forward or kill processes.

    Args:
        serial (str): The device serial.
        port (int)
        user (str, optional): Defaults to "".
        pid (int, optional): Defaults to 0.
    """
    assert is_unix(), "not a MacOS or Linux platform"
    if not user or user == "adb":
        adb_forward_remove(serial, port)
    else:
        execute("kill {pid}")
        logger.info(f"process {pid} killed")


def adb_forward(serial, local: int, remote: int, check: bool = False):
    """
    Rewrapped adb forward.

    Args:
        serial (str): The device serial.
        local (int): Local port number.
        remote (int): Remote port number.
        check (bool, optional): Check if the local port is occupied.
    """
    if check and is_unix():
        occupied, user, pid = port_is_occupied(local)
        if occupied:
            release_port(serial, local, user, pid)
    execute(f"adb -s {serial} forward tcp:{local} tcp:{remote}")
    logger.info(f"adb -s {serial} forward tcp:{local} tcp:{remote}")


def push_dir(
    serial: str,
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
        serial (str): The device serial.
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

    def is_matched(pattern: str, string: str, regular: str):
        if regular:
            res = re.compile(pattern).match(string)
            if res:
                return True
            return False
        else:
            return pattern in string

    excludes, filters = [] if not excludes else excludes, [] if not filters else filters
    if not os.path.isdir(source):
        raise FileNotFoundError(f"source path '{source}' points to no directory")

    # Make root dir
    execute(f"adb -s {serial} mkdir {target}")

    file_cnt, dir_cnt, skipped_dirs, filtered_files = 0, 0, [], []
    for root, _, files in os.walk(source):
        rel_dir = root.replace(source, "").strip("/")  # get relative path for subs in source

        # Excluding directories
        is_skipped = False
        for e in excludes:
            if is_matched(pattern=e, string=root, regular=regular):
                is_skipped = True
                break
        if is_skipped:
            skipped_dirs.append(root)
            continue

        # Make dir to prevent secure_mkdirs error on OS above Android 11
        abs_dir = os.path.join(target, rel_dir)
        execute(f"adb -s {serial} shell mkdir {abs_dir}")

        for file in files:
            src, dst, is_filtered = os.path.join(root, file), os.path.join(abs_dir, file), False

            # Filtering files
            for f in filters:
                if is_matched(pattern=f, string=src, regular=regular):
                    is_filtered = True
                    break
            if is_filtered:
                filtered_files.append(src)

            ret = execute(f"adb -s {serial} push {src} {dst}")
            if log:
                logger.info(ret)

        file_cnt += len(files)
        dir_cnt += 1

    # Log and return
    ret = (file_cnt, dir_cnt, skipped_dirs, filtered_files)
    logger.info(f"file push finished. {file_cnt} files under {dir_cnt} dirs have been pushed")
    if not log:
        return ret
    if skipped_dirs:
        logger.warning("these directories have been skipped:")
        for each in skipped_dirs:
            logger.warning(each)
    if filtered_files:
        logger.warning("these files have been filtered:")
        for each in filtered_files:
            logger.warning(each)
    return ret


def push_file(serial, source: str, target: str):
    """
    Push file to device.

    Args:
        serial (str): The device serial.
        apk_path (str, optional): Local resource path.
        push_path (str, optional): Push path.
    """
    if not os.path.isfile(source):
        raise FileNotFoundError(f"source path '{source}' points to no directory")
    logger.info(f"pushing file '{source}' to '{target}' ...")
    execute(f"adb -s {serial} push {source} {target}")


def permission(serial: str, package_name: str, permissions: Union[str, List[str]], give: bool = True) -> str:
    """
    Set permission for a package.

    Args:
        serial (str): The device serial.
        package_name (str)
        permissions (Union[str, List[str]]): Permission name in Android permission manifest.
            Example: READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
        give (bool, optional): True for grant permission. False for revoke permission. Defaults to True.

    Returns:
        str: Shell logs.
    """
    if isinstance(permissions, str):
        permissions = [permissions]
    ret = ""
    for p in permissions:
        ret += execute(
            f"adb -s {serial} shell pm {'grant' if give else 'revoke'} {package_name} android.permission.{p}"
        )
    return ret


def set_permission(serial: str, package_name: str, give: bool = True):
    """
    Set permission with presets for a package.

    Usage:
        utils.set_permission(pkg_name).readwrite()

    Args:
        serial (str): The device serial.
        package_name (str)
        give (bool, optional): True for grant permission. False for revoke permission. Defaults to True.

    Returns:
        str: Shell logs.
    """
    return namedtuple("SetPackagePermission", ["read", "write", "readwrite"])(
        functools.partial(permission, serial, package_name, "READ_EXTERNAL_STORAGE", give),
        functools.partial(permission, serial, package_name, "WRITE_EXTERNAL_STORAGE", give),
        functools.partial(permission, serial, package_name, ["READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE"], give),
    )
