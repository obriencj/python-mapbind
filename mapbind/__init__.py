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


__all__ = ("mapbind", "objbind", "funbind", )


def setup():

    from inspect import currentframe

    # why are we using strings instead of integer opcodes? Because
    # some versions of dis don't expose the constant easily, and I'm
    # not entirely sure that the constants are constant between
    # versions of python... but the names are!
    STORE_OPS = set(("STORE_NAME", "STORE_GLOBAL",
                     "STORE_FAST", "STORE_DEREF", ))

    try:
        from dis import get_instructions

    except ImportError:
        # okay, we're being loaded in an older Python environment.
        # There's no dis.get_instructions to import, so we'll have to
        # make one from scratch, like biscuits.

        from collections import namedtuple
        from dis import opname, \
            HAVE_ARGUMENT, EXTENDED_ARG, \
            hasname, haslocal, hasfree
        from functools import partial

        Instr = namedtuple("Instruction", ["offset", "opname", "argval"])

        def get_instructions(code_obj):
            """
            a cheap knock-off of the get_instructions function from the
            Python3 version of the dis module. In this case, since we
            only care about some of the opcodes, we're only filling
            all the data for those ones in.
            """

            code = code_obj.co_code
            free_names = code_obj.co_cellvars + code_obj.co_freevars
            extended_arg = 0
            n = len(code)
            i = 0

            while i < n:
                c = code[i]
                op = ord(c)

                instr = partial(Instr, i, opname[op])

                i += 1
                if op >= HAVE_ARGUMENT:
                    oparg = ord(code[i]) | (ord(code[i + 1]) << 8)
                    oparg |= extended_arg
                    extended_arg = 0
                    i += 2

                    if op == "EXTENDED_ARG":
                        extended_arg = oparg << 16

                    if op in hasname:
                        yield instr(code_obj.co_names[oparg])
                    elif op in haslocal:
                        yield instr(code_obj.co_varnames[oparg])
                    elif op in hasfree:
                        yield instr(free_names[oparg])
                    else:
                        yield instr(oparg)
                else:
                    yield instr(None)


    class RaiseError(object):
        def __repr__(self):
            return "<raise an error>"

    # this is a default object for mapbind and objbind. We use it
    # instead of None because None is a perfectly valid default value.
    raise_error = RaiseError()

    weirdness = "binding called without being the right-hand" \
                " of a flat unpack assignment"

    def bindings(caller):
        """
        Find the names for the bindings
        """

        # find our calling frame, and the index of the op that called us
        code = caller.f_code
        index = caller.f_lasti

        # disassemble the instructions for the calling frame, and advance
        # past our calling op's index
        iterins = get_instructions(code)
        for instr in iterins:
            if instr.offset > index:
                break
        else:
            raise ValueError("couldn't find calling instruction, wtf?")

        if instr.opname != "UNPACK_SEQUENCE":
            # someone invoked us without being the right-hand side of
            # an unpack assignment. WRONG.
            msg = "expecging UNPACK_SEQUENCE op, got %s" % instr.opname
            raise ValueError(msg)

        # this is the number of assignments being unpacked, we'll get that
        # many STORE_ ops from the bytecode
        count = instr.argval

        for _ in range(0, count):
            instr = next(iterins)
            if instr.opname in STORE_OPS:
                yield instr.argval
            else:
                # wtf, nested unpack maybe? or a star function call? I
                # say unto thee nay. NAY!
                msg = "expecing a STORE_* op, got %s" % instr.opname
                raise ValueError(msg)


    def mapbind(source_map, default=raise_error):
        """
        Obtains value for each matching key from source_map for each
        binding. If default is not provided, will raise KeyError if
        there's no matching mapping.

        eg.
        data = {"a": 100, "b": 200, "c": 300, "foo": 900, }
        a, b, c = mapbind(data)

        Will return data["a"], data["b"], data["c"]
        """

        caller = currentframe().f_back

        if default is raise_error:
            return [source_map[binding]
                    for binding in bindings(caller)]
        else:
            return [source_map.get(binding, default)
                    for binding in bindings(caller)]


    def objbind(source_obj, default=raise_error):
        """
        Obtains attribute with the matching name from source_obj for each
        binding. If default is not provided, will raise AttributeError
        if there's no matching attribute.

        eg.
        data = some_object()
        a, b, c = objbind(data)

        Will get the attribute "a" from data, the attribute "b" from
        data, and the attribute "c" from data, returning the results
        in that order.
        """

        caller = currentframe().f_back

        if default is raise_error:
            return [getattr(source_obj, binding)
                    for binding in bindings(caller)]
        else:
            return [getattr(source_obj, binding, default)
                    for binding in bindings(caller)]


    def funbind(fun):
        """
        Calls fun(NAME) to obtain the binding for each binding

        eg.
        a, b, c = funbind(my_function)

        Will call my_function three times with the arguments "a", "b",
        and "c", returning the results in that order
        """

        caller = currentframe().f_back
        return [fun(binding) for binding in bindings(caller)]


    return mapbind, objbind, funbind


mapbind, objbind, funbind = setup()
del setup


#
# The end.
