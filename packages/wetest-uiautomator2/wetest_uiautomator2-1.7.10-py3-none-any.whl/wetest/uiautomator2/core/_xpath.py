# !/usr/bin/python3
# coding: utf-8

from typing import Union, List

from ._selector import AttrSelector, expstr


def is_string(v):
    return isinstance(v, str) or isinstance(v, expstr)


def is_string_list(v):
    return isinstance(v, list) and all(is_string(i) for i in v)


def unpack_str(k, v: Union[str, expstr]):
    if type(v) is str:
        return f"@{k}='{v}'"
    if isinstance(v, expstr):
        return f"{v.method}(@{v.attrib},'{v.string}')"
    raise ValueError(f"make xpath failed: type of the value of {k} is {v.__class__.__name__}")


def unpack_str_list(k, v: Union[List[str], List[expstr]]):
    return f"{' or '.join([unpack_str(k, i) for i in v])}"


def unpack_bool(k, v: bool):
    return f"@{k}='true'" if v else f"@{k}='false'"


def make_xpath(selector: AttrSelector):
    ret = "//*"
    for k, v in selector.items():
        if is_string(v):
            ret += f"[{unpack_str(k, v)}]"
        elif is_string_list(v):
            ret += f"[{unpack_str_list(k, v)}]"
        elif isinstance(v, bool):
            ret += f"[{unpack_bool(k, v)}]"
        else:
            raise ValueError(
                f"selector contains value that is a string or bool type: " + f"{k} = {v}, v is {v.__class__.__name__}"
            )
    return ret
