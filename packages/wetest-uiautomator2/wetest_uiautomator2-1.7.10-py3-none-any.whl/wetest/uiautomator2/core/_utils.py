import inspect
import logging
import subprocess
import types
from typing import Callable

from ._logger import Logger


def execute(command, log=False) -> str:
    p = subprocess.Popen(command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    lines = p.stdout.readlines()
    ret = ""
    for line in lines:
        ret += str(line, encoding="UTF-8")
    if log:
        print(ret)
    return ret


class NothingType(object):
    def __init__(self, log: bool = False, err: Exception = None):
        self.log = log
        self.err = err

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        if self.log:
            print(f"ignores a method call: {attr}")
        return self.nothing

    def nothing(self, *args, **kwargs):
        return self

    def __bool__(self):
        return False

    __nonzero__ = __bool__


class Expectation:
    def __init__(
        self,
        obj: object,
        msg: str = None,
        err: Exception = None,
        logger: Logger = None,
        show_log: bool = False,
        handler: Callable = None,
        *args,
        **kwargs,
    ):
        self._obj = obj
        self._msg = msg
        self._err = err
        self._logger = logger
        self._show_log = show_log
        self._handler = handler if handler else None
        self._handler_args = args
        self._handler_kwargs = kwargs

    def __getattr__(self, attr):

        def wrapper(*args, **kwargs):
            # Seperate getattr with method call to prevent from catching AttributeError due to calling unexisted methods
            target = getattr(self._obj, attr)

            try:
                if isinstance(target, types.MethodType):
                    return target(*args, **kwargs)
                return target
            except Exception as e:  # Exceptions during method call
                if self._show_log:
                    self.print(f"expect().{attr}() raises {e.__class__.__name__}: {e}", logging.ERROR)
                if self._msg:
                    self.print(self._msg, logging.INFO)
                if self._err:
                    raise self._err
                if self._handler:
                    if "exception" in inspect.getfullargspec(self._handler).args:
                        self._handler(exception=e, *self._handler_args, **self._handler_kwargs)
                    else:
                        self._handler(*self._handler_args, **self._handler_kwargs)
                return NothingType(err=e, log=self._show_log)

        return wrapper

    def print(self, msg: str, level: int):
        if self._logger:
            self._logger.log(level, msg)
        else:
            print(msg)


"""
Deprecated: typing.Self requires Python 3.8 and is not good for business.
"""
# class ExpectBase(object):
#     from typing import Self
#     def expect(
#         self,
#         msg: str = None,
#         err: Exception = None,
#         show_log: bool = False,
#         handler: Callable = None,
#         *args,
#         **kwargs,
#         ) -> Self:
#         """
#         Usage: object.expect().method(*args, **kwargs)

#         The internal exception handler.
#         It can be elegantly combined with interfaces that need try-catch a lot.
#         It transmits all method calls to android_driver, and automatically skip or raise exceptions.
#         When an exception is skipped, an NothingType instance will be returned.
#         NothingType responses and then ignores any method call to prevent error caused by chaining.
#         Inspired by expect() method in Rust.

#         Args:
#             err (Exception, optional): Raise err instead of the actual raised one.
#                 Defaults to None.
#                 Return a NothingType if err is None. Nothing type ignores any method calls without errors.
#             show_log (bool, optional): True for print logs for debugging. Defaults to False.

#         Returns:
#             Self <- Expectation: a wrapped Self.
#         """
#         return Expectation(self, msg, err, show_log, handler, *args, **kwargs)
