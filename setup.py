#! /usr/bin/env python

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


from setuptools import setup


setup(name = "mapbind",
      version = "0.9.0",

      packages = (
          "mapbind",
      ),

      test_suite = "tests",

      # PyPI information
      author = "Christopher O'Brien",
      author_email = "obriencj@gmail.com",
      url = "https://github.com/obriencj/python-mapbind",
      license = "GNU Lesser General Public License v.3",

      description = "Local bindings from a map",

      provides = ("mapbind", ),
      requires = (),
      platforms = (),

      zip_safe = True,

      classifiers = (
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3",
          "Topic :: Software Development",
      )
)


#
# The end.
