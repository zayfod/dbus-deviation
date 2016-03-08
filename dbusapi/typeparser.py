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

from dbusapi import types
from dbusapi.log import Log


class TypeParserLog(Log):

    """Specialized Log subclass for type parser messages."""

    def __init__(self):
        """Construct a new TypeParserLog"""
        super(TypeParserLog, self).__init__()
        self.register_issue_code('unknown-type')
        self.register_issue_code('invalid-type')
        self.domain = 'type_parser'


class TypeParser(object):

    """
    Parse a D-Bus type string.

    This validates the string, but not exceedingly strictly..
    """

    def __init__(self, signature, log=None):
        """
        Construct a new TypeParser.

        Args:
            signature: A D-Bus type string.
        """
        self.signature = signature
        self.log = log or TypeParserLog()
        self._index = 0

    def get_output_codes(self):
        """Return a list of all possible output codes."""
        return self.log.issue_codes

    def get_output(self):
        """Return a list of all logged parser messages."""
        return self.log.issues

    def _get_next_character(self):
        """Return the next character from the signature."""
        if self._index < len(self.signature):
            character = self.signature[self._index]
            self._index += 1
        else:
            character = None
        return character

    def _parse_one(self, character):
        """Parse one character of a signature."""
        if character == "y":
            return types.Byte()
        elif character == "b":
            return types.Boolean()
        elif character == "n":
            return types.Int16()
        elif character == "q":
            return types.UInt16()
        elif character == "i":
            return types.Int32()
        elif character == "u":
            return types.UInt32()
        elif character == "x":
            return types.Int64()
        elif character == "t":
            return types.UInt64()
        elif character == "d":
            return types.Double()
        elif character == "s":
            return types.String()
        elif character == "o":
            return types.ObjectPath()
        elif character == "g":
            return types.Signature()
        elif character == "v":
            return types.Variant()
        elif character == "h":
            return types.UnixFD()
        elif character == "a":
            res = types.Array()
            character = self._get_next_character()
            if not character:
                self.log.log_issue('invalid-type',
                                   'Incomplete array declaration.')
                return None
            one_type = self._parse_one(character)
            if not one_type:
                # Invalid member type
                return None
            res.members.append(one_type)
            return res
        elif character == "(":
            res = types.Struct()
            while True:
                character = self._get_next_character()
                if not character:
                    self.log.log_issue('invalid-type',
                                       'Incomplete structure declaration.')
                    return None
                if character == ")":
                    break
                one_type = self._parse_one(character)
                if not one_type:
                    # Invalid member type
                    return None
                res.members.append(one_type)
            return res
        elif character == "{":
            res = types.DictEntry()
            while True:
                character = self._get_next_character()
                if not character:
                    self.log.log_issue('invalid-type',
                                       'Incomplete dictionary declaration.')
                    return None
                if character == "}":
                    break
                one_type = self._parse_one(character)
                if not one_type:
                    # Invalid member type
                    return None
                if len(res.members) >= 2:
                    self.log.log_issue('invalid-type',
                                       'Invalid dictionary declaration.')
                    return None
                res.members.append(one_type)
            return res
        else:
            self.log.log_issue('unknown-type',
                               'Unknown type ‘%s’.' % character)
            return None

    def parse(self):
        """
        Parse the type string and build an

        Returns:
            A non-empty list of types.

            If parsing fails, None is returned.
        """
        self._index = 0

        out = types.TypeSignature()
        while True:
            character = self._get_next_character()
            if not character:
                break

            one_type = self._parse_one(character)
            if not one_type:
                # Invalid type
                break

            out.members.append(one_type)

        if self.log.issues:
            return None

        return out
