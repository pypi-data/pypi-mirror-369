# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

'''
caldavctl uses a simple format to create new objects. this format is parsed and
converted into iCalendar objects.
'''

from abc import ABC, abstractmethod
from datetime import datetime
from functools import reduce
from operator import and_, xor
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class ValueParser(ABC):
    def __init__(self, txt):
        '''
        Arguments:

        txt - raw data
        '''
        self.txt = txt
        self.tokens = None
        self.value = None  # return value

    @abstractmethod
    def tokenize(self):
        ...

    @abstractmethod
    def validate(self):
        ...

    def parse(self):
        self.tokenize()
        self.validate()
        return self.value


class ParserError(Exception):
    pass


class TimezoneParser(ValueParser):
    def tokenize(self):
        self.tokens = self.txt

    def validate(self):
        try:
            self.value = ZoneInfo(self.tokens)
        except (ZoneInfoNotFoundError, ValueError):
            raise ParserError(f'invalid timezone: "{self.tokens}"')


class DatetimeParser(ValueParser):
    def tokenize(self):
        self.tokens = self.txt

    def validate(self):
        try:
            self.value = datetime.fromisoformat(self.tokens)
        except ValueError:
            raise ParserError(f'Invalid date format for: "{self.tokens}"')


def integer_parser(min=None, max=None):

    class IntegerParser(ValueParser):
        def tokenize(self):
            self.tokens = self.txt

        def validate(self):
            try:
                value = int(self.tokens)
            except ValueError as msg:
                raise ParserError(msg)
            if min and value < min:
                raise ParserError('the value is less than the minimum value.')
            if max and value > max:
                raise ParserError('the value is greater than the maximum value.')
            self.value = value

    return IntegerParser


def integer_list_parser(min=None, max=None, exception=[], sep=','):

    class IntegerListParser(ValueParser):
        def tokenize(self):
            self.tokens = self.txt.split(sep)

        def validate(self):
            try:
                values = [int(vl) for vl in self.tokens]
            except ValueError as msg:
                raise ParserError(msg)
            for value in values:
                if min and value < min:
                    raise ParserError(f'the value is less than the minimum value ({min}).')
                if max and value > max:
                    raise ParserError(f'the value is greater than the maximum value ({max}).')
                if value in exception:
                    raise ParserError(f'forbiden value {value}.')
            self.value = values

    return IntegerListParser


def choices_parser(choices, sep=','):
    choices = [el.upper() for el in choices]

    class EnumParser(ValueParser):
        def tokenize(self):
            self.tokens = self.txt

        def validate(self):
            if self.tokens.upper() not in choices:
                raise ParserError(f'Element {self.tokens} not in allowed values: {', '.join(choices)}')
            self.value = self.tokens

    return EnumParser


def string_parser(max_len=None):

    class StringParser(ValueParser):
        def tokenize(self):
            self.tokens = self.txt

        def validate(self):
            if max_len and len(self.tokens) > max_len:
                raise ParserError(f'max string lenght is {max_len}.')
            self.value = self.tokens

    return StringParser


def list_parser(max_len=None, sep=','):

    class ListParser(ValueParser):
        def tokenize(self):
            if self.txt:
                self.tokens = [el.strip() for el in self.txt.split(sep)]
            else:
                self.tokens = []

        def validate(self):
            if max_len and len(self.tokens) > max_len:
                raise ParserError(f'max list lenght is {max_len}.')
            self.value = self.tokens

    return ListParser


def flaten(lst):
    for el in lst:
        if isinstance(el, list):
            yield flaten(el)
        else:
            yield el


class ObjectParser(ABC):
    def __init__(self, obj, lexicon, mandatory=[], exclusive=[]):
        self.object = obj
        self.lexicon = lexicon
        self.mandatory = mandatory
        self.optional = set(lexicon.keys()) - set(flaten(mandatory))
        self.exclusive = exclusive

    @abstractmethod
    def tokenize(self):
        ...

    def check_mandatory(self, result):
        # Check mandatory fields
        for key in self.mandatory:
            if isinstance(key, list):
                if reduce(and_, [subkey in result for subkey in key]):
                    raise ParserError(f'Only one of these keys can be present: {', '.join(key)}')
                elif not reduce(xor, [subkey in result for subkey in key]):
                    raise ParserError(f'One of these keys must be present: {', '.join(key)}')
            else:
                if key not in result:
                    raise ParserError(f'Missing mandatory key: "{key}"')

    def check_exclusive(self, result):
        for exclusive_key in self.exclusive:
            if reduce(and_, [subkey in result for subkey in exclusive_key]):
                raise ParserError(f'Only one of these keys can be present: {', '.join(exclusive_key)}')

    def drop_optional(self, result):
        '''
        Remove empty optional keys from results
        '''
        for key in self.optional:
            if key in result and not result[key]:
                del result[key]

    def parse(self, tokens):
        result = {}
        for key, value in tokens:
            key = key.lower()  # The keys are case insensitive
            if key not in self.lexicon:
                raise ParserError(f'unknown key: "{key}".')

            value_type = self.lexicon[key]

            try:
                if value:
                    parsed_value = value_type(value).parse()
                else:
                    parsed_value = value
            except ParserError as msg:
                raise ParserError(f'Error evaluating key "{key.upper()}": {msg}')
            if key in result:
                # We have a key that can show up more than one time
                if not isinstance(result[key], list):
                    result[key] = [result[key]]
                result[key].append(parsed_value)
            else:
                # Single value key
                result[key] = parsed_value

        return result

    def run(self):
        tokens = self.tokenize()
        result = self.parse(tokens)
        self.check_mandatory(result)
        self.check_exclusive(result)
        self.drop_optional(result)
        return result


class EventParser(ObjectParser):

    def tokenize(self):
        # States:
        KEY = 0
        VALUE = 1

        data = self.object
        tokens = []
        pos = 0
        lenght = len(data)
        state = KEY
        while pos < lenght:
            if data[pos] in ' \t':  # Ignore spaces
                pos += 1
                continue
            if data[pos] == '#':  # Ignore comments
                pos = data.find('\n', pos) + 1
                if pos == 0:  # End of file
                    pos = lenght
                continue

            if state == KEY:  # Find the key
                if data[pos] in ';\n':  # New lines or semicolons before the key
                    pos += 1
                    continue
                end = data.find(':', pos)
                if end == -1:
                    raise ParserError('Could not find key/value pair.')
                key = data[pos:end].strip()
                pos = end + 1
                state = VALUE
                continue

            if state == VALUE:  # Find the value
                if pos == lenght or data[pos] in ';\n':  # End of file or empty value
                    pos += 1
                    tokens.append([key, ''])
                    state = KEY
                    continue
                if data[pos:pos + 2] == '[[':  # Multi line string
                    end = data.find(']]', pos)
                    if end == -1:  # No closing
                        raise ParserError('Unclosed double bracket')
                    value = data[pos + 2:end].strip()
                    tokens.append([key, value])
                    pos = end + 2
                    state = KEY
                    continue
                else:
                    # Single line string
                    semicolon = data.find(';', pos)
                    newline = data.find('\n', pos)
                    comment = data.find('#', pos)

                    if semicolon != -1 and newline != -1 and newline < semicolon:
                        end = newline
                    elif semicolon != -1 and newline != -1 and semicolon < newline:
                        end = semicolon
                    elif semicolon == -1 and newline == -1:  # end of file
                        end = lenght
                    elif semicolon == -1 and newline != -1:  # End of line no semicolons
                        end = newline
                    elif semicolon != -1 and newline == -1:  # Last line with semicolons
                        end = semicolon
                    else:  # Just to make sure I got all possible combinations
                        raise ParserError('Internal tokenizer error')

                    # Handle comments
                    if comment != -1 and comment < end:
                        value = data[pos:comment].strip()
                        end = comment - 1
                    else:
                        value = data[pos:end].strip()

                    tokens.append([key, value])
                    pos = end + 1
                    state = KEY
                    continue
            pos += 1

        if state == VALUE:
            tokens.append([key, ''])
        return tokens


class RRuleParser(ObjectParser):

    def tokenize(self):
        data = self.object
        return [
            [tok.upper().strip() for tok in keyvalue.split('=', maxsplit=1)]
            for keyvalue in data.split(';')
            if keyvalue.strip()
        ]
