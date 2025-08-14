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


import unittest as _ut


# This is a helper class to factor out the setup of an sgp4 satellite list
# in the unit tests.
class _sgp4_satlist_setup(_ut.TestCase):
    @classmethod
    def setUpClass(cls):
        from .. import _have_sgp4_deps

        if not _have_sgp4_deps():
            return

        import pathlib
        import polars as pl
        from bisect import bisect_left
        from .._sgp4_polyjectory import _make_satrec_from_dict

        # Fetch the current directory.
        cur_dir = pathlib.Path(__file__).parent.resolve()

        # Load the test data.
        try:
            gpes = pl.read_parquet(cur_dir / "strack_20240705.parquet")
        except Exception:
            return

        # Create the satellite objects.
        sat_list = [_make_satrec_from_dict(_) for _ in gpes.iter_rows(named=True)]

        # Create a sparse list of satellites.
        # NOTE: we manually include an object for which the
        # trajectory data terminates early if the exit_radius
        # is set to 12000.
        cls.sparse_sat_list = sorted(
            sat_list[::2000] + [sat_list[220]], key=lambda sat: sat.satnum
        )

        # Identify the new index of the added satellite in the sorted list.
        norad_id_list = [_.satnum for _ in cls.sparse_sat_list]
        idx = bisect_left(norad_id_list, sat_list[220].satnum)
        cls.exiting_idx = idx

        # List of 9000 satellites.
        cls.half_sat_list = sat_list[:9000]

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "sparse_sat_list"):
            del cls.sparse_sat_list
            del cls.half_sat_list
