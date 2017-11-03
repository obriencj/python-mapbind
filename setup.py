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
mapbind, assignment-aware binding functions

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3
"""


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(name = "mapbind",
      version = "1.0.0",

      packages = (
          "mapbind",
      ),

      test_suite = "tests",

      # PyPI information
      author = "Christopher O'Brien",
      author_email = "obriencj@gmail.com",
      url = "https://github.com/obriencj/python-mapbind",
      license = "GNU Lesser General Public License v.3",

      description = "Assignment-aware binding functions",

      # 2.6+ or 3.3+
      python_requires = ">=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4",

      classifiers = (
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Topic :: Software Development",
      )
)


#
# The end.
