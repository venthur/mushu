# __init__.py
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


"""
This package contains the low-level drivers for various amplifiers.

As a user, you'll probably not deal with them directly but with their decorated
counterparts via :func:`libmushu.__init__.get_amp`.

If you want to use the low level drivers directly you can use it like this::

    from libmushu.driver.randomamp import RandomAmp
    amp = RandomAmp()

TODO: Add a 'writing your own drivers' section or tutorial.

"""
