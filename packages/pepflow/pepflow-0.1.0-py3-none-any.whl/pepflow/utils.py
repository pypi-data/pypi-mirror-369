from __future__ import annotations

import enum
import numbers
from typing import Any

import numpy as np


def SOP(v, w):
    """Symmetric Outer Product."""
    return 1 / 2 * (np.outer(v, w) + np.outer(w, v))


def SOP_self(v):
    return SOP(v, v)


def merge_dict(dict1, dict2):
    merged_dict = dict1.copy()
    for key in dict2.keys():
        if key in dict1.keys():
            merged_dict[key] += dict2[key]
        else:
            merged_dict[key] = dict2[key]
    return merged_dict


def prune_dict(my_dict):
    pruned_dict = dict()
    for key in my_dict.keys():
        if my_dict[key] != 0:
            pruned_dict[key] = my_dict[key]
    return pruned_dict


class Op(enum.Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"


class Comparator(enum.Enum):
    GT = "GT"
    LT = "LT"
    EQ = "EQ"


def is_numerical(val: Any) -> bool:
    return isinstance(val, numbers.Number)
