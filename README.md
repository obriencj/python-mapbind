
# Overview of python-mapbind

Inspects its calling frame to figure out how you were going to bind
its results, then finds keys by those names in the given mapping and
returns them in the appropriate order.


## Wut?

A friend gave me the idea, and I wanted to see if it was
possible. Spoilers: it totally was.


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
a, b, c = mapbind(data)
```

The `mapbind` function looks at its calling frame's bytecode, figures
out that the result is going to be used in an unpacking assignment,
finds the names of the variables the assignment would bind to, and
returns an iterator for the values of the given items in data with
matching keys. Supercool.

## But...

"Can't I just do `locals().update(data)`?"

That only works at the global/module scope. Once you're inside of a
function, `locals()` is nothing but a view of the underlying fast,
free, and cell variables in a call frame.


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
