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

from .. import polyjectory, polytree, conjunctions_report, otype
from collections.abc import Iterable
from os import PathLike


# Wrapper to reduce typing for common cases of conjunction detection in the tests.
def _conj_wrapper(
    pj: polyjectory,
    conj_thresh: float,
    conj_det_interval: float,
    otypes: Iterable[otype] | None = None,
    tmpdir: PathLike | None = None,
) -> tuple[conjunctions_report, polytree]:
    from .. import detect_conjunctions, catalog, polytree

    pt = polytree(
        pj=pj,
        conj_det_interval=conj_det_interval,
        tmpdir=tmpdir,
    )

    cat = catalog(pj=pj, pt=pt, otypes=otypes)

    cr = detect_conjunctions(cat, conj_thresh=conj_thresh, tmpdir=tmpdir)

    return cr, pt


del polyjectory, polytree, conjunctions_report, otype, Iterable, PathLike
