# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, see
# <http://www.gnu.org/licenses/>.


from mapbind import mapbind
from unittest import TestCase


class TestMapBind(TestCase):

    def test_simple(self):
        data = {"tacos": 900, "beer": 700, "a": 100, "b": 200, "c": 300, }

        a, b, c = mapbind(data)
        self.assertEqual(a, data["a"])
        self.assertEqual(b, data["b"])
        self.assertEqual(c, data["c"])

        tacos, beer = mapbind(data)
        self.assertEqual(tacos, data["tacos"])
        self.assertEqual(beer, data["beer"])

        def bad_times():
            a, b, c, d = mapbind(data)

        self.assertRaises(KeyError, bad_times)


#
# The end.
