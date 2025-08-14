# Copyright 2024-2025 Francesco Biscani
#
# This file is part of the mizuba library.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from dataclasses import dataclass
from .core import polyjectory, polytree, conjunctions_report
from collections.abc import Iterable
from enum import IntEnum
import os


class otype(IntEnum):
    # NOTE: the numbering here is set up to match the codes
    # used in C++.
    PRIMARY = 1
    SECONDARY = 2
    MASKED = 4


@dataclass
class catalog:
    pj: polyjectory
    pt: polytree
    otypes: Iterable[otype] | None = None
    self_conjunctions: bool = True


def detect_conjunctions(
    cat: catalog | Iterable[catalog],
    conj_thresh: float,
    tmpdir: os.PathLike | str | None = None,
) -> conjunctions_report:
    from .core import _detect_conjunctions_impl
    from dataclasses import fields

    # Helper to turn a catalog into a tuple, while converting the otypes member
    # into a list of ints.
    #
    # NOTE: the dataclasses.astuple() function won't work here, it mandates all fields
    # of a dataclass to be deep-copyable/serialisable.
    def cat_to_tuple(cat: catalog):
        cat_list = [getattr(cat, field.name) for field in fields(cat)]

        # Turn otypes into a list of ints, if present.
        if cat_list[2] is not None:
            cat_list[2] = [int(n) for n in cat_list[2]]

        # Convert the result into a tuple.
        return tuple(cat_list)

    if isinstance(cat, catalog):
        cats = [cat_to_tuple(cat)]
    else:
        cats = [cat_to_tuple(_) for _ in cat]

    # Run the C++ function.
    return _detect_conjunctions_impl(cats, conj_thresh, tmpdir)


del dataclass, polyjectory, polytree, conjunctions_report, IntEnum, Iterable, os
