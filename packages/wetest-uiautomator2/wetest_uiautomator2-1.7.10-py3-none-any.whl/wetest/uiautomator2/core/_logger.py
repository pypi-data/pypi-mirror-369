# !/usr/bin/python3
# coding: utf-8

import logging

from typing import Any

from ._exceptions import AppiumAndroidException
from ._types import BaseResp


class Logger:
    def __init__(self, logger_name: str = "wetest-uiautomator2"):
        self.formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        self.isShowLog = True
        self.logger = logging.getLogger(logger_name)
        self.set_log_level(logging.INFO)

        ch = logging.StreamHandler()
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)

    def set_log_level(self, level):
        self.logger.setLevel(level)

    def enable_log(self):
        self.isShowLog = True
        self.set_log_level(logging.INFO)

    def disable_log(self):
        self.isShowLog = False
        self.set_log_level(logging.CRITICAL)

    def debug(self, msg, *args):
        if self.isShowLog:
            self.logger.debug(msg, *args)

    def info(self, msg, *args):
        if self.isShowLog:
            self.logger.info(msg, *args)

    def warning(self, msg, *args):
        if self.isShowLog:
            self.logger.warning(msg, *args)

    def error(self, msg, *args):
        if self.isShowLog:
            self.logger.error(msg, *args)

    def log(self, level, msg, *args, **kwargs):
        if self.isShowLog:
            self.logger.log(level, msg, *args, **kwargs)