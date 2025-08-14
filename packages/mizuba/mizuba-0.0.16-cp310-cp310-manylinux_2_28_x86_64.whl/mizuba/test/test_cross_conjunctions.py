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
from ._self_cross_utils import _self_cross_utils


class cross_conjunctions_test_case(_sgp4_satlist_setup, _self_cross_utils):
    def test_basics(self):
        # NOTE: catalog validation is tested also in the self conjunctions test case.
        from .. import detect_conjunctions, polyjectory, polytree, catalog
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times
        import numpy as np

        # Check mismatched poly orders.
        pj1 = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])
        pj2 = polyjectory(
            [np.ascontiguousarray(_planar_circ_tcs[:, :3, :])],
            [_planar_circ_times],
            [0],
        )

        pt1 = polytree(pj1, conj_det_interval=0.1)
        pt2 = polytree(pj2, conj_det_interval=0.1)

        with self.assertRaises(ValueError) as cm:
            detect_conjunctions(
                [
                    catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                    catalog(pj=pj2, pt=pt2, self_conjunctions=False),
                ],
                conj_thresh=1.0,
            )
        self.assertTrue(
            "Invalid polynomial order detected in detect_conjunctions(): all polyjectories must have the same polynomial order, but two polyjectories with different orders (20 and 2) were detected"
            in str(cm.exception)
        )

        # Check empty catalog list.
        with self.assertRaises(ValueError) as cm:
            detect_conjunctions(
                [],
                conj_thresh=1.0,
            )
        self.assertTrue(
            "Cannot invoke detect_conjunctions() with an empty list of catalogs"
            in str(cm.exception)
        )

        # Conjunction threshold too high.
        with self.assertRaises(ValueError) as cm:
            detect_conjunctions(
                [
                    catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                    catalog(pj=pj2, pt=pt2, self_conjunctions=False),
                ],
                conj_thresh=np.finfo(float).max,
            )
        self.assertTrue(
            "is too large, resulting in an overflow error" in str(cm.exception)
        )

    def test_broad_narrow_phase(self):
        # We rely on sgp4 data for this test.
        if not hasattr(type(self), "sparse_sat_list"):
            return

        from .. import (
            make_sgp4_polyjectory,
            polytree,
            detect_conjunctions,
            catalog,
            otype,
        )
        import polars as pl

        sat_list = self.half_sat_list

        begin_jd = 2460496.5

        # Build the polyjectory. Run it for only 15 minutes.
        duration = 15.0 / 1440.0
        pj = make_sgp4_polyjectory(sat_list, begin_jd, begin_jd + duration)[0]

        # Run the test for several conjunction detection intervals
        cdet_intervals = [1.0 / 1440, 5.0 / 1440.0, 1.0]
        for cdet_interval in cdet_intervals:
            # Build the polytree.
            pt = polytree(pj, conj_det_interval=cdet_interval)

            # Run self conjunction detection.
            cr = detect_conjunctions(catalog(pj=pj, pt=pt), conj_thresh=10.0)
            conj = cr.conjunctions
            conj_df = pl.DataFrame(conj)

            # Build a list of all objects which experience more than 1 conjunction, paired to the number
            # of conjunctions. We know such objects exist.

            # NOTE: need to start with two lists as the same object may show up as i or j.
            obj_list_i = (
                conj_df.group_by("i")
                .len()
                .filter(pl.col("len") > 1)
                .select(["i", "len"])
                .rows()
            )

            obj_list_j = (
                conj_df.group_by("j")
                .len()
                .filter(pl.col("len") > 1)
                .select(["j", "len"])
                .rows()
            )

            # Merge the two lists into a dict.
            obj_dict = dict(obj_list_i)
            for obj_idx, n_conjs in obj_list_j:
                if obj_idx in obj_dict:
                    obj_dict[obj_idx] += n_conjs
                else:
                    obj_dict[obj_idx] = n_conjs

            # Convert to a list.
            obj_list = obj_dict.items()

            # Run the testing on all objects in obj_list.
            for obj_idx, n_conjs in obj_list:
                # Construct a polyjectory and a polytree from the single object trajectory.
                pj_obj_idx = make_sgp4_polyjectory(
                    [sat_list[obj_idx]], begin_jd, begin_jd + duration
                )[0]
                pt_obj_idx = polytree(pj_obj_idx, conj_det_interval=cdet_interval)

                # Run the check.
                self._compare_self_cross(
                    conj_df, pj, pt, 10.0, obj_idx, n_conjs, pj_obj_idx, pt_obj_idx
                )

                # Run the same check using a slighlty different conj_det_interval in the
                # single object trajectory.
                pt_obj_idx = polytree(
                    pj_obj_idx, conj_det_interval=cdet_interval + cdet_interval / 10.0
                )
                self._compare_self_cross(
                    conj_df, pj, pt, 10.0, obj_idx, n_conjs, pj_obj_idx, pt_obj_idx
                )

            # Repeat the same testing, but this time make the single trajectory
            # start a bit earlier and end a bit later.
            for obj_idx, n_conjs in obj_list:
                pj_obj_idx = make_sgp4_polyjectory(
                    [sat_list[obj_idx]],
                    begin_jd - 1.0 / 256.0,
                    begin_jd + duration + 1.0 / 256.0,
                )[0]
                pt_obj_idx = polytree(pj_obj_idx, conj_det_interval=cdet_interval)

                self._compare_self_cross(
                    conj_df,
                    pj,
                    pt,
                    10.0,
                    obj_idx,
                    n_conjs,
                    pj_obj_idx,
                    pt_obj_idx,
                    1e-14,
                    1e-9,
                )

                # Again with a different conjunction detection interval.
                pt_obj_idx = polytree(
                    pj_obj_idx, conj_det_interval=cdet_interval - cdet_interval / 10.0
                )
                self._compare_self_cross(
                    conj_df,
                    pj,
                    pt,
                    10.0,
                    obj_idx,
                    n_conjs,
                    pj_obj_idx,
                    pt_obj_idx,
                    1e-14,
                    1e-9,
                )

            # Run also a test in which we explicitly mask the only object in the single-object
            # polyjectory. This exercises the codepath that handles masked objects in the cross
            # broad phase.
            obj_idx = list(obj_list)[0][0]
            pj_obj_idx = make_sgp4_polyjectory(
                [sat_list[obj_idx]],
                begin_jd - 1.0 / 256.0,
                begin_jd + duration + 1.0 / 256.0,
            )[0]
            pt_obj_idx = polytree(pj_obj_idx, conj_det_interval=cdet_interval)

            # Run cross conjunction detection, masking out obj_idx in pj.
            otypes = [otype.MASKED]
            cr_cross = detect_conjunctions(
                [
                    catalog(pj=pj, pt=pt, self_conjunctions=False),
                    catalog(
                        pj=pj_obj_idx,
                        pt=pt_obj_idx,
                        otypes=otypes,
                        self_conjunctions=False,
                    ),
                ],
                conj_thresh=10.0,
            )
            cross_conj = cr_cross.conjunctions
            self.assertEqual(len(cross_conj), 0)

            # Again with a different conjunction detection interval.
            pt_obj_idx = polytree(
                pj_obj_idx, conj_det_interval=cdet_interval + cdet_interval / 10.0
            )
            cr_cross = detect_conjunctions(
                [
                    catalog(pj=pj, pt=pt, self_conjunctions=False),
                    catalog(
                        pj=pj_obj_idx,
                        pt=pt_obj_idx,
                        otypes=otypes,
                        self_conjunctions=False,
                    ),
                ],
                conj_thresh=10.0,
            )
            cross_conj = cr_cross.conjunctions
            self.assertEqual(len(cross_conj), 0)

    def test_empty_traj(self):
        # Test to check that a polyjectory containing one or more
        # empty trajectories works as expected.
        from .. import polyjectory, polytree, catalog, detect_conjunctions, otype
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times
        import numpy as np

        conj_det_interval = 0.1

        # Construct a trajectory with zero steps.
        tcs_shape = list(_planar_circ_tcs.shape)
        tcs_shape[0] = 0
        tcs_no_steps = np.zeros(tuple(tcs_shape), dtype=float)

        # Construct the pjs/pts.
        pj1 = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])
        # NOTE: for pj2 we cannot have only empty trajs. We will mask out the non-empty traj later.
        pt1 = polytree(pj1, conj_det_interval=conj_det_interval)
        pj2 = polyjectory(
            [_planar_circ_tcs, tcs_no_steps],
            [_planar_circ_times, []],
            [0, 0],
        )
        pt2 = polytree(pj2, conj_det_interval=conj_det_interval)

        # Run cross conjunction detection.
        cr_cross = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(
                    pj=pj2,
                    pt=pt2,
                    self_conjunctions=False,
                    otypes=[otype.MASKED, otype.PRIMARY],
                ),
            ],
            conj_thresh=1.0,
        )

        # Verify there's no conjunctions.
        self.assertEqual(len(cr_cross.conjunctions), 0)

        # Same test with slightly different conj det interval.
        pt1 = polytree(
            pj1, conj_det_interval=conj_det_interval + conj_det_interval / 10.0
        )
        cr_cross = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(
                    pj=pj2,
                    pt=pt2,
                    self_conjunctions=False,
                    otypes=[otype.MASKED, otype.PRIMARY],
                ),
            ],
            conj_thresh=1.0,
        )
        self.assertEqual(len(cr_cross.conjunctions), 0)

        # Do the same with multiple empty trajs too.
        pj2 = polyjectory(
            [_planar_circ_tcs, tcs_no_steps, tcs_no_steps, tcs_no_steps],
            [_planar_circ_times, [], [], []],
            [0, 0, 0, 0],
        )
        pt2 = polytree(pj2, conj_det_interval=conj_det_interval)

        cr_cross = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(
                    pj=pj2,
                    pt=pt2,
                    self_conjunctions=False,
                    otypes=[otype.MASKED, otype.PRIMARY, otype.PRIMARY, otype.PRIMARY],
                ),
            ],
            conj_thresh=1.0,
        )

        self.assertEqual(len(cr_cross.conjunctions), 0)

        pj2 = polyjectory(
            [tcs_no_steps, tcs_no_steps, tcs_no_steps, _planar_circ_tcs],
            [[], [], [], _planar_circ_times],
            [0, 0, 0, 0],
        )
        pt2 = polytree(pj2, conj_det_interval=conj_det_interval)

        cr_cross = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(
                    pj=pj2,
                    pt=pt2,
                    self_conjunctions=False,
                    otypes=[otype.PRIMARY, otype.PRIMARY, otype.PRIMARY, otype.MASKED],
                ),
            ],
            conj_thresh=1.0,
        )

        self.assertEqual(len(cr_cross.conjunctions), 0)

    def test_nonzero_tbegin(self):
        # Simple test for trajectories beginning at different times.
        from .. import polyjectory, polytree, catalog, detect_conjunctions
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times

        _planar_circ_times1 = _planar_circ_times
        _planar_circ_times2 = _planar_circ_times + 1.0

        pj1 = polyjectory([_planar_circ_tcs], [_planar_circ_times1], [0])
        pj2 = polyjectory([_planar_circ_tcs], [_planar_circ_times2], [0])

        # Run the test for several conjunction detection intervals.
        for conj_det_interval in [0.01, 0.1, 0.5, 2.0, 5.0, 7.0, 10.0]:
            pt1 = polytree(pj1, conj_det_interval=conj_det_interval)
            pt2 = polytree(pj2, conj_det_interval=conj_det_interval)

            cr_cross = detect_conjunctions(
                [
                    catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                    catalog(pj=pj2, pt=pt2, self_conjunctions=False),
                ],
                conj_thresh=0.1,
            )

            # No conjunctions expected.
            self.assertEqual(len(cr_cross.conjunctions), 0)

            # Do the same test with slightly different conj det interval.
            pt1 = polytree(
                pj1, conj_det_interval=conj_det_interval + conj_det_interval / 10.0
            )
            cr_cross = detect_conjunctions(
                [
                    catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                    catalog(pj=pj2, pt=pt2, self_conjunctions=False),
                ],
                conj_thresh=0.1,
            )
            self.assertEqual(len(cr_cross.conjunctions), 0)

    def test_cd_begin_end(self):
        # Test to check for correctness with trajectories
        # beginning and ending within a conjunction step.
        from .. import polyjectory, polytree, detect_conjunctions, catalog
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

        # Construct the polyjectories/polytrees.
        pj1 = polyjectory([traj_data_0], [tm_data_0], [0])
        pj2 = polyjectory([traj_data_1], [tm_data_1], [0])
        pt1 = polytree(pj=pj1, conj_det_interval=2.0 / 3.0)
        pt2 = polytree(pj=pj2, conj_det_interval=2.0 / 3.0)

        # Run conjunction detection.
        cj = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(pj=pj2, pt=pt2, self_conjunctions=False),
            ],
            conj_thresh=1e-6,
        )

        # We must not detect any conjunction because the conjunection happens
        # when there is no data for both trajectories.
        self.assertEqual(len(cj.conjunctions), 0)

        # Repeat the same test with slightly different conj det interval.
        pt1 = polytree(pj=pj1, conj_det_interval=2.0 / 3.0 + 0.1)
        cj = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(pj=pj2, pt=pt2, self_conjunctions=False),
            ],
            conj_thresh=1e-6,
        )
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

        pj1 = polyjectory([traj_data_0], [tm_data_0], [0])
        pj2 = polyjectory([traj_data_1], [tm_data_1], [0])
        pt1 = polytree(pj=pj1, conj_det_interval=2.0 / 3.0)
        pt2 = polytree(pj=pj2, conj_det_interval=2.0 / 3.0)

        cj = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(pj=pj2, pt=pt2, self_conjunctions=False),
            ],
            conj_thresh=1e-6,
        )

        # Here we must detect the conjunction.
        conjs = cj.conjunctions
        self.assertEqual(len(conjs), 1)
        self.assertTrue(np.all(conjs["i"] == 0))
        self.assertTrue(np.all(conjs["j"] == 0))
        self.assertTrue(np.all(conjs["cat_i"] == 0))
        self.assertTrue(np.all(conjs["cat_j"] == 1))
        self.assertAlmostEqual(conjs["tca"][0], 1.0, places=15)
        self.assertAlmostEqual(conjs["dca"][0], 0.0, delta=1e-15)
        self.assertTrue(np.allclose(conjs["ri"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["rj"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vi"][0], [-1, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vj"][0], [1, 0, 0], atol=1e-15, rtol=0.0))

        # Repeat the same test with slightly different conj det interval.
        pt1 = polytree(pj=pj1, conj_det_interval=2.0 / 3.0 - 0.1)
        cj = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(pj=pj2, pt=pt2, self_conjunctions=False),
            ],
            conj_thresh=1e-6,
        )
        conjs = cj.conjunctions
        self.assertEqual(len(conjs), 1)
        self.assertTrue(np.all(conjs["i"] == 0))
        self.assertTrue(np.all(conjs["j"] == 0))
        self.assertTrue(np.all(conjs["cat_i"] == 0))
        self.assertTrue(np.all(conjs["cat_j"] == 1))
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

        pj1 = polyjectory([traj_data_0], [tm_data_0], [0])
        pj2 = polyjectory([traj_data_1], [tm_data_1], [0])
        pt1 = polytree(pj=pj1, conj_det_interval=2.0 / 3.0)
        pt2 = polytree(pj=pj2, conj_det_interval=2.0 / 3.0)

        cj = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(pj=pj2, pt=pt2, self_conjunctions=False),
            ],
            conj_thresh=1e-6,
        )

        self.assertEqual(len(cj.conjunctions), 0)

        # Repeat the same test with slightly different conj det interval.
        pt2 = polytree(pj=pj2, conj_det_interval=2.0 / 3.0 + 0.1)
        cj = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(pj=pj2, pt=pt2, self_conjunctions=False),
            ],
            conj_thresh=1e-6,
        )
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

        pj1 = polyjectory([traj_data_0], [tm_data_0], [0])
        pj2 = polyjectory([traj_data_1], [tm_data_1], [0])
        pt1 = polytree(pj=pj1, conj_det_interval=2.0 / 3.0)
        pt2 = polytree(pj=pj2, conj_det_interval=2.0 / 3.0)

        cj = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(pj=pj2, pt=pt2, self_conjunctions=False),
            ],
            conj_thresh=1e-6,
        )

        conjs = cj.conjunctions
        self.assertEqual(len(conjs), 1)
        self.assertTrue(np.all(conjs["i"] == 0))
        self.assertTrue(np.all(conjs["j"] == 0))
        self.assertTrue(np.all(conjs["cat_i"] == 0))
        self.assertTrue(np.all(conjs["cat_j"] == 1))
        self.assertAlmostEqual(conjs["tca"][0], 1.0, places=15)
        self.assertAlmostEqual(conjs["dca"][0], 0.0, delta=1e-15)
        self.assertTrue(np.allclose(conjs["ri"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["rj"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vi"][0], [-1, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vj"][0], [1, 0, 0], atol=1e-15, rtol=0.0))

        # Repeat the same test with slightly different conj det interval.
        pt2 = polytree(pj=pj2, conj_det_interval=2.0 / 3.0 + 0.1)
        cj = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(pj=pj2, pt=pt2, self_conjunctions=False),
            ],
            conj_thresh=1e-6,
        )
        conjs = cj.conjunctions
        self.assertEqual(len(conjs), 1)
        self.assertTrue(np.all(conjs["i"] == 0))
        self.assertTrue(np.all(conjs["j"] == 0))
        self.assertTrue(np.all(conjs["cat_i"] == 0))
        self.assertTrue(np.all(conjs["cat_j"] == 1))
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

        pj1 = polyjectory([traj_data_0], [tm_data_0], [0])
        pj2 = polyjectory([traj_data_1], [tm_data_1], [0])
        pt1 = polytree(pj=pj1, conj_det_interval=2.0 / 3.0)
        pt2 = polytree(pj=pj2, conj_det_interval=2.0 / 3.0)

        cj = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(pj=pj2, pt=pt2, self_conjunctions=False),
            ],
            conj_thresh=1e-6,
        )

        self.assertEqual(len(cj.conjunctions), 0)

        # Repeat the same test with slightly different conj det interval.
        pt2 = polytree(pj=pj2, conj_det_interval=2.0 / 3.0 + 0.1)
        cj = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(pj=pj2, pt=pt2, self_conjunctions=False),
            ],
            conj_thresh=1e-6,
        )
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

        pj1 = polyjectory([traj_data_0], [tm_data_0], [0])
        pj2 = polyjectory([traj_data_1], [tm_data_1], [0])
        pt1 = polytree(pj=pj1, conj_det_interval=2.0 / 3.0)
        pt2 = polytree(pj=pj2, conj_det_interval=2.0 / 3.0)

        cj = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(pj=pj2, pt=pt2, self_conjunctions=False),
            ],
            conj_thresh=1e-6,
        )

        conjs = cj.conjunctions
        # NOTE: we assert >=1 conjunctions are detected,
        # as here we are at the limits of the numerics and a second
        # spurious conjunction might be detected.
        self.assertGreaterEqual(len(conjs), 1)
        self.assertTrue(np.all(conjs["i"] == 0))
        self.assertTrue(np.all(conjs["j"] == 0))
        self.assertTrue(np.all(conjs["cat_i"] == 0))
        self.assertTrue(np.all(conjs["cat_j"] == 1))
        self.assertAlmostEqual(conjs["tca"][0], 1.0, places=15)
        self.assertAlmostEqual(conjs["dca"][0], 0.0, delta=1e-15)
        self.assertTrue(np.allclose(conjs["ri"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["rj"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vi"][0], [-1, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vj"][0], [1, 0, 0], atol=1e-15, rtol=0.0))

        # Repeat the same test with slightly different conj det interval.
        pt2 = polytree(pj=pj2, conj_det_interval=2.0 / 3.0 + 0.1)
        cj = detect_conjunctions(
            [
                catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                catalog(pj=pj2, pt=pt2, self_conjunctions=False),
            ],
            conj_thresh=1e-6,
        )
        conjs = cj.conjunctions
        self.assertGreaterEqual(len(conjs), 1)
        self.assertTrue(np.all(conjs["i"] == 0))
        self.assertTrue(np.all(conjs["j"] == 0))
        self.assertTrue(np.all(conjs["cat_i"] == 0))
        self.assertTrue(np.all(conjs["cat_j"] == 1))
        self.assertAlmostEqual(conjs["tca"][0], 1.0, places=15)
        self.assertAlmostEqual(conjs["dca"][0], 0.0, delta=1e-15)
        self.assertTrue(np.allclose(conjs["ri"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["rj"][0], [0, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vi"][0], [-1, 0, 0], atol=1e-15, rtol=0.0))
        self.assertTrue(np.allclose(conjs["vj"][0], [1, 0, 0], atol=1e-15, rtol=0.0))

    def test_nonoverlapping_times(self):
        # Simple test for trees with non-overlapping time intervals.
        from .. import polyjectory, polytree, catalog, detect_conjunctions
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times

        _planar_circ_times1 = _planar_circ_times
        _planar_circ_times2 = _planar_circ_times + 7.0

        pj1 = polyjectory([_planar_circ_tcs], [_planar_circ_times1], [0])
        pj2 = polyjectory([_planar_circ_tcs], [_planar_circ_times2], [0])

        # Run the test for several conjunction detection intervals.
        for conj_det_interval in [0.01, 0.1, 0.5, 2.0, 5.0, 7.0, 10.0]:
            pt1 = polytree(pj1, conj_det_interval=conj_det_interval)
            pt2 = polytree(pj2, conj_det_interval=conj_det_interval)

            cr_cross = detect_conjunctions(
                [
                    catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                    catalog(pj=pj2, pt=pt2, self_conjunctions=False),
                ],
                conj_thresh=0.1,
            )

            # No conjunctions expected.
            self.assertEqual(len(cr_cross.conjunctions), 0)

            # Repeat test with slightly different conj det interval.
            pt2 = polytree(
                pj2, conj_det_interval=conj_det_interval + conj_det_interval / 10.0
            )
            cr_cross = detect_conjunctions(
                [
                    catalog(pj=pj1, pt=pt1, self_conjunctions=False),
                    catalog(pj=pj2, pt=pt2, self_conjunctions=False),
                ],
                conj_thresh=0.1,
            )
            self.assertEqual(len(cr_cross.conjunctions), 0)
