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
mapbind

A simple set of functions for binding variables from a mapping, an
object's attributes, or an arbitrary function call given the variable
name.

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3
"""


__all__ = ("mapbind", "objbind", "funbind", "bindings", )


def setup():

    # So why is all of this inside of a setup function? Primarily it's
    # because I need to do all this jackassery to find or create the
    # get_instructions function. I also wanted to hide that RaiseError
    # type and the raise_error instance. Once that was done, I had all
    # these imports available as closures and it seemed silly to
    # replicate in a slower global scope. Aesthetically, it sucks. I
    # admit that. Oh well, more legible than the half the crap I see.

    from functools import partial
    from inspect import currentframe

    try:
        # I want the lazy one, because I'm lazy and I can relate to it
        # better. Old Python put the lazy one in itertools. So unfair.
        from itertools import imap

    except ImportError:
        # modern Python has its head on straight and realizes quality.
        imap = map

    try:
        # newer Python's dis has get_instructions, and that's awesome.
        from dis import get_instructions

    except ImportError:
        # okay, we're being loaded in an older Python environment.
        # There's no dis.get_instructions to import, so we'll have to
        # make one from scratch, like biscuits.

        from collections import namedtuple
        from dis import HAVE_ARGUMENT, opname

        Instr = namedtuple("Instruction", ["offset", "opname", "argval"])

        def get_instructions(code_obj):
            """
            a cheap knock-off of the get_instructions function from the
            Python3 version of the dis module. In this case, since we
            only care about some of the opcodes, we're only filling
            all the data for those ones in.
            """

            code = code_obj.co_code
            deref_names = code_obj.co_cellvars + code_obj.co_freevars

            limit = len(code)
            index = 0

            while index < limit:
                op = ord(code[index])
                name = opname[op]
                instr = partial(Instr, index, name)
                index += 1

                if op >= HAVE_ARGUMENT:
                    # Read the two arg bytes. All the older Pythons
                    # used two byte arguments, thankfully. The newer ones
                    # change that (3.6), but they have a dis module that
                    # can take care of those details for me.
                    oparg = ord(code[index]) | (ord(code[index + 1]) << 8)
                    index += 2

                    # Totally ignoring EXTENDED_ARG. You know why?
                    # Because it'll only impact us if you have more
                    # than 65535 local variables, in which case I
                    # don't even want to work for you, you deserve to
                    # break.

                    # I'm using the names of the op instead of their
                    # number because some older dis versions don't
                    # expose them as constants, and I'm not even sure
                    # that the opcode numbers really are constant
                    # across versions... but their names sure are! I'm
                    # also taking advantage of the fact that these
                    # ought to darned well be interned, so I can use
                    # 'is' as the check.
                    if name is "UNPACK_SEQUENCE":
                        yield instr(oparg)
                    elif name is "STORE_FAST":
                        yield instr(code_obj.co_varnames[oparg])
                    elif name is "STORE_DEREF":
                        yield instr(deref_names[oparg])
                    elif name is "STORE_GLOBAL" or name is "STORE_NAME":
                        yield instr(code_obj.co_names[oparg])
                    else:
                        # don't care.
                        yield instr(None)
                else:
                    # also don't care.
                    yield instr(None)


    def bindings(caller):
        """
        Find the names for the bindings that would be consumed by the
        caller frame.

        This is a relatively simple heuristic. unpack assignments
        usually look something like the following

        eg:  a, b, c = stuff()

        0   LOAD_FAST          0 (stuff)
        3   CALL_FUNCTION      0 (0 positional, 0 keyword pair)
        6   UNPACK_SEQUENCE    3
        9   STORE_FAST         1 (a)
        12  STORE_FAST         2 (b)
        15  STORE_FAST         3 (c)

        caller will have its index at the CALL_FUNCTION point there,
        so we skip past there and look for the argument to
        UNPACK_SEQUENCE (which is 3 in the example above). That lets
        us know how many STORE_FAST, STORE_GLOBAL, STORE_DEREF, or
        STORE_NAME operations will follow. Each of those has an
        argument that lets us figure out the name of that binding.
        Those names, in the order they appear, are our result.
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
            assert False, "f_lasti isn't in f_code"

        if instr.opname is not "UNPACK_SEQUENCE":
            # someone invoked us without being the right-hand side of
            # an unpack assignment. WRONG.
            msg = "invoked without an unpack binding, %r" % instr.opname
            raise ValueError(msg)

        # this is the number of assignments being unpacked, we'll get that
        # many STORE_ ops from the bytecode
        count = instr.argval

        found = []

        for _ in range(0, count):
            instr = next(iterins)
            name = instr.opname
            if name is "STORE_FAST" or name is "STORE_DEREF" or \
               name is "STORE_GLOBAL" or name is "STORE_NAME":
                found.append(instr.argval)
            else:
                # nested unpack maybe? or a star function call? I say
                # unto thee nay. NAY!
                msg = "unsupported non-binding operation, %r" % name
                raise ValueError(msg)

        return found


    class RaiseError(object):
        def __repr__(self):
            # this makes the help for the mapbind and objbind
            # functions look cool.
            return "<raise an error>"  # noqa


    # this is a default object for mapbind and objbind. We use it
    # instead of None because None would be a perfectly valid actual
    # default value for someone to specify. The RaiseError class on
    # the other hand, and this single instance of it in particular,
    # has no purpose outside of this scope, so make perfect sentinel
    # values.
    raise_error = RaiseError()


    def mapbind(source_map, default=raise_error):
        """
        Obtains value for each matching key from source_map for each
        binding. If default is not provided, will raise KeyError if
        there's no matching mapping.

        eg.
        data = {"a": 100, "b": 200, "c": 300, "foo": 900, }
        a, b, c = mapbind(data)

        Will bind as data["a"], data["b"], data["c"]
        """

        caller = currentframe().f_back
        dest_names = bindings(caller)

        if default is raise_error:
            return (source_map[binding] for binding in dest_names)
        else:
            return (source_map.get(binding, default)
                    for binding in dest_names)


    def objbind(source_obj, default=raise_error):
        """
        Obtains attribute with the matching name from source_obj for each
        binding. If default is not provided, will raise AttributeError
        if there's no matching attribute.

        eg.
        data = some_object()
        a, b, c = objbind(data)

        Will bind as data.a, data.b, data.c
        """

        caller = currentframe().f_back
        dest_names = bindings(caller)

        if default is raise_error:
            return imap(partial(getattr, source_obj), dest_names)
        else:
            return (getattr(source_obj, binding, default)
                    for binding in dest_names)


    def funbind(fun):
        """
        Calls fun(NAME) to obtain the binding for each binding

        eg.
        a, b, c = funbind(my_function)

        Will bind as my_function("a"), my_function("b"), my_function("c")
        """

        caller = currentframe().f_back
        dest_names = bindings(caller)

        return imap(fun, dest_names)


    # grr. qualname spoils all my lovely nested functions with horrid
    # names. I'll fix you guys up, don't worry.
    mapbind.__qualname__ = "mapbind.mapbind"
    objbind.__qualname__ = "mapbind.objbind"
    funbind.__qualname__ = "mapbind.funbind"
    bindings.__qualname__ = "mapbind.bindings"

    return mapbind, objbind, funbind, bindings


mapbind, objbind, funbind, bindings = setup()
del setup


#
# The end.
