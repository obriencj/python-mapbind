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
mapbind._dis

Provides some of get_instructions functionality across a range of
Python versions, emulating the relevant behavior if not present.

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3
"""


from collections import namedtuple
from dis import HAVE_ARGUMENT, opname
from functools import partial
from sys import version_info


__all__ = ("get_instructions", )


if (2, 0) <= version_info < (3, 0):
    # if we're working on a Python2 environment, then the code will be
    # a str and we'll need to run ord on each op.
    def get(code, index):
        return ord(code[index])

elif (3, 0) <= version_info < (4, 0):
    # otherwise, on a Python3 environment, then the code will be a
    # bytes object
    def get(code, index):
        return code[index]

else:
    # if we reach this point then we couldn't find a working
    # get_instructions, and we aren't sure about how to make one of
    # our own, so we cannot support whatever version this is. But hey,
    # we tried.
    raise NotImplementedError("Unsupported Python version")


Instr = namedtuple("Instruction", ["offset", "opname", "argval"])


def get_instructions(code_obj):
    """
    a cheap knock-off of the get_instructions function from the
    Python3 version of the dis module. In this case, since we only
    care about some of the opcodes, we're only filling in the relevant
    data for those.
    """

    code = code_obj.co_code
    deref_names = code_obj.co_cellvars + code_obj.co_freevars

    limit = len(code)
    index = 0

    while index < limit:
        op = get(code, index)
        name = opname[op]
        instr = partial(Instr, index, name)
        index += 1

        if op >= HAVE_ARGUMENT:
            # Read the two arg bytes. All the older Pythons used two
            # byte arguments, thankfully. The newer ones change that
            # (3.6), but they have a dis module that can take care of
            # those details for me.
            oparg = get(code, index) | (get(code, index + 1) << 8)
            index += 2

            # Totally ignoring EXTENDED_ARG. You know why?  Because
            # it'll only impact us if you have more than 65535 local
            # variables, in which case I don't even want to work for
            # you, you deserve to break.

            # I'm using the names of the op instead of their number
            # because some older dis versions don't expose them as
            # constants, and I'm not even sure that the opcode numbers
            # really are constant across versions... but their names
            # sure are!

            # PyPy string interning seems sketchy, so I use == instead
            # if 'is' as the comparator.

            if name == "UNPACK_SEQUENCE":
                yield instr(oparg)
            elif name == "STORE_FAST":
                yield instr(code_obj.co_varnames[oparg])
            elif name == "STORE_DEREF":
                yield instr(deref_names[oparg])
            elif name in ("STORE_GLOBAL", "STORE_NAME"):
                yield instr(code_obj.co_names[oparg])
            else:
                # don't care.
                yield instr(None)
        else:
            # also don't care.
            yield instr(None)


#
# The end.
