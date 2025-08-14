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

from ._sgp4_satlist_setup import _sgp4_satlist_setup


class self_conjunctions_test_case(_sgp4_satlist_setup):
    def test_basics(self):
        from .. import polyjectory
        from ._conj_wrapper import _conj_wrapper as conj
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times
        import numpy as np

        # Test error handling.
        pj = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])

        with self.assertRaises(ValueError) as cm:
            conj(conj_det_interval=1.0, pj=pj, conj_thresh=0.0)
        self.assertTrue(
            "The conjunction threshold must be finite and positive, but instead a"
            " value of" in str(cm.exception)
        )

        with self.assertRaises(ValueError) as cm:
            conj(pj, conj_thresh=float("inf"), conj_det_interval=1.0)
        self.assertTrue(
            "The conjunction threshold must be finite and positive, but instead a"
            " value of" in str(cm.exception)
        )

        with self.assertRaises(ValueError) as cm:
            conj(pj, conj_thresh=1.0, conj_det_interval=0.0)
        self.assertTrue(
            "The conjunction detection interval must be finite and positive,"
            in str(cm.exception)
        )

        with self.assertRaises(ValueError) as cm:
            conj(pj, conj_thresh=1.0, conj_det_interval=float("nan"))
        self.assertTrue(
            "The conjunction detection interval must be finite and positive,"
            in str(cm.exception)
        )

        # Test accessors.
        c = conj(pj, conj_thresh=1.0, conj_det_interval=0.1)[0]
        self.assertEqual(c.epoch, (0.0, 0.0))
        self.assertTrue(isinstance(c.conj, np.dtype))

    def test_main(self):
        from .. import (
            polyjectory,
        )
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times
        from ._conj_wrapper import _conj_wrapper as conj

        # Single planar circular orbit case.
        pj = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])

        # Run the test for several conjunction detection intervals.
        for conj_det_interval in [0.01, 0.1, 0.5, 2.0, 5.0, 7.0]:
            c, pt = conj(pj, conj_thresh=0.1, conj_det_interval=conj_det_interval)

            # No conjunctions expected.
            self.assertEqual(len(c.conjunctions), 0)

            # Test otypes initialisation.
            c = conj(
                pj,
                conj_thresh=0.1,
                conj_det_interval=conj_det_interval,
                otypes=[1] * pj.n_objs,
            )[0]

            # Error handling.
            with self.assertRaises(ValueError) as cm:
                conj(
                    pj,
                    conj_thresh=0.1,
                    conj_det_interval=conj_det_interval,
                    otypes=[],
                )
            self.assertTrue(
                "Invalid array of object types detected in a catalog: the expected size based on the number of objects in the polyjectory is 1, but the actual size is 0 instead"
                in str(cm.exception)
            )

            with self.assertRaises(ValueError) as cm:
                conj(
                    pj,
                    conj_thresh=0.1,
                    conj_det_interval=conj_det_interval,
                    otypes=[-5],
                )
            self.assertTrue(
                "The value of an object type in a catalog must be one of [1, 2, 4], but a value of"
                " -5 was detected instead" in str(cm.exception)
            )

            with self.assertRaises(ValueError) as cm:
                conj(
                    pj,
                    conj_thresh=0.1,
                    conj_det_interval=conj_det_interval,
                    otypes=[5],
                )
            self.assertTrue(
                "The value of an object type in a catalog must be one of [1, 2, 4], but a value of 5"
                " was detected instead" in str(cm.exception)
            )

    def test_tmpdir(self):
        # A test checking custom setting for tmpdir.
        import tempfile
        from pathlib import Path
        from .. import polyjectory, set_tmpdir, get_tmpdir
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times
        from ._conj_wrapper import _conj_wrapper as conj

        # Single planar circular orbit case.
        pj = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdir = Path(tmpdirname)

            # NOTE: this checks that the dir is empty.
            self.assertTrue(not any(tmpdir.iterdir()))

            c, pt = conj(pj, conj_thresh=0.1, conj_det_interval=0.01, tmpdir=tmpdir)

            self.assertTrue(any(tmpdir.iterdir()))

            del c, pt

        # A test to check that a custom tmpdir overrides
        # the global tmpdir.
        orig_global_tmpdir = get_tmpdir()
        set_tmpdir(__file__)

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdir = Path(tmpdirname)

            # NOTE: this checks that the dir is empty.
            self.assertTrue(not any(tmpdir.iterdir()))

            c, pt = conj(pj, conj_thresh=0.1, conj_det_interval=0.01, tmpdir=tmpdir)

            self.assertTrue(any(tmpdir.iterdir()))

            del c, pt

        # Restore the original global temp dir.
        set_tmpdir(orig_global_tmpdir)

    def test_broad_narrow_phase(self):
        # NOTE: for the broad-phase, we are relying
        # on internal debug checks implemented in C++.

        # We rely on sgp4 data for this test.
        if not hasattr(type(self), "sparse_sat_list"):
            return

        from .. import (
            make_sgp4_polyjectory,
            otype,
        )
        import numpy as np
        from ._conj_wrapper import _conj_wrapper as conj
        import sys

        sat_list = self.half_sat_list

        begin_jd = 2460496.5

        # Build the polyjectory. Run it for only 15 minutes.
        duration = 15.0 / 1440.0
        pj = make_sgp4_polyjectory(sat_list, begin_jd, begin_jd + duration)[0]

        # Build a list of object types that excludes two satellites
        # that we know undergo a conjunction.
        otypes = [otype.PRIMARY] * pj.n_objs
        otypes[6746] = otype.SECONDARY
        otypes[4549] = otype.SECONDARY

        # Run several tests using several conjunction detection intervals.
        # Store the conjunctions arrays for more testing later.
        c_arrays = []

        for cdet_interval in [1.0 / 1440, 5.0 / 1440.0, 1.0]:
            # Build the conjunctions report object. This will trigger
            # the internal C++ sanity checks in debug mode.
            c, pt = conj(
                pj, conj_thresh=10.0, conj_det_interval=cdet_interval, otypes=otypes
            )

            c_arrays.append(c.conjunctions)

            # The conjunctions must be sorted according to the TCA.
            self.assertTrue(np.all(np.diff(c.conjunctions["tca"]) >= 0))

            # All conjunctions must happen before the polyjectory end time.
            self.assertTrue(c.conjunctions["tca"][-1] < duration)

            # No conjunction must be at or above the threshold.
            self.assertTrue(np.all(np.diff(c.conjunctions["dca"]) < 10))

            # Objects cannot have conjunctions with themselves.
            self.assertTrue(np.all(c.conjunctions["i"] != c.conjunctions["j"]))

            # Check the catalog indices in the conjunctions.
            self.assertTrue(np.all(c.conjunctions["cat_i"] == 0))
            self.assertTrue(np.all(c.conjunctions["cat_j"] == 0))

            # DCA must be consistent with state vectors.
            self.assertTrue(
                np.all(
                    np.isclose(
                        np.linalg.norm(
                            c.conjunctions["ri"] - c.conjunctions["rj"], axis=1
                        ),
                        c.conjunctions["dca"],
                        rtol=1e-14,
                        atol=0.0,
                    )
                )
            )

            # Conjunctions cannot happen between secondaries.
            self.assertFalse(
                (4549, 6746) in list(tuple(_) for _ in c.conjunctions[["i", "j"]])
            )

            # Verify the conjunctions with the sgp4 python module.
            sl_array = np.array(sat_list)
            for cj in c.conjunctions:
                # Fetch the conjunction data.
                tca = cj["tca"]
                i, j = cj["i"], cj["j"]
                ri, rj = cj["ri"], cj["rj"]
                vi, vj = cj["vi"], cj["vj"]

                # Fetch the satellites.
                sat_i = sl_array[i]
                sat_j = sl_array[j]

                ei, sri, svi = sat_i.sgp4(begin_jd, tca)
                ej, srj, svj = sat_j.sgp4(begin_jd, tca)

                diff_ri = np.linalg.norm(sri - ri)
                diff_rj = np.linalg.norm(srj - rj)

                diff_vi = np.linalg.norm(svi - vi)
                diff_vj = np.linalg.norm(svj - vj)

                # NOTE: unit of measurement here is [km], vs typical
                # values of >1e3 km in the coordinates. Thus, relative
                # error is 1e-11, absolute error is ~10µm.
                self.assertLess(diff_ri, 1e-8)
                self.assertLess(diff_rj, 1e-8)

                # NOTE: unit of measurement here is [km/s], vs typicial
                # velocity values of >1 km/s.
                self.assertLess(diff_vi, 1e-11)
                self.assertLess(diff_vj, 1e-11)

            # Verify refcount handling on the conjunctions array.
            rc = sys.getrefcount(c)
            tmp_conj = c.conjunctions
            self.assertEqual(sys.getrefcount(c), rc + 1)
            with self.assertRaises(ValueError):
                tmp_conj[:] = tmp_conj
            with self.assertRaises(AttributeError):
                c.conjunctions = tmp_conj

        # Run consistency checks on c_arrays.
        for i in range(len(c_arrays)):
            cj_i = c_arrays[i]

            for j in range(i + 1, len(c_arrays)):
                cj_j = c_arrays[j]

                self.assertEqual(cj_i.shape, cj_j.shape)
                self.assertTrue(np.all(cj_i["i"] == cj_j["i"]))
                self.assertTrue(np.all(cj_i["j"] == cj_j["j"]))
                self.assertLess(
                    np.max(np.abs((cj_i["tca"] - cj_j["tca"]) / cj_j["tca"])), 1e-11
                )
                self.assertLess(
                    np.max(np.linalg.norm(cj_i["ri"] - cj_j["ri"], axis=1)), 1e-7
                )
                self.assertLess(
                    np.max(np.linalg.norm(cj_i["rj"] - cj_j["rj"], axis=1)), 1e-7
                )

        # Build a conjunctions report object with all masked otypes.
        # There cannot be aabb collisions or conjunctions.
        c, pt = conj(
            pj,
            conj_thresh=10.0,
            conj_det_interval=1.0,
            otypes=[otype.MASKED] * pj.n_objs,
        )

        self.assertEqual(len(c.conjunctions), 0)

        # Same with all secondaries.
        c, pt = conj(
            pj,
            conj_thresh=10.0,
            conj_det_interval=1.0,
            otypes=[otype.SECONDARY] * pj.n_objs,
        )

        self.assertEqual(len(c.conjunctions), 0)

        # Try with a mix of secondaries and masked.
        otypes = [otype.SECONDARY] * (pj.n_objs // 2)
        otypes += [otype.MASKED] * (pj.n_objs - pj.n_objs // 2)

        c, pt = conj(
            pj,
            conj_thresh=10.0,
            conj_det_interval=1.0,
            otypes=otypes,
        )

        self.assertEqual(len(c.conjunctions), 0)

    def test_empty_traj(self):
        # Test to check that a polyjectory containing one or more
        # empty trajectories works as expected.
        from .. import polyjectory
        from ._conj_wrapper import _conj_wrapper as conj
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times
        import numpy as np

        # Construct a trajectory with zero steps.
        tcs_shape = list(_planar_circ_tcs.shape)
        tcs_shape[0] = 0
        tcs_no_steps = np.zeros(tuple(tcs_shape), dtype=float)

        pj = polyjectory(
            [_planar_circ_tcs, tcs_no_steps], [_planar_circ_times, []], [0, 0]
        )
        c = conj(pj, conj_thresh=1.0, conj_det_interval=0.1)[0]
        self.assertEqual(len(c.conjunctions), 0)

        pj = polyjectory(
            [_planar_circ_tcs, tcs_no_steps, tcs_no_steps],
            [_planar_circ_times, [], []],
            [0, 0, 0],
        )
        c = conj(pj, conj_thresh=1.0, conj_det_interval=0.1)[0]
        self.assertEqual(len(c.conjunctions), 0)

        pj = polyjectory(
            [tcs_no_steps, _planar_circ_tcs, tcs_no_steps],
            [[], _planar_circ_times, []],
            [0, 0, 0],
        )
        c = conj(pj, conj_thresh=1.0, conj_det_interval=0.1)[0]
        self.assertEqual(len(c.conjunctions), 0)

        pj = polyjectory(
            [tcs_no_steps, tcs_no_steps, _planar_circ_tcs],
            [[], [], _planar_circ_times],
            [0, 0, 0],
        )
        c = conj(pj, conj_thresh=1.0, conj_det_interval=0.1)[0]
        self.assertEqual(len(c.conjunctions), 0)

    def test_nonzero_tbegin(self):
        # Simple test for a single object
        # whose trajectory begins at t > 0.
        from .. import polyjectory
        from ._conj_wrapper import _conj_wrapper as conj
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times

        # Shift up the times.
        _planar_circ_times = _planar_circ_times + 1.0

        # Single planar circular orbit case.
        pj = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])

        # Run the test for several conjunction detection intervals.
        for conj_det_interval in [0.01, 0.1, 0.5, 2.0, 5.0, 7.0, 10.0]:
            c, pt = conj(pj, conj_thresh=0.1, conj_det_interval=conj_det_interval)

            # No conjunctions expected.
            self.assertEqual(len(c.conjunctions), 0)

    def test_cd_begin_end(self):
        # Test to check for correctness with trajectories
        # beginning and ending within a conjunction step.
        from .. import polyjectory
        from ._conj_wrapper import _conj_wrapper as conjunctions
        import numpy as np

        # NOTE: in these tests, we have 2 objects initially
        # placed on the x axis at +-1. The two objects
        # move with uniform unitary speed towards the origin,
        # where they will meet at t = 1.

        # The overall time data runs at regular 0.1 intervals from 0 to 2.
        tm_data = np.array(
            [
                0.0,
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
                0.6,
                0.7,
                0.8,
                0.9,
                1.0,
                1.1,
                1.2,
                1.3,
                1.4,
                1.5,
                1.6,
                1.7,
                1.8,
                1.9,
                2.0,
            ]
        )

        # First case: no overlap between the two trajectories.

        # The time data for object 1 goes up to 0.9
        tm_data_0 = tm_data[:10]
        # The time data for object 2 goes from 1.1 to the end.
        tm_data_1 = tm_data[11:]

        # Construct the trajectory data for the first object, moving
        # right to left.
        traj_data_0 = []
        for tm in tm_data_0[1:]:
            tdata = np.zeros((7, 4))
            tdata[0, 0] = 1.0 - (tm - 0.1)
            tdata[0, 1] = -1.0
            tdata[3, 0] = -1.0

            traj_data_0.append(tdata)
        traj_data_0 = np.ascontiguousarray(np.array(traj_data_0).transpose((0, 2, 1)))

        # Construct the trajectory data for the second object, moving
        # left to right.
        traj_data_1 = []
        for tm in tm_data_1[1:]:
            tdata = np.zeros((7, 4))
            tdata[0, 0] = -(1.0 - (tm - 0.1))
            tdata[0, 1] = 1.0
            tdata[3, 0] = 1.0

            traj_data_1.append(tdata)
        traj_data_1 = np.ascontiguousarray(np.array(traj_data_1).transpose((0, 2, 1)))

        # Construct the polyjectory.
        pj = polyjectory([traj_data_0, traj_data_1], [tm_data_0, tm_data_1], [0, 0])

        # Run conjunction detection.
        cj = conjunctions(pj=pj, conj_thresh=1e-6, conj_det_interval=2.0 / 3.0)[0]

        # We must not detect any conjunction because the conjunection happens
        # when there is no data for both trajectories.
        self.assertEqual(len(cj.conjunctions), 0)

        # Second case: overlap between the two trajectories. The overlap occurs
        # in the second conjunction step.
        tm_data_0 = tm_data[:12]
        tm_data_1 = tm_data[9:]

        traj_data_0 = []
        for tm in tm_data_0[1:]:
            tdata = np.zeros((7, 4))
            tdata[0, 0] = 1.0 - (tm - 0.1)
            tdata[0, 1] = -1.0
            tdata[3, 0] = -1.0

            traj_data_0.append(tdata)
        traj_data_0 = np.ascontiguousarray(np.array(traj_data_0).transpose((0, 2, 1)))

        traj_data_1 = []
        for tm in tm_data_1[1:]:
            tdata = np.zeros((7, 4))
            tdata[0, 0] = -(1.0 - (tm - 0.1))
            tdata[0, 1] = 1.0
            tdata[3, 0] = 1.0

            traj_data_1.append(tdata)
        traj_data_1 = np.ascontiguousarray(np.array(traj_data_1).transpose((0, 2, 1)))

        pj = polyjectory([traj_data_0, traj_data_1], [tm_data_0, tm_data_1], [0, 0])
        cj = conjunctions(pj=pj, conj_thresh=1e-6, conj_det_interval=2.0 / 3.0)[0]
        # Here we must detect the conjunction.
        conjs = cj.conjunctions
        self.assertEqual(len(conjs), 1)
        self.assertTrue(np.all(conjs["i"] == 0))
        self.assertTrue(np.all(conjs["j"] == 1))
        self.assertTrue(np.all(conjs["cat_i"] == 0))
        self.assertTrue(np.all(conjs["cat_j"] == 0))
        self.assertAlmostEqual(conjs["tca"][0], 1.0, places=15)
        self.assertAlmostEqual(conjs["dca"][0], 0.0, delta=1e-15)
        self.assertTrue(np.allclose(conjs["ri"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["rj"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vi"][0], [-1, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vj"][0], [1, 0, 0], atol=1e-15, rtol=0.0))

        # Third case: both trajectories beginning staggered within the
        # conjunction step, no conjunction.
        tm_data_0 = tm_data[11:]
        tm_data_1 = tm_data[12:]

        traj_data_0 = []
        for tm in tm_data_0[1:]:
            tdata = np.zeros((7, 4))
            tdata[0, 0] = 1.0 - (tm - 0.1)
            tdata[0, 1] = -1.0
            tdata[3, 0] = -1.0

            traj_data_0.append(tdata)
        traj_data_0 = np.ascontiguousarray(np.array(traj_data_0).transpose((0, 2, 1)))

        traj_data_1 = []
        for tm in tm_data_1[1:]:
            tdata = np.zeros((7, 4))
            tdata[0, 0] = -(1.0 - (tm - 0.1))
            tdata[0, 1] = 1.0
            tdata[3, 0] = 1.0

            traj_data_1.append(tdata)
        traj_data_1 = np.ascontiguousarray(np.array(traj_data_1).transpose((0, 2, 1)))

        pj = polyjectory([traj_data_0, traj_data_1], [tm_data_0, tm_data_1], [0, 0])
        cj = conjunctions(pj=pj, conj_thresh=1e-6, conj_det_interval=2.0 / 3.0)[0]
        self.assertEqual(len(cj.conjunctions), 0)

        # Fourth case: both trajectories beginning staggered within the
        # conjunction step, with conjunction.
        tm_data_0 = tm_data[9:]
        tm_data_1 = tm_data[8:]

        traj_data_0 = []
        for tm in tm_data_0[1:]:
            tdata = np.zeros((7, 4))
            tdata[0, 0] = 1.0 - (tm - 0.1)
            tdata[0, 1] = -1.0
            tdata[3, 0] = -1.0

            traj_data_0.append(tdata)
        traj_data_0 = np.ascontiguousarray(np.array(traj_data_0).transpose((0, 2, 1)))

        traj_data_1 = []
        for tm in tm_data_1[1:]:
            tdata = np.zeros((7, 4))
            tdata[0, 0] = -(1.0 - (tm - 0.1))
            tdata[0, 1] = 1.0
            tdata[3, 0] = 1.0

            traj_data_1.append(tdata)
        traj_data_1 = np.ascontiguousarray(np.array(traj_data_1).transpose((0, 2, 1)))

        pj = polyjectory([traj_data_0, traj_data_1], [tm_data_0, tm_data_1], [0, 0])
        cj = conjunctions(pj=pj, conj_thresh=1e-6, conj_det_interval=2.0 / 3.0)[0]
        conjs = cj.conjunctions
        self.assertEqual(len(conjs), 1)
        self.assertTrue(np.all(conjs["i"] == 0))
        self.assertTrue(np.all(conjs["j"] == 1))
        self.assertAlmostEqual(conjs["tca"][0], 1.0, places=15)
        self.assertAlmostEqual(conjs["dca"][0], 0.0, delta=1e-15)
        self.assertTrue(np.allclose(conjs["ri"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["rj"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vi"][0], [-1, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vj"][0], [1, 0, 0], atol=1e-15, rtol=0.0))

        # Fifth case: both trajectories ending staggered within the conjunction step,
        # no conjunction.
        tm_data_0 = tm_data[:9]
        tm_data_1 = tm_data[:8]

        traj_data_0 = []
        for tm in tm_data_0[1:]:
            tdata = np.zeros((7, 4))
            tdata[0, 0] = 1.0 - (tm - 0.1)
            tdata[0, 1] = -1.0
            tdata[3, 0] = -1.0

            traj_data_0.append(tdata)
        traj_data_0 = np.ascontiguousarray(np.array(traj_data_0).transpose((0, 2, 1)))

        traj_data_1 = []
        for tm in tm_data_1[1:]:
            tdata = np.zeros((7, 4))
            tdata[0, 0] = -(1.0 - (tm - 0.1))
            tdata[0, 1] = 1.0
            tdata[3, 0] = 1.0

            traj_data_1.append(tdata)
        traj_data_1 = np.ascontiguousarray(np.array(traj_data_1).transpose((0, 2, 1)))

        pj = polyjectory([traj_data_0, traj_data_1], [tm_data_0, tm_data_1], [0, 0])
        cj = conjunctions(pj=pj, conj_thresh=1e-6, conj_det_interval=2.0 / 3.0)[0]
        self.assertEqual(len(cj.conjunctions), 0)

        # Sixth case: both trajectories ending staggered within the conjunction step,
        # with conjunction.
        tm_data_0 = tm_data[:11]
        tm_data_1 = tm_data[:12]

        traj_data_0 = []
        for tm in tm_data_0[1:]:
            tdata = np.zeros((7, 4))
            tdata[0, 0] = 1.0 - (tm - 0.1)
            tdata[0, 1] = -1.0
            tdata[3, 0] = -1.0

            traj_data_0.append(tdata)
        traj_data_0 = np.ascontiguousarray(np.array(traj_data_0).transpose((0, 2, 1)))

        traj_data_1 = []
        for tm in tm_data_1[1:]:
            tdata = np.zeros((7, 4))
            tdata[0, 0] = -(1.0 - (tm - 0.1))
            tdata[0, 1] = 1.0
            tdata[3, 0] = 1.0

            traj_data_1.append(tdata)
        traj_data_1 = np.ascontiguousarray(np.array(traj_data_1).transpose((0, 2, 1)))

        pj = polyjectory([traj_data_0, traj_data_1], [tm_data_0, tm_data_1], [0, 0])
        cj = conjunctions(pj=pj, conj_thresh=1e-6, conj_det_interval=2.0 / 3.0)[0]
        conjs = cj.conjunctions
        # NOTE: we assert >=1 conjunctions are detected,
        # as here we are at the limits of the numerics and a second
        # spurious conjunction might be detected.
        self.assertGreaterEqual(len(conjs), 1)
        self.assertTrue(np.all(conjs["i"] == 0))
        self.assertTrue(np.all(conjs["j"] == 1))
        self.assertTrue(np.all(conjs["cat_i"] == 0))
        self.assertTrue(np.all(conjs["cat_j"] == 0))
        self.assertAlmostEqual(conjs["tca"][0], 1.0, places=15)
        self.assertAlmostEqual(conjs["dca"][0], 0.0, delta=1e-15)
        self.assertTrue(np.allclose(conjs["ri"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["rj"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vi"][0], [-1, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vj"][0], [1, 0, 0], atol=1e-15, rtol=0.0))

    def test_validate_catalog(self):
        from .. import polyjectory, polytree, detect_conjunctions, catalog
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times
        from copy import deepcopy

        # Inconsistent number of objectsin pj vs pt.
        pj1 = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])
        pj2 = polyjectory(
            [_planar_circ_tcs] + [_planar_circ_tcs],
            [_planar_circ_times] + [_planar_circ_times],
            [0, 0],
        )
        pt = polytree(pj1, conj_det_interval=0.1)
        cat = catalog(pj=pj2, pt=pt)

        with self.assertRaises(ValueError) as cm:
            detect_conjunctions(
                cat,
                conj_thresh=1.0,
            )
        self.assertTrue(
            "Inconsistent numbers of objects detected in a catalog: the polyjectory contains 2 object(s) while the polytree contains 1 object(s)"
            in str(cm.exception)
        )

        # Inconsistent maxT.
        pj1 = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])
        new_times = deepcopy(_planar_circ_times)
        new_times[-1] += 1.0
        pj2 = polyjectory([_planar_circ_tcs], [new_times], [0])
        pt = polytree(pj1, conj_det_interval=0.1)
        cat = catalog(pj=pj2, pt=pt)
        with self.assertRaises(ValueError) as cm:
            detect_conjunctions(cat, conj_thresh=1.0)
        self.assertTrue(
            "Inconsistent maxT values detected in a catalog" in str(cm.exception)
        )

        # Inconsistent epoch.
        pj1 = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])
        pj2 = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0], epoch=1.0)
        pt = polytree(pj1, conj_det_interval=0.1)
        cat = catalog(pj=pj2, pt=pt)
        with self.assertRaises(ValueError) as cm:
            detect_conjunctions(cat, conj_thresh=1.0)
        self.assertTrue(
            "Inconsistent epochs detected in a catalog" in str(cm.exception)
        )

        # Test the self conjunctions flag.
        pj = polyjectory(
            [_planar_circ_tcs] + [_planar_circ_tcs],
            [_planar_circ_times] + [_planar_circ_times],
            [0, 0],
        )
        pt = polytree(pj, conj_det_interval=0.1)
        cat = catalog(pj=pj, pt=pt, self_conjunctions=False)
        conj = detect_conjunctions(cat, conj_thresh=1.0)
        self.assertEqual(len(conj.conjunctions), 0)
