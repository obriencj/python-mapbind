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


from mapbind import mapbind, objbind, funbind, takebind
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


class TestObjBind(TestCase):

    @staticmethod
    def _get_data():
        class Obj(object):
            def __init__(self):
                self.a = 100
                self.b = 200
                self.c = 300
                self.tacos = 900
                self.beer = 700

        return Obj()


    def test_present(self):
        data = self._get_data()

        a, b, c = objbind(data)
        self.assertEqual(a, data.a)
        self.assertEqual(b, data.b)
        self.assertEqual(c, data.c)

        tacos, beer = objbind(data)
        self.assertEqual(tacos, data.tacos)
        self.assertEqual(beer, data.beer)


    def test_missing(self):
        data = self._get_data()

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


class TestTakeBind(TestCase):

    def test_binding(self):

        data = iter(range(0, 999))
        a, b, c = takebind(data)
        x, y, z = takebind(data)

        self.assertEqual(a, 0)
        self.assertEqual(b, 1)
        self.assertEqual(c, 2)
        self.assertEqual(x, 3)
        self.assertEqual(y, 4)
        self.assertEqual(z, 5)


    def test_runout(self):

        data = iter(range(0, 4))

        a, b, c = takebind(data)
        self.assertEqual(a, 0)
        self.assertEqual(b, 1)
        self.assertEqual(c, 2)

        def oops():
            x, y, z = takebind(data)

        self.assertRaises(ValueError, oops)

        data = iter(range(0, 4))

        a, b, c = takebind(data)
        self.assertEqual(a, 0)
        self.assertEqual(b, 1)
        self.assertEqual(c, 2)

        x, y, z = takebind(data, None)
        self.assertEqual(x, 3)
        self.assertEqual(y, None)
        self.assertEqual(z, None)


class TestBindings(TestCase):

    def test_bad(self):
        def noop(*args, **kwds):
            pass

        def bad_data(name):
            # none of these tests should ever actually get this far!
            self.assertFalse(True)

        def bad_times():
            funbind(bad_data)

        self.assertRaises(ValueError, bad_times)

        def bad_times():
            return funbind(bad_data)

        self.assertRaises(ValueError, bad_times)

        def bad_times():
            a = funbind(bad_data)

        self.assertRaises(ValueError, bad_times)

        def bad_times():
            a, (b, c) = funbind(bad_data)

        self.assertRaises(ValueError, bad_times)

        def bad_times():
            noop(funbind(bad_data))

        self.assertRaises(ValueError, bad_times)

        def bad_times():
            noop(*funbind(bad_data))

        self.assertRaises(ValueError, bad_times)


    def test_global(self):

        accu = []
        def accumulate(name):
            accu.append(name)
            return "|%s|" % name

        global x

        a, x = funbind(accumulate)

        self.assertEqual(accu, ["a", "x"])
        self.assertEqual(a, "|a|")
        self.assertEqual(x, "|x|")
        self.assertEqual(x, globals()["x"])


#
# The end.
