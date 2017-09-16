# Overview of python-mapbind

[![Build Status](https://travis-ci.org/obriencj/python-mapbind.svg?branch=master)](https://travis-ci.org/obriencj/python-mapbind)

Functions that inspect their calling frame to figure out how you were
going to bind their results, and returns values appropriate for the
bindings.


## Wut?

A friend gave me the idea, and I wanted to see if it was possible.
Spoilers: it totally was.


## Usage

Consider the following
```python
# if you find yourself having to write code like this
a = data["a"]
b = data["b"]
c = data["c"]

# or like this
a, b, c = map(data.get, ("a", "b", "c"))

# then stop it. Use mapbind instead:
from mapbind import mapbind
a, b, c = mapbind(data)
```

The `mapbind` function looks at its calling frame's bytecode, figures
out that the result is going to be used in an unpacking assignment,
finds the names of the variables the assignment would bind to, and
returns an iterator for the values of the given items in data with
matching keys. Supercool.

Also included are `objbind` which will find attributes on an object,
`funbind` which will call a function for each binding name, and
`takebind` which will return the right amount of values from a
sequence to fulfill the count of bindings.

```python
from mapbind import objbind

a, b, c = objbind(some_object)

assert a == some_object.a
assert b == some_object.b
assert c == some_object.c
```

```python
from mapbind import funbind

accu = []
def accumulator(name):
	accu.append(name)
	return "|%s|" % name

a, b, c = funbind(accumulator)

assert accu == ["a", "b", "c"]
assert a == "|a|"
assert b == "|b|"
assert c == "|c|"
```

```python
from mapbind import takebind

seq = range(0, 100)
a, b = takebind(seq)

assert a == 0
assert b == 1

seq = range(0, 2)
a, b, c, d, e, f, g = takebind(seq, 9001)

assert a == 0
assert b == 1
assert [c, d, e, f, g] == [9001] * 5
```


## But...

"Can't I just do `locals().update(data)`?"

That only works at the global/module scope. Once you're inside of a
function, `locals()` is nothing but a snapshot of the underlying fast,
free, and cell variables in a call frame.


## Supported Versions

This has been tested as working on the following versions and
implementations of Python

* Python 2.6, 2.7
* Python 3.4, 3.5, 3.6
* PyPy, PyPy3

It is implemented entirely in Python (no native extensions). It has no
runtime dependencies outside of itself and those provided as part of
the standard Python environment, though to run the unit tests you'll
need setuptools.


## Contact

author: Christopher O'Brien  <obriencj@gmail.com>

original git repository: <https://github.com/obriencj/python-mapbind>


## License

This library is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation; either version 3 of the
License, or (at your option) any later version.

This library is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, see
<http://www.gnu.org/licenses/>.
