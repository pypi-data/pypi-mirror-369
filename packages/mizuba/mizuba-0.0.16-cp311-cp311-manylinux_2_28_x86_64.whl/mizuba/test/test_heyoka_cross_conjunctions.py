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

from ._common_heyoka_test import _common_heyoka_test
from ._self_cross_utils import _self_cross_utils


class heyoka_cross_conjunctions_test_case(_common_heyoka_test, _self_cross_utils):
    # A test case in which we compare the results of conjunction
    # detection with a heyoka simulation in which we keep
    # track of the minimum distances between the objects.
    def test_tle(self):
        from .. import _have_sgp4_deps, _have_heyoka_deps, otype

        if not _have_sgp4_deps() or not _have_heyoka_deps():
            return

        from .. import (
            polyjectory,
            conjunctions_report,
            polytree,
            detect_conjunctions,
            catalog,
        )
        import numpy as np
        import pathlib
        import polars as pl
        from sgp4.api import SatrecArray
        from .._sgp4_polyjectory import _make_satrec_from_dict

        # Deterministic seeding.
        rng = np.random.default_rng(42)

        # Fetch the current directory.
        cur_dir = pathlib.Path(__file__).parent.resolve()

        # Load the test data.
        try:
            gpes = pl.read_parquet(cur_dir / "strack_20240705.parquet")
        except Exception:
            return

        # Create the satellite objects.
        sat_list = [_make_satrec_from_dict(_) for _ in gpes.iter_rows(named=True)]

        # Select around 10 objects.
        sat_list = sat_list[:: len(sat_list) // 10]
        N = len(sat_list)

        # Compute their positions at some date.
        jd = 2460496.5
        sat_arr = SatrecArray(sat_list)
        e, r, v = sat_arr.sgp4(np.array([jd]), np.array([0.0]))
        self.assertTrue(np.all(e == 0))

        # NOTE: gravitational constant in km**3/(kg * s**2).
        ta, hy_conj_list = self._make_kep_ta(6.67430e-20, 5.972168e24, N)

        # Setup the initial conditions.
        ic_rs = ta.state.reshape((-1, 7))
        for i in range(N):
            ic_rs[i, 0:3] = r[i][0]
            ic_rs[i, 3:6] = v[i][0]
            ic_rs[i, 6] = np.linalg.norm(ic_rs[i, 0:3])

        # Run the propagation and fetch the continuous output object.
        res = ta.propagate_for(86400.0, c_output=True)
        c_out = res[4]

        # Sort the heyoka conjunction list according to tca and transform it into the
        # appropriate structured dtype.
        hy_conj_list = np.sort(
            np.array(hy_conj_list, dtype=conjunctions_report.conj), order="tca"
        )
        # Store the original heyoka conjunction list so that we can reset it at the
        # beginning of the for loop below.
        orig_hy_conj_list = hy_conj_list

        N1 = N // 2
        N2 = N - N1
        conj_det_interval = 60.0

        # NOTE: we use cdt_delta to run the tests with mismatched conjunction detection intervals
        # in the two polytrees.
        for cdt_delta in [0.0, conj_det_interval / 10.0]:
            hy_conj_list = orig_hy_conj_list

            # Build the polyjectories/polytrees.
            trajs1 = []
            for i in range(N1):
                trajs1.append(
                    np.ascontiguousarray(
                        c_out.tcs[:, i * 7 : (i + 1) * 7, :].transpose((0, 2, 1))
                    )
                )

            trajs2 = []
            for i in range(N1, N):
                trajs2.append(
                    np.ascontiguousarray(
                        c_out.tcs[:, i * 7 : (i + 1) * 7, :].transpose((0, 2, 1))
                    )
                )

            pj1 = polyjectory(trajs1, [c_out.times] * N1, [0] * N1)
            pj2 = polyjectory(trajs2, [c_out.times] * N2, [0] * N2)
            pt1 = polytree(pj1, conj_det_interval=conj_det_interval + cdt_delta)
            pt2 = polytree(pj2, conj_det_interval=conj_det_interval - cdt_delta)

            # Run first a conjunction detection with stupidly large conjunction threshold,
            # so that we detect all conjunctions.
            cj = detect_conjunctions(
                [
                    catalog(pj1, pt1),
                    catalog(pj2, pt2),
                ],
                conj_thresh=1e6,
            )

            # Filter out from the conjunctions list the conjunctions which happen
            # at the time boundaries of the polyjectory, since heyoka cannot detect these.
            cjc = cj.conjunctions[
                np.logical_and.reduce(
                    (
                        np.abs(cj.conjunctions["tca"] - 86400.0) > 86400.0 * 1e-14,
                        cj.conjunctions["tca"] > 0,
                    )
                )
            ]

            # Initial comparison: check number of conjunctions, tcas, dcas, and posvels. This must work
            # because we know that conjunctions are sorted according to tca.
            self.assertEqual(len(cjc), len(hy_conj_list))
            self.assertTrue(
                np.all(np.isclose(cjc["tca"], hy_conj_list["tca"], rtol=1e-12))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["dca"], hy_conj_list["dca"], rtol=1e-12))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["ri"], hy_conj_list["ri"], rtol=1e-10))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["rj"], hy_conj_list["rj"], rtol=1e-10))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["vi"], hy_conj_list["vi"], rtol=1e-10))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["vj"], hy_conj_list["vj"], rtol=1e-10))
            )
            self.assertTrue(np.all(np.logical_or(cjc["cat_i"] == 0, cjc["cat_i"] == 1)))
            self.assertTrue(np.all(np.logical_or(cjc["cat_j"] == 0, cjc["cat_j"] == 1)))
            self.assertTrue(np.all(cjc["cat_i"] <= cjc["cat_j"]))

            # Check manually the indices for a few randomly-selected conjunctions.
            hy_df = pl.DataFrame(hy_conj_list)
            for _ in range(10):
                cur_conj = cjc[rng.integers(0, len(cjc))]
                orig_i = (
                    cur_conj["i"] if (cur_conj["cat_i"] == 0) else (cur_conj["i"] + N1)
                )
                orig_j = (
                    cur_conj["j"] if (cur_conj["cat_j"] == 0) else (cur_conj["j"] + N1)
                )
                # NOTE: here we are switching from relative to absolute tolerances, hence they are higher.
                self._check_conj_present(
                    hy_df, orig_i, orig_j, cur_conj, 0.0, 1e-8, 1e-6
                )

            # Re-run the same conjunction test but make only the first object of each polyjectory a primary.
            otypes1 = [otype.SECONDARY] * N1
            otypes1[0] = otype.PRIMARY
            otypes2 = [otype.SECONDARY] * N2
            otypes2[0] = otype.PRIMARY

            cj = detect_conjunctions(
                [
                    catalog(pj1, pt1, otypes=otypes1),
                    catalog(pj2, pt2, otypes=otypes2),
                ],
                conj_thresh=1e6,
            )

            flist = hy_conj_list[
                np.logical_or.reduce(
                    (
                        hy_conj_list["i"] == 0,
                        hy_conj_list["i"] == N1,
                        hy_conj_list["j"] == 0,
                        hy_conj_list["j"] == N1,
                    )
                )
            ]

            cjc = cj.conjunctions[
                np.logical_and.reduce(
                    (
                        np.abs(cj.conjunctions["tca"] - 86400.0) > 86400.0 * 1e-14,
                        cj.conjunctions["tca"] > 0,
                    )
                )
            ]

            self.assertEqual(len(cjc), len(flist))
            self.assertTrue(np.all(np.isclose(cjc["tca"], flist["tca"], rtol=1e-12)))
            self.assertTrue(np.all(np.isclose(cjc["dca"], flist["dca"], rtol=1e-12)))
            self.assertTrue(np.all(np.isclose(cjc["ri"], flist["ri"], rtol=1e-10)))
            self.assertTrue(np.all(np.isclose(cjc["rj"], flist["rj"], rtol=1e-10)))
            self.assertTrue(np.all(np.isclose(cjc["vi"], flist["vi"], rtol=1e-10)))
            self.assertTrue(np.all(np.isclose(cjc["vj"], flist["vj"], rtol=1e-10)))
            self.assertTrue(np.all(np.logical_or(cjc["cat_i"] == 0, cjc["cat_i"] == 1)))
            self.assertTrue(np.all(np.logical_or(cjc["cat_j"] == 0, cjc["cat_j"] == 1)))
            self.assertTrue(np.all(cjc["cat_i"] <= cjc["cat_j"]))

            # Check manually the indices for a few randomly-selected conjunctions.
            hy_df = pl.DataFrame(flist)
            for _ in range(10):
                cur_conj = cjc[rng.integers(0, len(cjc))]
                orig_i = (
                    cur_conj["i"] if (cur_conj["cat_i"] == 0) else (cur_conj["i"] + N1)
                )
                orig_j = (
                    cur_conj["j"] if (cur_conj["cat_j"] == 0) else (cur_conj["j"] + N1)
                )
                # NOTE: here we are switching from relative to absolute tolerances, hence they are higher.
                self._check_conj_present(
                    hy_df, orig_i, orig_j, cur_conj, 0.0, 1e-9, 1e-7
                )

            # Run another conjunction detection, this time conjunction
            # thresh 500km.
            cj = detect_conjunctions(
                [
                    catalog(pj1, pt1),
                    catalog(pj2, pt2),
                ],
                conj_thresh=500,
            )

            hy_conj_list = hy_conj_list[hy_conj_list["dca"] < 500.0]

            cjc = cj.conjunctions[
                np.logical_and.reduce(
                    (
                        np.abs(cj.conjunctions["tca"] - 86400.0) > 86400.0 * 1e-14,
                        cj.conjunctions["tca"] > 0,
                    )
                )
            ]

            self.assertEqual(len(cjc), len(hy_conj_list))
            self.assertTrue(
                np.all(np.isclose(cjc["tca"], hy_conj_list["tca"], rtol=1e-12))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["dca"], hy_conj_list["dca"], rtol=1e-12))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["ri"], hy_conj_list["ri"], rtol=1e-12))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["rj"], hy_conj_list["rj"], rtol=1e-12))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["vi"], hy_conj_list["vi"], rtol=1e-12))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["vj"], hy_conj_list["vj"], rtol=1e-12))
            )
            self.assertTrue(np.all(np.logical_or(cjc["cat_i"] == 0, cjc["cat_i"] == 1)))
            self.assertTrue(np.all(np.logical_or(cjc["cat_j"] == 0, cjc["cat_j"] == 1)))
            self.assertTrue(np.all(cjc["cat_i"] <= cjc["cat_j"]))

            # Check manually the indices for a few randomly-selected conjunctions.
            hy_df = pl.DataFrame(hy_conj_list)
            for _ in range(10):
                cur_conj = cjc[rng.integers(0, len(cjc))]
                orig_i = (
                    cur_conj["i"] if (cur_conj["cat_i"] == 0) else (cur_conj["i"] + N1)
                )
                orig_j = (
                    cur_conj["j"] if (cur_conj["cat_j"] == 0) else (cur_conj["j"] + N1)
                )
                # NOTE: here we are switching from relative to absolute tolerances, hence they are higher.
                self._check_conj_present(
                    hy_df, orig_i, orig_j, cur_conj, 0.0, 1e-9, 1e-7
                )

            # Re-run the same conjunction test but make only the second object of each polyjectory a primary.
            otypes1 = [otype.SECONDARY] * N1
            otypes1[1] = otype.PRIMARY
            otypes2 = [otype.SECONDARY] * N2
            otypes2[1] = otype.PRIMARY

            cj = detect_conjunctions(
                [
                    catalog(pj1, pt1, otypes=otypes1),
                    catalog(pj2, pt2, otypes=otypes2),
                ],
                conj_thresh=500,
            )

            flist = hy_conj_list[
                np.logical_or.reduce(
                    (
                        hy_conj_list["i"] == 1,
                        hy_conj_list["i"] == N1 + 1,
                        hy_conj_list["j"] == 1,
                        hy_conj_list["j"] == N1 + 1,
                    )
                )
            ]

            cjc = cj.conjunctions[
                np.logical_and.reduce(
                    (
                        np.abs(cj.conjunctions["tca"] - 86400.0) > 86400.0 * 1e-14,
                        cj.conjunctions["tca"] > 0,
                    )
                )
            ]

            self.assertEqual(len(cjc), len(flist))
            self.assertTrue(np.all(np.isclose(cjc["tca"], flist["tca"], rtol=1e-12)))
            self.assertTrue(np.all(np.isclose(cjc["dca"], flist["dca"], rtol=1e-12)))
            self.assertTrue(np.all(np.isclose(cjc["ri"], flist["ri"], rtol=1e-12)))
            self.assertTrue(np.all(np.isclose(cjc["rj"], flist["rj"], rtol=1e-12)))
            self.assertTrue(np.all(np.isclose(cjc["vi"], flist["vi"], rtol=1e-12)))
            self.assertTrue(np.all(np.isclose(cjc["vj"], flist["vj"], rtol=1e-12)))
            self.assertTrue(np.all(np.logical_or(cjc["cat_i"] == 0, cjc["cat_i"] == 1)))
            self.assertTrue(np.all(np.logical_or(cjc["cat_j"] == 0, cjc["cat_j"] == 1)))
            self.assertTrue(np.all(cjc["cat_i"] <= cjc["cat_j"]))

            # Check manually the indices for a few randomly-selected conjunctions.
            hy_df = pl.DataFrame(flist)
            for _ in range(10):
                cur_conj = cjc[rng.integers(0, len(cjc))]
                orig_i = (
                    cur_conj["i"] if (cur_conj["cat_i"] == 0) else (cur_conj["i"] + N1)
                )
                orig_j = (
                    cur_conj["j"] if (cur_conj["cat_j"] == 0) else (cur_conj["j"] + N1)
                )
                # NOTE: here we are switching from relative to absolute tolerances, hence they are higher.
                self._check_conj_present(
                    hy_df, orig_i, orig_j, cur_conj, 0.0, 1e-9, 1e-7
                )

            # Run another conjunction detection, this time conjunction
            # thresh 200km.
            cj = detect_conjunctions(
                [
                    catalog(pj1, pt1),
                    catalog(pj2, pt2),
                ],
                conj_thresh=200,
            )

            hy_conj_list = hy_conj_list[hy_conj_list["dca"] < 200.0]

            cjc = cj.conjunctions[
                np.logical_and.reduce(
                    (
                        np.abs(cj.conjunctions["tca"] - 86400.0) > 86400.0 * 1e-14,
                        cj.conjunctions["tca"] > 0,
                    )
                )
            ]

            self.assertEqual(len(cjc), len(hy_conj_list))
            self.assertTrue(
                np.all(np.isclose(cjc["tca"], hy_conj_list["tca"], rtol=1e-12))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["dca"], hy_conj_list["dca"], rtol=1e-12))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["ri"], hy_conj_list["ri"], rtol=1e-12))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["rj"], hy_conj_list["rj"], rtol=1e-12))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["vi"], hy_conj_list["vi"], rtol=1e-12))
            )
            self.assertTrue(
                np.all(np.isclose(cjc["vj"], hy_conj_list["vj"], rtol=1e-12))
            )
            self.assertTrue(np.all(np.logical_or(cjc["cat_i"] == 0, cjc["cat_i"] == 1)))
            self.assertTrue(np.all(np.logical_or(cjc["cat_j"] == 0, cjc["cat_j"] == 1)))
            self.assertTrue(np.all(cjc["cat_i"] <= cjc["cat_j"]))

            # Check manually the indices for a few randomly-selected conjunctions.
            hy_df = pl.DataFrame(hy_conj_list)
            for _ in range(10):
                cur_conj = cjc[rng.integers(0, len(cjc))]
                orig_i = (
                    cur_conj["i"] if (cur_conj["cat_i"] == 0) else (cur_conj["i"] + N1)
                )
                orig_j = (
                    cur_conj["j"] if (cur_conj["cat_j"] == 0) else (cur_conj["j"] + N1)
                )
                # NOTE: here we are switching from relative to absolute tolerances, hence they are higher.
                self._check_conj_present(
                    hy_df, orig_i, orig_j, cur_conj, 0.0, 1e-9, 1e-7
                )

    def test_close_conjunction(self):
        # Test keplerian orbits leading to collisions.
        from .. import _have_heyoka_deps

        if not _have_heyoka_deps():
            return

        from copy import copy
        from .. import (
            polyjectory,
            otype,
            conjunctions_report,
            polytree,
            detect_conjunctions,
            catalog,
        )
        import numpy as np

        N = 2
        conj_det_interval = 0.1
        conj_thresh = 1e-4

        # NOTE: run the same test with different initial times for the trajectories and mismatched
        # conjunction detection intervals.
        for cdt_delta in [0.0, conj_det_interval / 10.0]:
            for init_time in [0.0, 0.2, 0.31]:
                ta, hy_conj_list = self._make_kep_ta(1.0, 1.0, N)
                ta.time = init_time

                # Setup the initial conditions.
                ic_rs = ta.state.reshape((-1, 7))

                ic_rs[0, 0] = 1.0
                ic_rs[0, 4] = 1.0
                ic_rs[0, 6] = 1.0

                ic_rs[1, 0] = -1.0
                ic_rs[1, 4] = 1.0
                ic_rs[1, 6] = 1.0

                c_out = ta.propagate_for(4.8, c_output=True)[4]

                # Build the polyjectories/polytrees.
                trajs = []
                for i in range(N):
                    trajs.append(
                        np.ascontiguousarray(
                            c_out.tcs[:, i * 7 : (i + 1) * 7, :].transpose((0, 2, 1))
                        )
                    )
                pj1 = polyjectory([trajs[0]], [c_out.times], [0])
                pj2 = polyjectory([trajs[1]], [c_out.times], [0])
                pt1 = polytree(pj1, conj_det_interval=conj_det_interval - cdt_delta)
                pt2 = polytree(pj2, conj_det_interval=conj_det_interval + cdt_delta)

                # Detect conjunctions.
                cj = detect_conjunctions(
                    [catalog(pj=pj1, pt=pt1), catalog(pj=pj2, pt=pt2)],
                    conj_thresh=conj_thresh,
                )

                # Store the original conjunctions array for later use.
                orig_conj = copy(cj.conjunctions)

                hy_conj_arr = np.sort(
                    np.array(hy_conj_list, dtype=conjunctions_report.conj), order="tca"
                )

                self.assertEqual(len(hy_conj_arr), 2)

                # Compare the results.
                self.assertEqual(len(cj.conjunctions), len(hy_conj_arr))
                self.assertTrue(
                    np.all(
                        np.isclose(
                            cj.conjunctions["tca"], hy_conj_arr["tca"], rtol=1e-12
                        )
                    )
                )
                self.assertTrue(
                    np.all(
                        np.isclose(
                            cj.conjunctions["dca"], hy_conj_arr["dca"], rtol=1e-12
                        )
                    )
                )
                self.assertTrue(np.all(cj.conjunctions["i"] == 0))
                self.assertTrue(np.all(cj.conjunctions["j"] == 0))
                self.assertTrue(np.all(cj.conjunctions["cat_i"] == 0))
                self.assertTrue(np.all(cj.conjunctions["cat_j"] == 1))
                self.assertTrue(
                    np.all(
                        np.isclose(cj.conjunctions["ri"], hy_conj_arr["ri"], rtol=1e-12)
                    )
                )
                self.assertTrue(
                    np.all(
                        np.isclose(cj.conjunctions["rj"], hy_conj_arr["rj"], rtol=1e-12)
                    )
                )
                self.assertTrue(
                    np.all(
                        np.isclose(cj.conjunctions["vi"], hy_conj_arr["vi"], rtol=1e-12)
                    )
                )
                self.assertTrue(
                    np.all(
                        np.isclose(cj.conjunctions["vj"], hy_conj_arr["vj"], rtol=1e-12)
                    )
                )

                # Try primary-secondary as otypes.
                cj = detect_conjunctions(
                    [
                        catalog(pj=pj1, pt=pt1, otypes=[otype.PRIMARY]),
                        catalog(pj=pj2, pt=pt2, otypes=[otype.SECONDARY]),
                    ],
                    conj_thresh=conj_thresh,
                )
                self.assertTrue(np.all(orig_conj == cj.conjunctions))

                cj = detect_conjunctions(
                    [
                        catalog(pj=pj1, pt=pt1, otypes=[otype.SECONDARY]),
                        catalog(pj=pj2, pt=pt2, otypes=[otype.PRIMARY]),
                    ],
                    conj_thresh=conj_thresh,
                )
                self.assertTrue(np.all(orig_conj == cj.conjunctions))

                # Try with several otype combination that must result
                # in no detected conjunctions.
                cj = detect_conjunctions(
                    [
                        catalog(pj=pj1, pt=pt1, otypes=[otype.MASKED]),
                        catalog(pj=pj2, pt=pt2, otypes=[otype.MASKED]),
                    ],
                    conj_thresh=conj_thresh,
                )
                self.assertEqual(len(cj.conjunctions), 0)

                cj = detect_conjunctions(
                    [
                        catalog(pj=pj1, pt=pt1, otypes=[otype.SECONDARY]),
                        catalog(pj=pj2, pt=pt2, otypes=[otype.SECONDARY]),
                    ],
                    conj_thresh=conj_thresh,
                )
                self.assertEqual(len(cj.conjunctions), 0)

                cj = detect_conjunctions(
                    [
                        catalog(pj=pj1, pt=pt1, otypes=[otype.PRIMARY]),
                        catalog(pj=pj2, pt=pt2, otypes=[otype.MASKED]),
                    ],
                    conj_thresh=conj_thresh,
                )
                self.assertEqual(len(cj.conjunctions), 0)

                cj = detect_conjunctions(
                    [
                        catalog(pj=pj1, pt=pt1, otypes=[otype.MASKED]),
                        catalog(pj=pj2, pt=pt2, otypes=[otype.PRIMARY]),
                    ],
                    conj_thresh=conj_thresh,
                )
                self.assertEqual(len(cj.conjunctions), 0)

                cj = detect_conjunctions(
                    [
                        catalog(pj=pj1, pt=pt1, otypes=[otype.SECONDARY]),
                        catalog(pj=pj2, pt=pt2, otypes=[otype.MASKED]),
                    ],
                    conj_thresh=conj_thresh,
                )
                self.assertEqual(len(cj.conjunctions), 0)

                cj = detect_conjunctions(
                    [
                        catalog(pj=pj1, pt=pt1, otypes=[otype.MASKED]),
                        catalog(pj=pj2, pt=pt2, otypes=[otype.SECONDARY]),
                    ],
                    conj_thresh=conj_thresh,
                )
                self.assertEqual(len(cj.conjunctions), 0)

                # Try an equatorial collision too.
                ta.time = init_time
                ta.state[:] = 0.0
                ta.reset_cooldowns()
                hy_conj_list.clear()

                ic_rs[0, 0] = 1.0
                ic_rs[0, 4] = 1.0
                ic_rs[0, 6] = 1.0

                ic_rs[1, 0] = -1.0
                ic_rs[1, 4] = 1.0
                ic_rs[1, 6] = 1.0

                c_out = ta.propagate_for(4.8, c_output=True)[4]

                # Build the polyjectories/polytrees.
                trajs = []
                for i in range(N):
                    trajs.append(
                        np.ascontiguousarray(
                            c_out.tcs[:, i * 7 : (i + 1) * 7, :].transpose((0, 2, 1))
                        )
                    )
                pj1 = polyjectory([trajs[0]], [c_out.times], [0])
                pj2 = polyjectory([trajs[1]], [c_out.times], [0])
                pt1 = polytree(pj1, conj_det_interval=conj_det_interval + cdt_delta)
                pt2 = polytree(pj2, conj_det_interval=conj_det_interval - cdt_delta)

                # Detect conjunctions.
                cj = detect_conjunctions(
                    [catalog(pj=pj1, pt=pt1), catalog(pj=pj2, pt=pt2)],
                    conj_thresh=conj_thresh,
                )

                hy_conj_arr = np.sort(
                    np.array(hy_conj_list, dtype=conjunctions_report.conj), order="tca"
                )

                self.assertEqual(len(hy_conj_arr), 2)

                # Compare the results.
                self.assertEqual(len(cj.conjunctions), len(hy_conj_arr))
                self.assertTrue(
                    np.all(
                        np.isclose(
                            cj.conjunctions["tca"], hy_conj_arr["tca"], rtol=1e-12
                        )
                    )
                )
                self.assertTrue(
                    np.all(
                        np.isclose(
                            cj.conjunctions["dca"], hy_conj_arr["dca"], rtol=1e-12
                        )
                    )
                )
                self.assertTrue(np.all(cj.conjunctions["i"] == 0))
                self.assertTrue(np.all(cj.conjunctions["j"] == 0))
                self.assertTrue(np.all(cj.conjunctions["cat_i"] == 0))
                self.assertTrue(np.all(cj.conjunctions["cat_j"] == 1))
                self.assertTrue(
                    np.all(
                        np.isclose(cj.conjunctions["ri"], hy_conj_arr["ri"], rtol=1e-12)
                    )
                )
                self.assertTrue(
                    np.all(
                        np.isclose(cj.conjunctions["rj"], hy_conj_arr["rj"], rtol=1e-12)
                    )
                )
                self.assertTrue(
                    np.all(
                        np.isclose(cj.conjunctions["vi"], hy_conj_arr["vi"], rtol=1e-12)
                    )
                )
                self.assertTrue(
                    np.all(
                        np.isclose(cj.conjunctions["vj"], hy_conj_arr["vj"], rtol=1e-12)
                    )
                )

                # Try two identical trajectories. This should produce no conjunctions.
                ta.time = init_time
                ta.state[:] = 0.0
                ta.reset_cooldowns()
                hy_conj_list.clear()

                ic_rs[0, 0] = 1.0
                ic_rs[0, 4] = 1.0
                ic_rs[0, 6] = 1.0

                ic_rs[1, 0] = 1.0
                ic_rs[1, 4] = 1.0
                ic_rs[1, 6] = 1.0

                c_out = ta.propagate_for(4.8, c_output=True)[4]

                # Build the polyjectory.
                trajs = []
                for i in range(N):
                    trajs.append(
                        np.ascontiguousarray(
                            c_out.tcs[:, i * 7 : (i + 1) * 7, :].transpose((0, 2, 1))
                        )
                    )
                pj1 = polyjectory([trajs[0]], [c_out.times], [0])
                pj2 = polyjectory([trajs[1]], [c_out.times], [0])
                pt1 = polytree(pj1, conj_det_interval=conj_det_interval - cdt_delta)
                pt2 = polytree(pj2, conj_det_interval=conj_det_interval + cdt_delta)

                # Detect conjunctions.
                cj = detect_conjunctions(
                    [catalog(pj=pj1, pt=pt1), catalog(pj=pj2, pt=pt2)],
                    conj_thresh=conj_thresh,
                )

                self.assertEqual(len(cj.conjunctions), 0)
                self.assertEqual(len(hy_conj_list), 0)

    def test_boundary(self):
        # A test similar to the first test in test_boundary_conjunctions, but using Keplerian
        # orbits integrated with heyoka.
        from .. import _have_heyoka_deps

        if not _have_heyoka_deps():
            return

        from math import sqrt, pi
        import numpy as np
        from .. import polyjectory, polytree, detect_conjunctions, catalog

        # Setup a fixed-centre problem with two non-interacting
        # objects following Keplerian orbits. The first orbit
        # is circular, the second elliptic. The two objects will experience
        # conjunctions at the peri/apo centre of the elliptic orbit.
        N = 2
        ta, hy_conj_list = self._make_kep_ta(1.0, 1.0, N)

        # Setup the initial conditions.
        ic_rs = ta.state.reshape((-1, 7))

        # Eccentricity of the second orbit.
        ecc = 0.3

        ic_rs[0, 0] = 1.0
        ic_rs[0, 4] = 1.0
        ic_rs[0, 6] = 1.0

        ic_rs[1, 0] = 1.0 + ecc
        ic_rs[1, 4] = -1.0 * sqrt((1 - ecc) / (1 + ecc))
        ic_rs[1, 6] = 1.0 + ecc

        # Propagate until a short time before the second conjunction.
        c_out = ta.propagate_for(pi - 1e-6, c_output=True)[4]

        # NOTE: heyoka must detect only the initial conjunction at t == 0.
        self.assertEqual(len(hy_conj_list), 1)

        conj_det_interval = 0.1

        for cdt_delta in [0.0, conj_det_interval / 10.0]:
            # Build the polyjectory.
            trajs = []
            for i in range(N):
                trajs.append(
                    np.ascontiguousarray(
                        c_out.tcs[:, i * 7 : (i + 1) * 7, :].transpose((0, 2, 1))
                    )
                )
            pj1 = polyjectory([trajs[0]], [c_out.times], [0])
            pj2 = polyjectory([trajs[1]], [c_out.times], [0])
            pt1 = polytree(pj1, conj_det_interval=conj_det_interval + cdt_delta)
            pt2 = polytree(pj2, conj_det_interval=conj_det_interval - cdt_delta)

            # Run conjunction detection with a very large threshold.
            cj = detect_conjunctions(
                [catalog(pj=pj1, pt=pt1), catalog(pj=pj2, pt=pt2)],
                conj_thresh=10000.0,
            )

            # NOTE: we must detect 2 conjunctions: the initial one at t=0
            # and the second one which does not correspond to a minimum
            # of the mutual distance.
            self.assertEqual(len(cj.conjunctions), 2)
            self.assertEqual(cj.conjunctions["tca"][0], 0.0)
            self.assertAlmostEqual(cj.conjunctions["tca"][1], pi - 1e-6, places=15)
            self.assertAlmostEqual(cj.conjunctions["dca"][0], ecc, places=15)

            # A second test in which we repeat the integration of the circular
            # orbit, but starting from (0, 1) rather than (1, 0), and we stop
            # again the integration right before the second conjunction. The objective
            # is to generate trajectory data for the circular orbit that begins
            # later than the other orbit.
            ta.reset_cooldowns()
            ta.time = pi / 2
            ic_rs[:] = 0.0

            ic_rs[0, 1] = 1.0
            ic_rs[0, 3] = -1.0
            ic_rs[0, 6] = 1.0
            ic_rs[1, 0] = 1.0 + ecc
            ic_rs[1, 4] = -1.0 * sqrt((1 - ecc) / (1 + ecc))
            ic_rs[1, 6] = 1.0 + ecc

            new_c_out = ta.propagate_for(pi / 2 - 1e-6, c_output=True)[4]

            # NOTE: no conjunctions must have been detected by heyoka in this
            # second integration.
            self.assertEqual(len(hy_conj_list), 1)

            # Build the trajectory data.
            trajs = []
            # Circular orbit.
            trajs.append(
                np.ascontiguousarray(new_c_out.tcs[:, :7, :].transpose((0, 2, 1)))
            )
            # Elliptic orbit.
            trajs.append(
                np.ascontiguousarray(c_out.tcs[:, 7:14, :].transpose((0, 2, 1)))
            )

            # Build the time data.
            times = []
            # Circular orbit.
            times.append(new_c_out.times)
            # Elliptic orbit.
            times.append(c_out.times)

            pj1 = polyjectory([trajs[0]], [times[0]], [0])
            pj2 = polyjectory([trajs[1]], [times[1]], [0])
            pt1 = polytree(pj1, conj_det_interval=conj_det_interval - cdt_delta)
            pt2 = polytree(pj2, conj_det_interval=conj_det_interval + cdt_delta)

            # Run conjunction detection with a very large threshold.
            cj = detect_conjunctions(
                [catalog(pj=pj1, pt=pt1), catalog(pj=pj2, pt=pt2)],
                conj_thresh=10000.0,
            )

            # NOTE: in addition to the conjunction at the end, we also have a conjunction
            # at the beginning of the circular trajectory (as the distance square
            # between the two objects at t = pi/2 is still increasing).
            self.assertEqual(len(cj.conjunctions), 2)
            self.assertAlmostEqual(cj.conjunctions["tca"][0], pi / 2, places=15)
            self.assertAlmostEqual(cj.conjunctions["tca"][1], pi - 1e-6, places=15)

    def test_epoch_handling(self):
        # This test checks that the merging of conjunctions reports correctly
        # handles catalogs with different epochs.
        from .. import _have_heyoka_deps

        if not _have_heyoka_deps():
            return

        from math import pi
        import numpy as np
        from .. import polyjectory, polytree, detect_conjunctions, catalog

        conj_det_interval = 0.1
        conj_thresh = 1e-3

        # Setup a fixed-centre problem with two non-interacting
        # objects following Keplerian circular orbits. The first orbit is clockwise
        # starting from (-1, 0) at t=0, while the second orbit is counterclockwise
        # starting from (0, -1) at t=pi/2. We must detect a conjunction at tca=pi in the
        # merged report.
        ta1, _ = self._make_kep_ta(1.0, 1.0, 1)
        ta2, _ = self._make_kep_ta(1.0, 1.0, 1)

        # Setup the initial conditions.
        ic_rs1 = ta1.state.reshape((-1, 7))
        ic_rs1[0, 0] = -1.0
        ic_rs1[0, 4] = 1.0
        ic_rs1[0, 6] = 1.0

        ic_rs2 = ta2.state.reshape((-1, 7))
        ic_rs2[0, 1] = -1.0
        ic_rs2[0, 3] = 1.0
        ic_rs2[0, 6] = 1.0

        # Propagate the first orbit until t=3pi/2 and the second orbit until pi.
        c_out1 = ta1.propagate_until(3 * pi / 2, c_output=True)[4]
        c_out2 = ta2.propagate_until(pi, c_output=True)[4]

        # Build the polyjectories and polytrees.
        traj1 = np.ascontiguousarray(c_out1.tcs.transpose((0, 2, 1)))
        traj2 = np.ascontiguousarray(c_out2.tcs.transpose((0, 2, 1)))

        pj1 = polyjectory([traj1], [c_out1.times], [0])
        # NOTE: set the epoch of the second trajectory to pi/2.
        pj2 = polyjectory([traj2], [c_out2.times], [0], epoch=pi / 2)
        pt1 = polytree(pj1, conj_det_interval=conj_det_interval)
        pt2 = polytree(pj2, conj_det_interval=conj_det_interval)

        # Detect conjunctions.
        cr = detect_conjunctions(
            [catalog(pj=pj1, pt=pt1), catalog(pj=pj2, pt=pt2)], conj_thresh
        )

        # The conjunctions epoch must be the earlier epoch, that is, (0, 0).
        self.assertEqual(cr.epoch, (0.0, 0.0))

        # We must have detected a single conjunction.
        conjs = cr.conjunctions
        self.assertEqual(len(conjs), 1)

        # Check the conjunction properties. We expect the conjunction at (1, 0) and t=pi.
        self.assertEqual(conjs[0]["cat_i"], 0)
        self.assertEqual(conjs[0]["cat_j"], 1)
        self.assertEqual(conjs[0]["i"], 0)
        self.assertEqual(conjs[0]["j"], 0)
        self.assertLess(abs(conjs[0]["tca"] - pi), 1e-14)
        self.assertLess(conjs[0]["dca"], 1e-14)
        self.assertLess(np.linalg.norm(conjs[0]["ri"] - [1, 0, 0]), 1e-14)
        self.assertLess(np.linalg.norm(conjs[0]["rj"] - [1, 0, 0]), 1e-14)
        self.assertLess(np.linalg.norm(conjs[0]["vi"] - [0, -1, 0]), 1e-14)
        self.assertLess(np.linalg.norm(conjs[0]["vj"] - [0, 1, 0]), 1e-14)

        # Do the same testing with the catalogs swapped around.
        cr = detect_conjunctions(
            [catalog(pj=pj2, pt=pt2), catalog(pj=pj1, pt=pt1)], conj_thresh
        )
        self.assertEqual(cr.epoch, (0.0, 0.0))
        conjs = cr.conjunctions
        self.assertEqual(len(conjs), 1)
        self.assertEqual(conjs[0]["cat_i"], 0)
        self.assertEqual(conjs[0]["cat_j"], 1)
        self.assertEqual(conjs[0]["i"], 0)
        self.assertEqual(conjs[0]["j"], 0)
        self.assertLess(abs(conjs[0]["tca"] - pi), 1e-14)
        self.assertLess(conjs[0]["dca"], 1e-14)
        self.assertLess(np.linalg.norm(conjs[0]["ri"] - [1, 0, 0]), 1e-14)
        self.assertLess(np.linalg.norm(conjs[0]["rj"] - [1, 0, 0]), 1e-14)
        self.assertLess(np.linalg.norm(conjs[0]["vi"] - [0, 1, 0]), 1e-14)
        self.assertLess(np.linalg.norm(conjs[0]["vj"] - [0, -1, 0]), 1e-14)
