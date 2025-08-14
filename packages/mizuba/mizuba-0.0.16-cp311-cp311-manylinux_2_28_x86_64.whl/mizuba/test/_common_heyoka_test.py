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


# Class to factor out common test code involving heyoka.
class _common_heyoka_test(_ut.TestCase):
    def _make_kep_ta(self, G, M, N):
        import heyoka as hy
        import numpy as np
        from copy import copy

        # The original dynamical model - Keplerian centre of attraction.
        orig_dyn = hy.model.fixed_centres(G, [M], [[0.0, 0.0, 0.0]])
        orig_vars = ["x", "y", "z", "vx", "vy", "vz"]

        # Create a dynamical model corresponding to N objects
        # non interacting with each other, attracted by the Keplerian
        # Earth. Also add an equation for the distance from the centre
        # of attraction.
        var_list = []
        dyn = []
        for i in range(N):
            new_vars = [hy.expression(_ + f"_{i}") for _ in orig_vars]
            new_vars += [hy.make_vars(f"r_{i}")]
            xi, yi, zi, vxi, vyi, vzi, ri = new_vars

            dsub = dict(zip(orig_vars, new_vars))
            new_dyn = hy.subs([_[1] for _ in orig_dyn], dsub)
            new_dyn += [(xi * vxi + yi * vyi + zi * vzi) / ri]

            var_list += new_vars
            dyn += new_dyn

        # List of conjunctions detected by heyoka.
        hy_conj_list = []

        # The conjunction event callback.
        class conj_cb:
            def __init__(self, i, j):
                self.i = i
                self.j = j

            def __call__(self, ta, time, d_sgn):
                # Compute the state of the system
                # at the point of minimum distance.
                # between objects i and j.
                ta.update_d_output(time)

                # Extract the state vectors
                # for objects i and j.
                st = ta.d_output.reshape(-1, 7)
                ri = st[self.i, 0:3]
                rj = st[self.j, 0:3]
                vi = st[self.i, 3:6]
                vj = st[self.j, 3:6]

                # Append to hy_conj_list:
                # - tca and dca,
                # - the indices of the objects,
                # - the state vectors.
                hy_conj_list.append(
                    (
                        0,
                        0,
                        self.i,
                        self.j,
                        time,
                        np.linalg.norm(ri - rj),
                        copy(ri),
                        copy(vi),
                        copy(rj),
                        copy(vj),
                    )
                )

        # Create the events for detecting conjunctions.
        ev_list = []
        svs_arr = np.array(var_list).reshape((-1, 7))
        for i in range(N):
            xi, yi, zi, vxi, vyi, vzi = svs_arr[i, :6]
            for j in range(i + 1, N):
                xj, yj, zj, vxj, vyj, vzj = svs_arr[j, :6]

                # The event equation.
                eq = (
                    (xi - xj) * (vxi - vxj)
                    + (yi - yj) * (vyi - vyj)
                    + (zi - zj) * (vzi - vzj)
                )

                # Create the event.
                ev_list.append(
                    hy.nt_event(
                        eq, conj_cb(i, j), direction=hy.event_direction.positive
                    )
                )

        # Build the integrator.
        ta = hy.taylor_adaptive(
            list(zip(var_list, dyn)), compact_mode=True, nt_events=ev_list
        )

        return ta, hy_conj_list
