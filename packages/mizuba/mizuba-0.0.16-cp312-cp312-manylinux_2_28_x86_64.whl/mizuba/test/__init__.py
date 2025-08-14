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


def run_test_suite(data_sources: bool = False) -> None:
    import unittest as _ut

    from . import (
        test_self_conjunctions,
        test_boundary_self_conjunctions,
        test_boundary_cross_conjunctions,
        test_polyjectory,
        test_polytree,
        test_heyoka_self_conjunctions,
        test_heyoka_cross_conjunctions,
        test_data_sources,
        test_make_sgp4_polyjectory,
        test_tmpdir,
        test_cross_conjunctions,
    )

    retval = 0

    tl = _ut.TestLoader()

    suite = tl.loadTestsFromTestCase(test_self_conjunctions.self_conjunctions_test_case)
    suite.addTest(
        tl.loadTestsFromTestCase(test_cross_conjunctions.cross_conjunctions_test_case)
    )
    suite.addTest(
        tl.loadTestsFromTestCase(
            test_boundary_self_conjunctions.boundary_self_conjunctions_test_case
        )
    )
    suite.addTest(
        tl.loadTestsFromTestCase(
            test_boundary_cross_conjunctions.boundary_cross_conjunctions_test_case
        )
    )
    suite.addTest(
        tl.loadTestsFromTestCase(
            test_heyoka_self_conjunctions.heyoka_self_conjunctions_test_case
        )
    )
    suite.addTest(
        tl.loadTestsFromTestCase(
            test_heyoka_cross_conjunctions.heyoka_cross_conjunctions_test_case
        )
    )
    suite.addTest(tl.loadTestsFromTestCase(test_polyjectory.polyjectory_test_case))
    suite.addTest(tl.loadTestsFromTestCase(test_polytree.polytree_test_case))
    if data_sources:
        suite.addTest(
            tl.loadTestsFromTestCase(test_data_sources.data_sources_test_case)
        )
    suite.addTest(
        tl.loadTestsFromTestCase(
            test_make_sgp4_polyjectory.make_sgp4_polyjectory_test_case
        )
    )
    suite.addTest(tl.loadTestsFromTestCase(test_tmpdir.tmpdir_test_case))

    test_result = _ut.TextTestRunner(verbosity=2).run(suite)

    if len(test_result.failures) > 0 or len(test_result.errors) > 0:
        retval = 1

    if retval != 0:
        raise RuntimeError("One or more tests failed.")
