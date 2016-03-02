#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
#
# Copyright © 2016 Kaloyan Tenchov
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

"""
Unit tests for dbusapi.typeparser
"""


from dbusapi.typeparser import TypeParser
import unittest


def _test_parser(signature):
    """Build a TypeParser for a signature and parse it."""
    parser = TypeParser(signature)
    types = parser.parse()
    return parser, types


class TestParserErrors(unittest.TestCase):
    """Test error handling in the TypeParser."""

    # pylint: disable=invalid-name
    def assertOutput(self, signature, partial_output):  # noqa
        (parser, types) = _test_parser(signature)
        self.assertEqual(types, None)
        actual_output = [(i[0], i[1]) for i in partial_output]
        self.assertEqual(parser.get_output(), actual_output)

    def test_unknown_type(self):
        self.assertOutput(
            "?", [
                ('unknown-type', 'Unknown type ‘?’.'),
            ])

    def test_incomplete(self):
        self.assertOutput(
            "aa", [
                ('invalid-type', 'Incomplete array declaration.'),
            ])

    def test_incomplete2(self):
        self.assertOutput(
            "(ii", [
                ('invalid-type', 'Incomplete structure declaration.'),
            ])

    def test_incomplete3(self):
        self.assertOutput(
            "ii)", [
                ('unknown-type', 'Unknown type ‘)’.'),
            ])

    def test_incomplete4(self):
        self.assertOutput(
            "a{suu}", [
                ('invalid-type', 'Invalid dictionary declaration.'),
            ])

    def test_incomplete5(self):
        self.assertOutput(
            "a{su", [
                ('invalid-type', 'Incomplete dictionary declaration.'),
            ])

    def test_incomplete6(self):
        self.assertOutput(
            "a{s", [
                ('invalid-type', 'Incomplete dictionary declaration.'),
            ])


class TestParserNormal(unittest.TestCase):
    """Test normal parsing of unusual input in the TypeParser."""

    # pylint: disable=invalid-name
    def assertParse(self, signature):  # noqa
        (parser, type_signature) = _test_parser(signature)
        self.assertEqual(parser.get_output(), [])
        actual_signature = str(type_signature)
        self.assertEqual(signature, actual_signature)

    def test_int32(self):
        self.assertParse("i")

    def test_two_int32(self):
        self.assertParse("ii")

    def test_two_int32_arrays(self):
        self.assertParse("aiai")

    def test_uint32(self):
        self.assertParse("u")

    def test_two_uint32(self):
        self.assertParse("uu")

    def test_array_int32(self):
        self.assertParse("ai")

    def test_array_array_int32(self):
        self.assertParse("aai")

    def test_array_uint32(self):
        self.assertParse("au")

    def test_array_variant(self):
        self.assertParse("av")

    def test_struct_ints(self):
        self.assertParse("(iii)")

    def test_two_structs(self):
        self.assertParse("(ii)(ii)")

    def test_struct_struct_ints(self):
        self.assertParse("(i(ii))")

    def test_struct_variant(self):
        self.assertParse("(v)")

    def test_struct_ius(self):
        self.assertParse("(ius)")

    def test_array_struct_ints(self):
        self.assertParse("a(ii)")

    def test_array_dict(self):
        self.assertParse("a{us}")

    def test_array_dict2(self):
        self.assertParse("a{us}i")


if __name__ == '__main__':
    # Run test suite
    unittest.main()
