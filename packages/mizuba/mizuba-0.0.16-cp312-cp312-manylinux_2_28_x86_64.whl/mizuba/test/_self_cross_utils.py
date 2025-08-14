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


# This is a helper class to factor out utilities used when comparing self
# and cross conjunction detection.
class _self_cross_utils(_ut.TestCase):
    # Function to verify the presence of a conjunction conj in a dataframe df.
    #
    # i and j are the indices of the conjuncting objects of conj in df. i and j may
    # be different from conj['i'] and conj['j'] as conj may originate from another
    # dataframe where the object indices are different. time_tol and posvel_tol are
    # absolute tolerances to be used when comparing floating-point data between
    # conjunctions. epoch_diff is the difference between the epochs df and conj refer to.
    #
    # Note that the identification of a conjunction cannot in general be 100% accurate,
    # due to the presence of floating-point data which may exhibit slight variations
    # depending on how the conjunction was computed.
    def _check_conj_present(self, df, i, j, conj, epoch_diff, time_tol, posvel_tol):
        import polars as pl
        import numpy as np

        # Predicate to identify the conjuncting pair (i, j) or (j, i) in df.
        pred_same_idxs = ((pl.col("i") == i) & (pl.col("j") == j)) | (
            (pl.col("j") == i) & (pl.col("i") == j)
        )

        # Predicate to identify the conjunction based on the tca, allowing for a tolerance
        # and accounting for the difference in epochs.
        close_tca = (epoch_diff + (pl.col("tca") - conj["tca"])).abs() < time_tol

        # Try to locate the conjunction in df.
        filt_df = df.filter(pred_same_idxs & close_tca)

        # Check that we found it.
        self.assertEqual(len(filt_df), 1)

        # Check dca.
        self.assertLess(
            abs(filt_df["dca"][0] - conj["dca"]),
            posvel_tol,
        )

        # Check position and velocity.
        #
        # NOTE: for these we have to branch because the i/j indices may be swapped
        # in filt_df wrt conj.
        if filt_df["i"][0] == i:
            self.assertLess(
                np.linalg.norm(filt_df["ri"][0] - conj["ri"]),
                posvel_tol,
            )
            self.assertLess(
                np.linalg.norm(filt_df["vi"][0] - conj["vi"]),
                posvel_tol,
            )
            self.assertLess(
                np.linalg.norm(filt_df["rj"][0] - conj["rj"]),
                posvel_tol,
            )
            self.assertLess(
                np.linalg.norm(filt_df["vj"][0] - conj["vj"]),
                posvel_tol,
            )
        else:
            self.assertLess(
                np.linalg.norm(filt_df["ri"][0] - conj["rj"]),
                posvel_tol,
            )
            self.assertLess(
                np.linalg.norm(filt_df["vi"][0] - conj["vj"]),
                posvel_tol,
            )
            self.assertLess(
                np.linalg.norm(filt_df["rj"][0] - conj["ri"]),
                posvel_tol,
            )
            self.assertLess(
                np.linalg.norm(filt_df["vj"][0] - conj["vi"]),
                posvel_tol,
            )

    # Helper to verify the consistency of cross conjunction detection with self conjunction detection.
    #
    # df is a conjunctions dataframe resulting from self-conjunction detection on pj/pt with conjunction
    # threshold conj_thresh. obj_idx is the index of an object in pj experiencing n_conjs conjunctions
    # (reported in df). obj_pj and obj_pt are single-object polyjectory/polytree for the object obj_idx.
    #
    # This function will perform cross-conjunction detection between pj/pt and obj_pj/obj_pt, masking out
    # obj_idx in pj/pt. It will then check that n_conjs conjunctions are detected and that they match the
    # conjunctions reported in df. tol is the tolerance used when matching conjunction data between self
    # and cross.
    def _compare_self_cross(
        self,
        df,
        pj,
        pt,
        conj_thresh,
        obj_idx,
        n_conjs,
        obj_pj,
        obj_pt,
        time_tol=1e-14,
        posvel_tol=1e-14,
    ):
        import polars as pl
        from .. import otype, detect_conjunctions, catalog
        from .._dl_utils import _dl_leq, _dl_sub
        import numpy as np

        # Run cross conjunction detection, masking out obj_idx in pj.
        otypes = [otype.PRIMARY] * pj.n_objs
        otypes[obj_idx] = otype.MASKED
        cr_cross = detect_conjunctions(
            [
                catalog(pj=pj, pt=pt, otypes=otypes, self_conjunctions=False),
                catalog(pj=obj_pj, pt=obj_pt, self_conjunctions=False),
            ],
            conj_thresh=conj_thresh,
        )
        cross_conj = cr_cross.conjunctions
        cross_conj_df = pl.DataFrame(cross_conj)

        # Check the epochs.
        self.assertTrue(_dl_leq(*cr_cross.epoch, *pj.epoch))
        self.assertTrue(_dl_leq(*cr_cross.epoch, *obj_pj.epoch))

        # The number of detected cross-conjunctions must match n_conjs.
        self.assertEqual(len(cross_conj), n_conjs)

        # Re-run cross detection with opposite catalog order.
        cr_cross_switch = detect_conjunctions(
            [
                catalog(pj=obj_pj, pt=obj_pt, self_conjunctions=False),
                catalog(pj=pj, pt=pt, otypes=otypes, self_conjunctions=False),
            ],
            conj_thresh=conj_thresh,
        )

        # Check the epoch.
        self.assertEqual(cr_cross.epoch, cr_cross_switch.epoch)

        # The tca and dca must be the same. The catalog indices too because we enforce the first
        # catalog index to be less than the second.
        self.assertTrue(
            np.all(
                cr_cross_switch.conjunctions[["cat_i", "cat_j", "tca", "dca"]]
                == cross_conj[["cat_i", "cat_j", "tca", "dca"]]
            )
        )

        # The other fields must be swapped.
        self.assertTrue(np.all(cr_cross_switch.conjunctions["i"] == cross_conj["j"]))
        self.assertTrue(np.all(cr_cross_switch.conjunctions["j"] == cross_conj["i"]))
        self.assertTrue(np.all(cr_cross_switch.conjunctions["ri"] == cross_conj["rj"]))
        self.assertTrue(np.all(cr_cross_switch.conjunctions["rj"] == cross_conj["ri"]))
        self.assertTrue(np.all(cr_cross_switch.conjunctions["vi"] == cross_conj["vj"]))
        self.assertTrue(np.all(cr_cross_switch.conjunctions["vj"] == cross_conj["vi"]))

        # Because obj_idx has been masked out in the first catalog, it cannot show
        # up as a conjuncting object for the first catalog in the results.
        filt_cdf = cross_conj_df.filter(
            (pl.col("cat_i") == 0) & (pl.col("i") == obj_idx)
        )
        self.assertEqual(len(filt_cdf), 0)

        # Compute the difference between the epoch of self and cross conjunction detection.
        epoch_diff = _dl_sub(*pj.epoch, *cr_cross.epoch)[0]

        # Run checks on the individual conjunctions.
        for cur_cross_conj in cross_conj:
            # The catalog indices must be (0, 1).
            self.assertEqual(cur_cross_conj["cat_i"], 0)
            self.assertEqual(cur_cross_conj["cat_j"], 1)

            # The conjuncting object from the second catalog (i.e., the single-object
            # catalog) must have an index of zero.
            self.assertEqual(cur_cross_conj["j"], 0)

            # Check that cur_cross_conj is present in conj_df.
            self._check_conj_present(
                df,
                cur_cross_conj["i"],
                obj_idx,
                cur_cross_conj,
                epoch_diff,
                time_tol,
                posvel_tol,
            )
