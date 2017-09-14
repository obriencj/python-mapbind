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


"""
mapbind, a simple utility for binding vars from a map

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3
"""


from inspect import currentframe
from dis import get_instructions


__all__ = ("mapbind", )


def mapbind(source_map):
    """
    Find just the values for the bindings you were going to ask for.
    """

    # find our calling frame, and the index of the op that called us
    caller = currentframe().f_back
    code = caller.f_code
    index = caller.f_lasti

    # disassemble the instructions for the calling frame, and advance
    # past our calling op's index
    iterins = get_instructions(code)
    for instr in iterins:
        if instr.offset > index:
            break

    if instr.opname != "UNPACK_SEQUENCE":
        # someone invoked us without being the right-hand side of an
        # unpack assignment, do let's be a noop
        return source_map

    # this is the number of assignments being unpacked, we'll get that
    # many STORE_ ops from the bytecode
    count = instr.argval

    # each STORE_ op has an argval which is the name it would assign
    # to. This is just a convenience that the dis module fills in!
    dest_keys = (next(iterins).argval for _ in range(0, count))

    # finally, just return a generator that'll provide the values from
    # the source_map that match to the bindings
    return (source_map[dest] for dest in dest_keys)


#
# The end.
