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


from functools import partial
from inspect import currentframe
from itertools import islice


try:
    # I want the lazy one, because I'm lazy and I can relate to it
    # better. Old Python put the lazy one in itertools. So unfair.
    from itertools import imap

except ImportError:
    # modern Python has its head on straight and realizes quality.
    imap = map


try:
    # old Python had its lazy range named this, so let's see if it's
    # there or not.
    xrange

except NameError:
    # new Python just has range, which is lazy. Let's maky an alias so
    # we can be lazy in both Pythons
    xrange = range


__all__ = ("mapbind", "objbind", "funbind", "takebind", "bindings", )


def setup():

    from sys import version_info

    try:
        # newer Python's dis has get_instructions, and that's awesome.
        from dis import get_instructions

    except ImportError:
        # okay, we're being loaded in an older Python environment.
        # There's no dis.get_instructions to import, so we'll have to
        # make one from scratch, like biscuits.

        from collections import namedtuple
        from dis import HAVE_ARGUMENT, opname

        if (2, 0) <= version_info < (3, 0):
            # if we're working on a Python2 environment, then the code
            # will be a str and we'll need to run ord on each op.
            def get(code, index):
                return ord(code[index])

        elif (3, 0) <= version_info < (4, 0):
            # otherwise, on a Python3 environment, then the code will
            # be a bytes object
            def get(code, index):
                return code[index]

        else:
            # if we reach this point then we couldn't find a working
            # get_instructions, and we aren't sure about how to make
            # one of our own, so we cannot support whatever version
            # this is. But hey, we tried.
            raise NotImplementedError("Unsupported Python version")

        Instr = namedtuple("Instruction", ["offset", "opname", "argval"])

        def get_instructions(code_obj):
            """
            a cheap knock-off of the get_instructions function from the
            Python3 version of the dis module. In this case, since we
            only care about some of the opcodes, we're only filling in
            the relevant data for those.
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
                    # Read the two arg bytes. All the older Pythons
                    # used two byte arguments, thankfully. The newer ones
                    # change that (3.6), but they have a dis module that
                    # can take care of those details for me.
                    oparg = get(code, index) | (get(code, index + 1) << 8)
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
                    # across versions... but their names sure are!

                    # PyPy string interning seems sketchy, so I use ==
                    # instead if 'is' as the comparator.

                    if name == "UNPACK_SEQUENCE":
                        yield instr(oparg)
                    elif name == "STORE_FAST":
                        yield instr(code_obj.co_varnames[oparg])
                    elif name == "STORE_DEREF":
                        yield instr(deref_names[oparg])
                    elif name == "STORE_GLOBAL" or name == "STORE_NAME":
                        yield instr(code_obj.co_names[oparg])
                    else:
                        # don't care.
                        yield instr(None)
                else:
                    # also don't care.
                    yield instr(None)

    return get_instructions


get_instructions = setup()
del setup


def bindings(caller, noname=False, _cache={}):
    """
    Find the names for the bindings that would be consumed by the
    caller frame.

    This is a relatively simple heuristic. unpack assignments usually
    look something like the following

    eg:  a, b, c = stuff()

    0   LOAD_FAST          0 (stuff)
    3   CALL_FUNCTION      0 (0 positional, 0 keyword pair)
    6   UNPACK_SEQUENCE    3
    9   STORE_FAST         1 (a)
    12  STORE_FAST         2 (b)
    15  STORE_FAST         3 (c)

    caller will have its index at the CALL_FUNCTION point there, so we
    skip past there and look for the argument to UNPACK_SEQUENCE
    (which is 3 in the example above). That lets us know how many
    STORE_FAST, STORE_GLOBAL, STORE_DEREF, or STORE_NAME operations
    will follow. Each of those has an argument that lets us figure out
    the name of that binding.  Those names, in the order they appear,
    are our result.

    If the optional noname parameter is True, then the heuristic stops
    after reading the count of bindings from an UNPACK_SEQUENCE op,
    and bindings will return a simple iterable of the appropriate
    length but with useless items (no names).
    """

    # find our calling frame, and the index of the op that called us
    code = caller.f_code
    index = caller.f_lasti

    cache_key = (code, index)
    if cache_key in _cache:
        return _cache[cache_key]

    # disassemble the instructions for the calling frame, and advance
    # past our calling op's index
    iterins = get_instructions(code)
    for instr in iterins:
        if instr.offset > index:
            break
    else:
        assert False, "f_lasti isn't in f_code"

    if instr.opname != "UNPACK_SEQUENCE":
        # someone invoked us without being the right-hand side of
        # an unpack assignment. WRONG.
        msg = "invoked without an unpack binding, %r" % instr.opname
        raise ValueError(msg)

    # this is the number of assignments being unpacked, we'll get that
    # many STORE_ ops from the bytecode
    count = instr.argval

    if noname:
        # the noname case is when we're being called via takebind,
        # which doesn't attempt to actually use the binding names.
        # we'll simply return an xrange of the appropriate length.
        result = xrange(0, count)
        _cache[cache_key] = result
        return result

    found = []

    for _ in xrange(0, count):
        instr = next(iterins)
        name = instr.opname

        if name == "STORE_FAST" or name == "STORE_DEREF" or \
           name == "STORE_GLOBAL" or name == "STORE_NAME":
            found.append(instr.argval)
        else:
            # nested unpack maybe? or a star function call? I say
            # unto thee nay. NAY!
            msg = "unsupported non-binding operation, %r" % name
            raise ValueError(msg)

    _cache[cache_key] = found
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
del RaiseError


def mapbind(source_map, default=raise_error):
    """
    Obtains value for each matching key from source_map for each
    binding.  If default is not provided, will raise KeyError if
    there's no matching mapping.

    eg.
    data = {"a": 100, "b": 200, "c": 300, "foo": 900, }
    a, b, c = mapbind(data)

    Will bind as data["a"], data["b"], data["c"]
    """

    caller = currentframe().f_back
    dest_names = bindings(caller)

    if default is raise_error:
        # why are we using imap instead of a generator? Because with
        # this, any exceptions raised will not show as having come
        # from inside the mapbind function.
        return imap(source_map.__getitem__, dest_names)
    else:
        return (source_map.get(binding, default)
                for binding in dest_names)


def objbind(source_obj, default=raise_error):
    """
    Obtains attribute with the matching name from source_obj for each
    binding.  If default is not provided, will raise AttributeError
    if there's no matching attribute.

    eg.
    data = some_object()
    a, b, c = objbind(data)

    Will bind as data.a, data.b, data.c
    """

    caller = currentframe().f_back
    dest_names = bindings(caller)

    if default is raise_error:
        # similarly to the mapbind case, using an imap and a partial
        # prevents any backtrace from peering into the objbind
        # function.
        return imap(partial(getattr, source_obj), dest_names)
    else:
        return (getattr(source_obj, binding, default)
                for binding in dest_names)


def funbind(fun):
    """
    Calls fun(NAME) to obtain the value for each binding, where NAME
    will be the binding variable name. Will be called from left to
    right.

    eg.
    a, b, c = funbind(my_function)

    Will bind as my_function("a"), my_function("b"), my_function("c")
    """

    caller = currentframe().f_back
    dest_names = bindings(caller)

    # the use of imap means funbind won't be part of backtraces if fun
    # raises an exception.
    return imap(fun, dest_names)


def takebind(sequence, default=raise_error):
    """
    Iterates over sequence to obtain the value for each binding

    eg.
    data = iter(range(0, 999))
    a, b, c = takebind(data)
    d, e, f = takebind(data)

    Will only take as many items from the iterable as are needed
    to fulfill the binding. Does nothing special with the binding
    names, and in fact doesn't perform the normal opcode check, so
    in this case nested unpacking is allowed provided the iterable
    results individually support further unpacking.

    If takebind runs out of items in the sequence and default is not
    specified, a ValueError will result as insufficient results will
    be returned. If default is specified, then it will be used to pad
    out the needed bindings.
    """

    caller = currentframe().f_back
    dest_names = bindings(caller, noname=True)

    # important to note that this is a noop if sequence is already a
    # an iterator
    iterator = iter(sequence)

    if default is not raise_error:
        # we don't want to raise an exception for running out of our
        # sequence, so let's wrap each step as a call to next with the
        # default value filled in. Thus when we run out of actual
        # sequence, we'll start emitting the default value
        # infinitely. Note that I'm re-purposing the raise_error
        # object instance as a sentinel value -- this form of iter
        # will stop when the result of the callable returns the
        # sentinel. Since we don't actually want it to ever stop,
        # we'll use a sentinel that should never actually happen,
        # which we conveniently already had!
        iterator = iter(partial(next, iterator, default), raise_error)

    # and now we just slice our sequence to the right length.
    return islice(iterator, 0, len(dest_names))


#
# The end.
