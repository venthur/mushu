# test_triggerprecision.py
# Copyright (C) 2013  Bastian Venthur
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


from __future__ import division
import time
import unittest


class TestTimerPrecision(unittest.TestCase):

    def test_precision(self):
        """The precision of the timer must be at least 10us."""
        # collect as many timestamps as possible in 1 second, remove the
        # duplicates and count the number of elements
        times = []
        t_start = time.time()
        while time.time() < t_start + 1:
            times.append(time.time())
        # remove duplicates
        times = list(set(times))
        resolution = (max(times) - min(times)) / len(times)
        self.assertLessEqual(resolution, 10*1e-6)


if __name__ == '__main__':
    unittest.main()
