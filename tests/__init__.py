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


from mapbind import mapbind, objbind, funbind
from unittest import TestCase


class TestMapBind(TestCase):

    def test_present(self):
        data = {"tacos": 900, "beer": 700, "a": 100, "b": 200, "c": 300, }

        a, b, c = mapbind(data)
        self.assertEqual(a, data["a"])
        self.assertEqual(b, data["b"])
        self.assertEqual(c, data["c"])

        tacos, beer = mapbind(data)
        self.assertEqual(tacos, data["tacos"])
        self.assertEqual(beer, data["beer"])


    def test_missing(self):
        data = {"tacos": 900, "beer": 700, "a": 100, "b": 200, "c": 300, }

        def bad_times():
            a, b, c, d = mapbind(data)

        self.assertRaises(KeyError, bad_times)

        a, b, c, d, tacos, beer = mapbind(data, "wut")
        self.assertEqual(a, 100)
        self.assertEqual(b, 200)
        self.assertEqual(c, 300)
        self.assertEqual(d, "wut")
        self.assertEqual(tacos, 900)
        self.assertEqual(beer, 700)


    def test_bad_binding(self):
        data = {"tacos": 900, "beer": 700, "a": 100, "b": 200, "c": 300, }

        def noop(*args, **kwds):
            pass

        def bad_times():
            mapbind(data)

        self.assertRaises(ValueError, bad_times)

        def bad_times():
            return mapbind(data)

        self.assertRaises(ValueError, bad_times)

        def bad_times():
            a = mapbind(data)

        self.assertRaises(ValueError, bad_times)

        def bad_times():
            noop(mapbind(data))

        self.assertRaises(ValueError, bad_times)

        def bad_times():
            noop(*mapbind(data))

        self.assertRaises(ValueError, bad_times)


class TestObjBind(TestCase):

    def test_present(self):
        class Obj(object):
            def __init__(self):
                self.a = 100
                self.b = 200
                self.c = 300
                self.tacos = 900
                self.beer = 700

        data = Obj()

        a, b, c = objbind(data)
        self.assertEqual(a, data.a)
        self.assertEqual(b, data.b)
        self.assertEqual(c, data.c)

        tacos, beer = objbind(data)
        self.assertEqual(tacos, data.tacos)
        self.assertEqual(beer, data.beer)


    def test_missing(self):
        class Obj(object):
            def __init__(self):
                self.a = 100
                self.b = 200
                self.c = 300
                self.tacos = 900
                self.beer = 700

        data = Obj()

        def bad_times():
            a, b, c, d = objbind(data)

        self.assertRaises(AttributeError, bad_times)

        a, b, c, d, tacos, beer = objbind(data, "wut")
        self.assertEqual(a, 100)
        self.assertEqual(b, 200)
        self.assertEqual(c, 300)
        self.assertEqual(d, "wut")
        self.assertEqual(tacos, 900)
        self.assertEqual(beer, 700)


class TestFunBind(TestCase):

    def test_binding(self):

        accu = []

        def accumulate(key):
            accu.append(key)
            return "|%s|" % key

        a, b, c = funbind(accumulate)
        self.assertEqual(a, "|a|")
        self.assertEqual(b, "|b|")
        self.assertEqual(c, "|c|")
        self.assertEqual(accu, ["a", "b", "c"])


    def test_raises(self):

        accu = []

        def accumulate(key):
            if key == "fail":
                raise Exception("noooo")
            else:
                accu.append(key)
                return "|%s|" % key

        a, b, c = funbind(accumulate)
        self.assertEqual(a, "|a|")
        self.assertEqual(b, "|b|")
        self.assertEqual(c, "|c|")
        self.assertEqual(accu, ["a", "b", "c"])

        accu = []

        try:
            x, fail, z = funbind(accumulate)
        except Exception:
            pass
        else:
            self.assertTrue(False)

        self.assertEqual(accu, ["x"])

        try:
            self.assertFalse(x)
            self.assertTrue(False)
        except NameError:
            pass
        except:
            self.assertTrue(False)
        else:
            self.assertTrue(False)

        try:
            self.assertFalse(fail)
            self.assertTrue(False)
        except NameError:
            pass
        except:
            self.assertTrue(False)
        else:
            self.assertTrue(False)

        try:
            self.assertFalse(z)
            self.assertTrue(False)
        except NameError:
            pass
        except:
            self.assertTrue(False)
        else:
            self.assertTrue(False)


#
# The end.
