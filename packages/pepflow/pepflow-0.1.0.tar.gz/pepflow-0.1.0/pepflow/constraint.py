from __future__ import annotations

from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from pepflow.point import Scalar

from pepflow import utils


@attrs.frozen
class Constraint:
    """It represents `expression relation 0`."""

    scalar: Scalar | float
    comparator: utils.Comparator
    name: str
