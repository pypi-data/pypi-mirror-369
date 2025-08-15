# !/usr/bin/python3
# coding: utf-8

import re
from typing import Union, List, Dict


class expstr:
    method = ""
    suffix = ""

    def __init__(self, string: str, attrib: str = None) -> None:
        assert type(string) is str, "class expstr receives a non-string value"
        self.string = string
        self.attrib = attrib if attrib else ""

    def __repr__(self) -> str:
        return self.string


class ContainStr(expstr):
    method = "contains"
    suffix = "_contains"


class RegexStr(expstr):
    method = "matches"
    suffix = "_matches"

    def __init__(self, string: str, attrib: str = None) -> None:
        super().__init__(string, attrib)
        try:
            re.compile(self.string)
        except re.error:
            raise ValueError(f"regular expression fails to compile: '{self.string}'") from None


class StartwithStr(expstr):
    method = "starts-with"
    suffix = "_startswith"


class EndwithStr(expstr):
    method = "ends-with"
    suffix = "_endswith"


EXPANED_STR_TYPE_LIST: List = [
    ContainStr,
    RegexStr,
    StartwithStr,
    EndwithStr,
]


class AttrSelector(dict):
    __fields = {
        "text": "text",
        "classname": "class",
        "package": "package",
        "id": "resource-id",
        "content_desc": "content-desc",
        "checkable": "checkable",
        "checked": "checked",
        "clickable": "clickable",
        "long_clickable": "long_clickable",
        "focused": "focused",
        "focusable": "focusable",
        "scrollable": "scrollable",
        "enabled": "enabled",
        "selected": "selected",
        "password": "selected",
        "displayed": "displayed",
    }

    def __init__(self, **kwargs: Dict[str, Union[bool, str, expstr, List[str], List[expstr]]]):
        for k in kwargs:
            self[k] = kwargs[k]

    def __setitem__(self, k: str, v):
        # Preset keys
        if k in self.__fields:
            return super().__setitem__(self.__fields[k], v)

        # Preset keys with _contains, _startswith, _endswith and _matches suffix
        for C in EXPANED_STR_TYPE_LIST:
            if k.endswith(C.suffix):
                """
                The process might be a bit hard to comprehend.
                Input:
                    dict[prefix_suffix] = value
                Transfer:
                    dict[prefix] = expstr(
                        string = valuek
                        attrib = self.__fields[prefix]
                        method ≈ suffix)
                Postprocessing:
                    make_xpath(dict) -> str
                """
                prefix = k.replace(C.suffix, "")
                if not prefix in self.__fields:
                    break
                attrib = self.__fields[prefix]
                if isinstance(v, str):
                    return super().__setitem__(k.replace(prefix, attrib), C(string=v, attrib=attrib))
                elif isinstance(v, list):
                    return super().__setitem__(k.replace(prefix, attrib), [C(string=i, attrib=attrib) for i in v])

                # v is not valid
                raise ValueError(f"the value of '{k}' cannot be a {v.__class__.__name__} type")

        # k is not valid
        raise AttributeError(
            f"'{k}' is not allowed. only the given params {list(self.__fields.keys())} or them combined with "
            + f"{[C.suffix for C in EXPANED_STR_TYPE_LIST]} suffixes are allowed the be given"
        )

    def __delitem__(self, k):
        if k in self.__fields:
            super().__delitem__(self.__fields[k])
        elif k in self.keys():
            super().__delitem__(k)


"""
from typing import TypedDict

class InnerSelectorTypeHint(TypedDict):
    text: str
    classname: str
    package: str
    id: str
    resource_id: str
    checkable: bool
    checked: bool
    clickable: bool
    long_clickable: bool
    focused: bool
    focusable: bool
    scrollable: bool
    enabled: bool
    selected: bool
    password: bool
    displayed: bool
"""
