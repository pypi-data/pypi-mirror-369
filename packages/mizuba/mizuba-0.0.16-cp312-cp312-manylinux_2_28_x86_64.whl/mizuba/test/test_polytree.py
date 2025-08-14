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


class polytree_test_case(_sgp4_satlist_setup):
    # Helper to verify that the aabbs are consistent
    # with the positions of the objects computed via
    # polynomial evaluation.
    def _verify_polytree_aabbs(self, c, pj, rng):
        import numpy as np

        # For every conjunction step, pick random times within,
        # evaluate the polyjectory at the corresponding times and
        # assert that the positions are within the aabbs.
        for cd_idx, end_time in enumerate(c.cd_end_times):
            begin_time = 0.0 if cd_idx == 0 else c.cd_end_times[cd_idx - 1]

            # Pick 5 random times.
            random_times = rng.uniform(begin_time, end_time, (5,))

            # Fetch the global aabb for this conjunction step.
            global_lb = c.aabbs[cd_idx, pj.n_objs, 0]
            global_ub = c.aabbs[cd_idx, pj.n_objs, 1]

            if not np.isfinite(global_lb[0]):
                # Non-finite value detected in the global AABB.

                # All global AABB values must be infinity.
                self.assertTrue(np.all(np.isinf(global_lb)))
                self.assertTrue(np.all(np.isinf(global_ub)))

                # The AABBs of all objects must be infinities.
                self.assertTrue(
                    all(
                        np.all(np.isinf(c.aabbs[cd_idx, obj_idx]))
                        for obj_idx in range(pj.n_objs)
                    )
                )

                # Continue to the next conjunction step.
                continue

            # Iterate over all objects.
            for obj_idx in range(pj.n_objs):
                # Fetch the polyjectory data for the current object.
                traj, traj_times, status = pj[obj_idx]

                # Fetch the AABB of the object.
                aabb = c.aabbs[cd_idx, obj_idx]

                # If there is no trajectory data for the current
                # object, just check that its aabb is infinite.
                if traj.shape[0] == 0:
                    self.assertTrue(np.all(np.isinf(aabb)))
                    continue

                if begin_time >= traj_times[-1]:
                    # The trajectory data for the current object
                    # ends before the beginning of the current conjunction
                    # step. Skip the current object and assert that its
                    # aabb is infinite.
                    self.assertTrue(np.all(np.isinf(aabb)))
                    continue
                elif traj_times[0] >= end_time:
                    # The trajectory data for the current object
                    # begins at or after the end time of the conjunction
                    # step. Skip the current object and assert that its
                    # aabb is infinite.
                    self.assertTrue(np.all(np.isinf(aabb)))
                    continue
                else:
                    # The time data for the current object overlaps
                    # with the conjunction step. The aabb must be finite.
                    self.assertTrue(np.all(np.isfinite(aabb)))

                # The aabb must be included in the global one.
                self.assertTrue(np.all(aabb[0] >= global_lb))
                self.assertTrue(np.all(aabb[1] <= global_ub))

                # Iterate over the random times.
                for time in random_times:
                    # Look for the first trajectory time data point *after* 'time'.
                    step_idx = np.searchsorted(traj_times, time, side="right")

                    # Skip the current 'time' if it is past the end of
                    # trajectory data.
                    if step_idx == len(traj_times):
                        continue

                    # Skip the current 'time' if it is before the beginning
                    # of trajectory data.
                    if step_idx == 0:
                        continue

                    # Fetch the polynomials for all state variables
                    # in the trajectory step.
                    # NOTE: step_idx - 1 because we need the
                    # trajectory step that ends at traj_times[step_idx].
                    traj_polys = traj[step_idx - 1]

                    # Compute the poly evaluation interval.
                    # This is the time elapsed since the beginning
                    # of the trajectory step.
                    h = time - traj_times[step_idx - 1]

                    # Evaluate the polynomials and check that
                    # the results fit in the aabb.
                    for coord_idx, aabb_idx in zip([0, 1, 2, 6], range(4)):
                        pval = np.polyval(traj_polys[::-1, coord_idx], h)
                        # NOTE: I am not sure that these checks are 100% airtight.
                        #
                        # On the one hand, in the computation of the AABBs we add some slack in the conversion from double
                        # to float, which can absorb some of the truncation error arising when evaluating the
                        # trajectory polynomials.
                        #
                        # On the other hand, it is probably not mathematically guaranteed that the checks will hold for all
                        # possible inputs. That is, we could in principle have a combination of random times and trajectory
                        # polynomials such that the next two assertion fail due to rounding errors. This seems rather unlikely,
                        # but something to keep in mind.
                        self.assertGreater(pval, aabb[0][aabb_idx])
                        self.assertLess(pval, aabb[1][aabb_idx])

    def test_basics(self):
        import sys
        from .. import polytree, polyjectory
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times
        import numpy as np

        # Test error handling on construction.
        pj = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])

        with self.assertRaises(ValueError) as cm:
            polytree(pj, conj_det_interval=0.0)
        self.assertTrue(
            "The conjunction detection interval must be finite and positive,"
            in str(cm.exception)
        )

        with self.assertRaises(ValueError) as cm:
            polytree(pj, conj_det_interval=float("nan"))
        self.assertTrue(
            "The conjunction detection interval must be finite and positive,"
            in str(cm.exception)
        )

        # Test accessors.
        pt = polytree(pj, conj_det_interval=0.1)

        self.assertEqual(pt.n_cd_steps, len(pt.cd_end_times))
        self.assertTrue(isinstance(pt.bvh_node, np.dtype))
        self.assertEqual(pt.conj_det_interval, 0.1)
        self.assertEqual(pt.n_objs, pj.n_objs)
        self.assertEqual(pt.maxT, pj.maxT)
        self.assertEqual(pt.cd_end_times[-1], pt.maxT)
        self.assertEqual(pt.epoch, pj.epoch)

        # aabbs.
        rc = sys.getrefcount(pt)
        aabbs = pt.aabbs
        self.assertEqual(sys.getrefcount(pt), rc + 1)
        with self.assertRaises(ValueError) as cm:
            aabbs[:] = aabbs
        with self.assertRaises(AttributeError) as cm:
            pt.aabbs = aabbs

        # cd_end_times.
        rc = sys.getrefcount(pt)
        cd_end_times = pt.cd_end_times
        self.assertEqual(sys.getrefcount(pt), rc + 1)
        with self.assertRaises(ValueError) as cm:
            cd_end_times[:] = cd_end_times
        with self.assertRaises(AttributeError) as cm:
            pt.cd_end_times = cd_end_times

        # srt_aabbs.
        rc = sys.getrefcount(pt)
        srt_aabbs = pt.srt_aabbs
        self.assertEqual(sys.getrefcount(pt), rc + 1)
        with self.assertRaises(ValueError) as cm:
            srt_aabbs[:] = srt_aabbs
        with self.assertRaises(AttributeError) as cm:
            pt.srt_aabbs = srt_aabbs

        # mcodes.
        rc = sys.getrefcount(pt)
        mcodes = pt.mcodes
        self.assertEqual(sys.getrefcount(pt), rc + 1)
        with self.assertRaises(ValueError) as cm:
            mcodes[:] = mcodes
        with self.assertRaises(AttributeError) as cm:
            pt.mcodes = mcodes

        # srt_mcodes.
        rc = sys.getrefcount(pt)
        srt_mcodes = pt.srt_mcodes
        self.assertEqual(sys.getrefcount(pt), rc + 1)
        with self.assertRaises(ValueError) as cm:
            srt_mcodes[:] = srt_mcodes
        with self.assertRaises(AttributeError) as cm:
            pt.srt_mcodes = srt_mcodes

        # srt_idx.
        rc = sys.getrefcount(pt)
        srt_idx = pt.srt_idx
        self.assertEqual(sys.getrefcount(pt), rc + 1)
        with self.assertRaises(ValueError) as cm:
            srt_idx[:] = srt_idx
        with self.assertRaises(AttributeError) as cm:
            pt.srt_idx = srt_idx

        pt.hint_release()

    def test_main(self):
        import numpy as np
        from .. import (
            polytree,
            polyjectory,
        )
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times

        # Deterministic seeding.
        rng = np.random.default_rng(42)

        # Single planar circular orbit case.
        pj = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])

        # Run the test for several conjunction detection intervals.
        for conj_det_interval in [0.01, 0.1, 0.5, 2.0, 5.0, 7.0]:
            pt = polytree(pj, conj_det_interval=conj_det_interval)

            # Shape checks.
            self.assertEqual(pt.aabbs.shape[0], pt.cd_end_times.shape[0])
            self.assertEqual(pt.srt_aabbs.shape[0], pt.cd_end_times.shape[0])
            self.assertEqual(pt.srt_aabbs.shape, pt.aabbs.shape)
            self.assertEqual(pt.mcodes.shape[0], pt.cd_end_times.shape[0])
            self.assertEqual(pt.srt_mcodes.shape[0], pt.cd_end_times.shape[0])
            self.assertEqual(pt.srt_idx.shape[0], pt.cd_end_times.shape[0])

            # The conjunction detection end time must coincide
            # with the trajectory end time and maxT.
            self.assertEqual(pt.cd_end_times[-1], pj[0][1][-1])
            self.assertEqual(pt.cd_end_times[-1], pt.maxT)

            # The global aabbs must all coincide
            # exactly with the only object's aabbs.
            self.assertTrue(np.all(pt.aabbs[:, 0] == pt.aabbs[:, 1]))
            # With only one object, aabbs and srt_aabbs must be identical.
            self.assertTrue(np.all(pt.aabbs == pt.srt_aabbs))

            # In the z and r coordinates, all aabbs
            # should be of size circa 0.1.
            self.assertTrue(np.all(pt.aabbs[:, 0, 0, 2] >= -0.05001))
            self.assertTrue(np.all(pt.aabbs[:, 0, 1, 2] <= 0.05001))

            self.assertTrue(np.all(pt.aabbs[:, 0, 0, 3] >= 1 - 0.05001))
            self.assertTrue(np.all(pt.aabbs[:, 0, 1, 3] <= 1 + 0.05001))

            # Verify the aabbs.
            self._verify_polytree_aabbs(pt, pj, rng)

            pt.hint_release()

        # Test that if we specify a conjunction detection interval
        # larger than maxT, the time data in the polytree object
        # is correctly clamped.
        pt = polytree(pj, conj_det_interval=42.0)
        self.assertEqual(pt.n_cd_steps, 1)
        self.assertEqual(pt.cd_end_times[0], pj[0][1][-1])
        self.assertEqual(pt.cd_end_times[0], pt.maxT)

        # Run the sgp4 tests, if possible.
        if not hasattr(type(self), "sparse_sat_list"):
            return

        from .. import make_sgp4_polyjectory

        # Use the sparse satellite list.
        sat_list = self.sparse_sat_list

        begin_jd = 2460496.5

        # Build the polyjectory.
        pt = make_sgp4_polyjectory(
            sat_list, begin_jd, begin_jd + 0.25, exit_radius=12000.0
        )[0]
        tot_n_objs = pt.n_objs

        # Build the polytree object.
        c = polytree(pt, conj_det_interval=1.0 / 1440.0)

        # Verify the aabbs.
        self._verify_polytree_aabbs(c, pt, rng)

        # Shape checks.
        self.assertEqual(c.aabbs.shape, c.srt_aabbs.shape)
        self.assertEqual(c.mcodes.shape, c.srt_mcodes.shape)
        self.assertEqual(c.srt_idx.shape, (c.n_cd_steps, pt.n_objs))

        # The global aabbs must be the same in srt_aabbs.
        self.assertTrue(
            np.all(c.aabbs[:, pt.n_objs, :, :] == c.srt_aabbs[:, pt.n_objs, :, :])
        )

        # The individual aabbs for the objects will differ.
        self.assertFalse(
            np.all(c.aabbs[:, : pt.n_objs, :, :] == c.srt_aabbs[:, : pt.n_objs, :, :])
        )

        # The morton codes won't be sorted.
        self.assertFalse(np.all(np.diff(c.mcodes.astype(object)) >= 0))

        # The sorted morton codes must be sorted.
        self.assertTrue(np.all(np.diff(c.srt_mcodes.astype(object)) >= 0))

        # srt_idx is not sorted.
        self.assertFalse(np.all(np.diff(c.srt_idx.astype(object)) >= 0))

        # Indexing into aabbs and mcodes via srt_idx must produce
        # srt_abbs and srt_mcodes.
        for cd_idx in range(c.n_cd_steps):
            self.assertEqual(sorted(c.srt_idx[cd_idx]), list(range(pt.n_objs)))

            self.assertTrue(
                np.all(
                    c.aabbs[cd_idx, c.srt_idx[cd_idx], :, :]
                    == c.srt_aabbs[cd_idx, : pt.n_objs, :, :]
                )
            )

            self.assertTrue(
                np.all(c.mcodes[cd_idx, c.srt_idx[cd_idx]] == c.srt_mcodes[cd_idx])
            )

        # The exiting satellite's trajectory data terminates
        # early. After termination, the morton codes must be -1.

        # Fetch all the aabbs of the exiting satellite.
        exit_aabbs = c.aabbs[:, self.exiting_idx, :, :]

        # Check that not all are finite.
        self.assertFalse(np.all(np.isfinite(exit_aabbs)))

        # Compute the indices of the conjunction steps
        # in which infinite aabbs show up.
        inf_idx = np.any(np.isinf(exit_aabbs), axis=(1, 2)).nonzero()[0]

        # Check the Morton codes.
        self.assertTrue(np.all(c.mcodes[inf_idx, self.exiting_idx] == ((1 << 64) - 1)))

        # Similarly, the number of objects reported in the root
        # node of the bvh trees must be tot_n_objs - 2.
        # NOTE: -3 (rather than -1) because 2 other satellites generated
        # infinite aabbs.
        for idx in inf_idx:
            t = c.get_bvh_tree(idx)
            self.assertEqual(t[0]["end"] - t[0]["begin"], tot_n_objs - 3)

    def test_tmpdir(self):
        # A test checking custom setting for tmpdir in the constructors.
        import tempfile
        from pathlib import Path
        from .. import polytree, polyjectory, set_tmpdir, get_tmpdir
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times

        # Single planar circular orbit case.
        pj = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdir = Path(tmpdirname)

            # NOTE: this checks that the dir is empty.
            self.assertTrue(not any(tmpdir.iterdir()))

            c = polytree(pj, conj_det_interval=0.01, tmpdir=tmpdir)

            self.assertTrue(any(tmpdir.iterdir()))

            del c

        # A test to check that a custom tmpdir overrides
        # the global tmpdir.
        orig_global_tmpdir = get_tmpdir()
        set_tmpdir(__file__)

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdir = Path(tmpdirname)

            # NOTE: this checks that the dir is empty.
            self.assertTrue(not any(tmpdir.iterdir()))

            c = polytree(pj, conj_det_interval=0.01, tmpdir=tmpdir)

            self.assertTrue(any(tmpdir.iterdir()))

            del c

        # Restore the original global temp dir.
        set_tmpdir(orig_global_tmpdir)

        # Check that an empty tmpdir is interpreted as if not provided.
        # NOTE: here we only check the lack of throwing.
        _c = polytree(pj, conj_det_interval=0.01, tmpdir="")

    def test_zero_aabbs(self):
        # Test to check behaviour with aabbs of zero size.
        import numpy as np
        from .. import polytree, polyjectory

        # Trajectory data for a single step.
        tdata = np.zeros((7, 6))
        # Make the object fixed in Cartesian space with x,y,z coordinates all 1.
        tdata[:3, 0] = 1.0
        # Set the radial coordinate.
        tdata[6, 0] = np.sqrt(3.0)
        tdata = np.ascontiguousarray(tdata.transpose())

        pj = polyjectory([[tdata, tdata, tdata]], [[0.0, 1.0, 2.0, 3.0]], [0])

        c = polytree(pj, conj_det_interval=0.1)

        self.assertTrue(
            np.all(
                c.aabbs[:, :, 0, :3] == np.nextafter(np.single(1), np.single("-inf"))
            )
        )
        self.assertTrue(
            np.all(
                c.aabbs[:, :, 1, :3] == np.nextafter(np.single(1), np.single("+inf"))
            )
        )
        self.assertTrue(
            np.all(
                c.aabbs[:, :, 0, 3]
                == np.nextafter(np.single(np.sqrt(3.0)), np.single("-inf"))
            )
        )
        self.assertTrue(
            np.all(
                c.aabbs[:, :, 1, 3]
                == np.nextafter(np.single(np.sqrt(3.0)), np.single("+inf"))
            )
        )

    def test_no_traj_data(self):
        # This is a test to verify that when an object lacks
        # trajectory data it is always placed at the end of
        # the srt_* data.
        import numpy as np
        from .. import polytree, polyjectory

        # The goal here is to generate trajectory
        # data for which the aabb centre's morton code
        # is all ones (this will be tdata7). This will allow
        # us to verify that missing traj data is placed
        # after tdata7.

        # x.
        tdata0 = np.zeros((6, 7))
        tdata0[0, 0] = 1.0
        tdata1 = np.zeros((6, 7))
        tdata1[0, 0] = -1.0

        # y.
        tdata2 = np.zeros((6, 7))
        tdata2[0, 1] = 1.0
        tdata3 = np.zeros((6, 7))
        tdata3[0, 1] = -1.0

        # z.
        tdata4 = np.zeros((6, 7))
        tdata4[0, 2] = 1.0
        tdata5 = np.zeros((6, 7))
        tdata5[0, 2] = -1.0

        # Center.
        tdata6 = np.zeros((6, 7))

        # All ones.
        tdata7 = np.zeros((6, 7))
        tdata7[0:1] = 1

        # NOTE: the first 10 objects will have traj
        # data only for the first step, not the second.
        pj = polyjectory(
            [[tdata0]] * 10
            + [
                [tdata0] * 2,
                [tdata1] * 2,
                [tdata2] * 2,
                [tdata3] * 2,
                [tdata4] * 2,
                [tdata5] * 2,
                [tdata6] * 2,
                [tdata7] * 2,
            ],
            [[0.0, 1.0]] * 10 + [[0.0, 1.0, 2.0]] * 8,
            [0] * 18,
        )

        conjs = polytree(pj, 1.0)

        # Verify that at the second step all
        # inf aabbs are at the end of srt_aabbs
        # and the morton codes are all -1.
        self.assertTrue(np.all(np.isinf(conjs.aabbs[1, :10])))
        self.assertTrue(np.all(np.isinf(conjs.srt_aabbs[1, -11:-1])))
        self.assertTrue(np.all(conjs.mcodes[1, :10] == (2**64 - 1)))
        self.assertTrue(conjs.mcodes[1:, -1] == (2**64 - 1))
        self.assertTrue(np.all(conjs.srt_mcodes[1, -11:] == (2**64 - 1)))

    def test_bvh(self):
        # NOTE: most of the validation of bvh
        # trees is done within the C++ code
        # during construction in debug mode.
        # Here we instantiate several corner cases.
        import numpy as np
        from .. import polytree, polyjectory

        # Polyjectory with a single object.
        tdata = np.zeros((6, 7))
        tdata[1, :] = 0.1

        pj = polyjectory([[tdata]], [[0.0, 1.0]], [0])
        conjs = polytree(pj, 1.0)

        with self.assertRaises(IndexError) as cm:
            conjs.get_bvh_tree(1)
        self.assertTrue(
            "Cannot fetch the BVH tree for the conjunction timestep at index 1: the"
            " total number of conjunction steps is only 1" in str(cm.exception)
        )

        t = conjs.get_bvh_tree(0)
        self.assertEqual(len(t), 1)

        # Polyjectory with two identical objects.
        # This will result in exhausting all bits
        # in the morton codes for splitting.
        pj = polyjectory([[tdata], [tdata]], [[0.0, 1.0], [0.0, 1.0]], [0, 0])
        conjs = polytree(pj, 1.0)
        t = conjs.get_bvh_tree(0)
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0]["begin"], 0)
        self.assertEqual(t[0]["end"], 2)
        self.assertEqual(t[0]["left"], -1)
        self.assertEqual(t[0]["right"], -1)

        # Polyjectory in which the morton codes
        # of two objects differ at the last bit.
        # x.
        tdata0 = np.zeros((6, 7))
        tdata0[0, 0] = 1.0
        tdata1 = np.zeros((6, 7))
        tdata1[0, 0] = -1.0

        # y.
        tdata2 = np.zeros((6, 7))
        tdata2[0, 1] = 1.0
        tdata3 = np.zeros((6, 7))
        tdata3[0, 1] = -1.0

        # z.
        tdata4 = np.zeros((6, 7))
        tdata4[0, 2] = 1.0
        tdata5 = np.zeros((6, 7))
        tdata5[0, 2] = -1.0

        # Center.
        tdata6 = np.zeros((6, 7))

        # All ones.
        tdata7 = np.zeros((6, 7))
        tdata7[0, :] = 1

        # All ones but last.
        tdata8 = np.zeros((6, 7))
        tdata8[0, :] = 1
        tdata8[0, 0] = 1.0 - 2.1 / 2**16

        pj = polyjectory(
            [
                [tdata0],
                [tdata1],
                [tdata2],
                [tdata3],
                [tdata4],
                [tdata5],
                [tdata6],
                [tdata7],
                [tdata8],
            ],
            [[0.0, 1.0]] * 9,
            [0] * 9,
        )

        conjs = polytree(pj, 1.0)
        self.assertEqual(conjs.mcodes[0, -2], 2**64 - 1)
        self.assertEqual(conjs.mcodes[0, -1], 2**64 - 2)
        t = conjs.get_bvh_tree(0)
        self.assertEqual(conjs.srt_idx[0, -1], 7)
        self.assertEqual(conjs.srt_idx[0, -2], 8)

    def test_nonzero_tbegin(self):
        # Simple test for a single object
        # whose trajectory begins at t > 0.
        from .. import polytree, polyjectory
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times
        import numpy as np

        # Deterministic seeding.
        rng = np.random.default_rng(420)

        # Shift up the times.
        _planar_circ_times = _planar_circ_times + 1.0

        # Single planar circular orbit case.
        pj = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])

        # Run the test for several conjunction detection intervals.
        for conj_det_interval in [0.01, 0.1, 0.5, 2.0, 5.0, 7.0, 10.0]:
            c = polytree(pj, conj_det_interval=conj_det_interval)

            # Shape checks.
            self.assertEqual(c.aabbs.shape[0], c.cd_end_times.shape[0])
            self.assertEqual(c.srt_aabbs.shape[0], c.cd_end_times.shape[0])
            self.assertEqual(c.srt_aabbs.shape, c.aabbs.shape)
            self.assertEqual(c.mcodes.shape[0], c.cd_end_times.shape[0])
            self.assertEqual(c.srt_mcodes.shape[0], c.cd_end_times.shape[0])
            self.assertEqual(c.srt_idx.shape[0], c.cd_end_times.shape[0])

            # The conjunction detection end time must coincide
            # with the trajectory end time.
            self.assertEqual(c.cd_end_times[-1], pj[0][1][-1])

            # The global aabbs must all coincide
            # exactly with the only object's aabbs.
            self.assertTrue(np.all(c.aabbs[:, 0] == c.aabbs[:, 1]))
            # With only one object, aabbs and srt_aabbs must be identical.
            self.assertTrue(np.all(c.aabbs == c.srt_aabbs))

            # In the z and r coordinates, all aabbs should be of size circa 0.1.
            self.assertTrue(np.all(c.aabbs[:, 0, 0, 2] >= -0.05001))
            self.assertTrue(np.all(c.aabbs[:, 0, 1, 2] <= 0.05001))

            self.assertTrue(np.all(c.aabbs[:, 0, 0, 3] >= 1 - 0.05001))
            self.assertTrue(np.all(c.aabbs[:, 0, 1, 3] <= 1 + 0.05001))

            # Verify the aabbs.
            self._verify_polytree_aabbs(c, pj, rng)

    def test_persist(self):
        from .. import polyjectory, polytree
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times
        from pathlib import Path
        import tempfile

        pj = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])

        with tempfile.TemporaryDirectory() as tmpdirname:
            pt = polytree(
                pj,
                conj_det_interval=0.1,
                persist=True,
                tmpdir=Path(tmpdirname),
            )
            data_dir = pt.data_dir
            self.assertTrue(data_dir.is_dir())
            self.assertTrue(data_dir.exists())
            self.assertTrue(pt.persist)

            # NOTE: the importance of running "del pt" here is that on some platforms
            # (e.g., Windows) we need a way of enforcing the deletion of the data dir
            # **before** the removal of tmpdirname, otherwise an error will be raised.
            # "del pt" is not guaranteed to actually garbage-collect pt in all Python
            # implementations, but it should be ok in CPython at least.
            del pt

    def test_mount(self):
        from .. import polyjectory, polytree
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times
        import tempfile
        from pathlib import Path
        import numpy as np

        pj = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])

        pt = polytree(pj, conj_det_interval=0.1)

        # Check mounting a non-persistent data dir.
        with self.assertRaises(ValueError) as cm:
            polytree.mount(pt.data_dir)
        self.assertTrue(": the data is not persistent" in str(cm.exception))

        # Check mounting a non-existing data dir.
        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.assertRaises(ValueError) as cm:
                polytree.mount(Path(tmpdirname) / "foobar")
            self.assertTrue(
                "could not be canonicalised (does it exist?)" in str(cm.exception)
            )

        # Check mounting a file.
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(Path(tmpdirname) / "foobar", "wb"):
                pass

            with self.assertRaises(ValueError) as cm:
                polytree.mount(Path(tmpdirname) / "foobar")
            self.assertTrue("the path is not a directory" in str(cm.exception))

        # Check a working case.
        with tempfile.TemporaryDirectory() as tmpdirname:
            pt = polytree(
                pj,
                conj_det_interval=0.1,
                tmpdir=Path(tmpdirname),
                persist=True,
            )
            data_dir = pt.data_dir

            pt2 = polytree.mount(data_dir)

            # Compare some data.
            self.assertTrue(np.all(pt.aabbs == pt2.aabbs))
            self.assertTrue(np.all(pt.srt_aabbs == pt2.srt_aabbs))
            self.assertTrue(np.all(pt.mcodes == pt2.mcodes))
            self.assertTrue(np.all(pt.srt_mcodes == pt2.srt_mcodes))

            # NOTE: the importance of running "del pt, pt2" here is that on some platforms
            # (e.g., Windows) we need a way of enforcing the deletion of the data dirs
            # **before** the removal of tmpdirname, otherwise an error will be raised.
            # "del pt, pt2" is not guaranteed to actually garbage-collect pt and pt2 in all Python
            # implementations, but it should be ok in CPython at least.
            del pt, pt2

    def test_dir_removal(self):
        # A test checking behaviour when polyjectory data
        # is deleted before the polyjectory is garbage-collected.
        from .. import polyjectory, polytree
        from ._planar_circ import _planar_circ_tcs, _planar_circ_times
        import numpy as np
        import os
        import shutil

        pj = polyjectory([_planar_circ_tcs], [_planar_circ_times], [0])

        pt = polytree(pj, conj_det_interval=0.1)

        if os.name == "nt":
            # On Windows, we won't be able to delete the data
            # because it is "owned" by the polyjectory object.
            with self.assertRaises(Exception):
                shutil.rmtree(pt.data_dir)

            self.assertTrue(pt.data_dir.exists())

        elif os.name == "posix":
            # On posix, we assume we can remove the data.
            # The memory-mapped regions should remain valid
            # because we have not closed the file descriptors.
            shutil.rmtree(pt.data_dir)

            self.assertFalse(pt.data_dir.exists())

            pt2 = polytree(pj, conj_det_interval=0.1)

            self.assertTrue(np.all(pt.aabbs == pt2.aabbs))
            self.assertTrue(np.all(pt.srt_aabbs == pt2.srt_aabbs))
            self.assertTrue(np.all(pt.mcodes == pt2.mcodes))
            self.assertTrue(np.all(pt.srt_mcodes == pt2.srt_mcodes))
