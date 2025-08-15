# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from caldavctl.object_parser import EventParser, ParserError
from caldavctl.event_builder import parse_event, check_if_naive, EVENT_LEXICON, MANDATORY_KEYS


sample_event_data_i = """
        SUMMARY: This is a description
        LOCATION: [[Timbuktu]] # With a comment
        CATEGORIES: Birthday, Shopping, Training
        TIMEZONE: Europe/Lisbon
        DTSTART: 2024-01-20 09:00
        DTEND: 2024-01-20 09:45
        DESCRIPTION: [[
        Once upon a time,
        There was a little lamb
        ]]
        """

expected_tokens_i = [
    ['SUMMARY', 'This is a description'],
    ['LOCATION', 'Timbuktu'],
    ['CATEGORIES', 'Birthday, Shopping, Training'],
    ['TIMEZONE', "Europe/Lisbon"],
    ['DTSTART', '2024-01-20 09:00'],
    ['DTEND', '2024-01-20 09:45'],
    ['DESCRIPTION', 'Once upon a time,\n        There was a little lamb']
]

sample_event_data_ii = '''# Mandatory
SUMMARY: Example summary
DTSTART: 2024-12-30 09:00
DTEND: 2024-12-30 09:45

# Optional
LOCATION:
CATEGORIES:
TIMEZONE: Europe/Lisbon
DESCRIPTION: [[ ]]

# NOTES:
#
#   * Date and time:
#       * The dates must be in iso format, for instance: 2024-12-29 13:45;
#       * The timezone used if the one defined by default or the one defined in
#         "TIMEZONE";
#   * Categories: the categories are a comma separeted list;
#   * Description: The description can be multi line, just make sure it's
#     delimited by [[ ]].'''


@pytest.fixture
def default_timezone():
    return ZoneInfo('UTC')


tokenize_test_data = (
    (sample_event_data_i, expected_tokens_i),
    # Multiple keys in one line
    ('KEY1:VALUE1; KEY2:VALUE2;', [['KEY1', 'VALUE1'], ['KEY2', 'VALUE2']]),
    ('KEY1:VALUE1; KEY2:VALUE2\nKEY3:VALUE3;', [['KEY1', 'VALUE1'], ['KEY2', 'VALUE2'],
                                                ['KEY3', 'VALUE3']]),

    # Empty values
    ('KEY1:', [['KEY1', '']]),
    ('KEY1:\nKEY2:', [['KEY1', ''], ['KEY2', '']]),
    ('KEY1:   ', [['KEY1', '']]),  # Whitespace that should be trimmed
    ('KEY1:; KEY2:value', [['KEY1', ''], ['KEY2', 'value']]),

    # Comments handling
    ('KEY: value # comment', [['KEY', 'value']]),
    ('# Just a comment\nKEY: value', [['KEY', 'value']]),
    ('KEY: value with # hash', [['KEY', 'value with']]),
    ('KEY: value # comment\nKEY2: value2', [['KEY', 'value'], ['KEY2', 'value2']]),

    # Whitespace handling
    ('  KEY:  value  ', [['KEY', 'value']]),
    ('KEY:value', [['KEY', 'value']]),
    (' KEY : value ', [['KEY', 'value']]),

    # Multiline values with brackets
    ('''KEY: [[
    multiline
    value
    ]]''', [['KEY', 'multiline\n    value']]),

    # Nested brackets
    ('KEY: [[ value with [nested] brackets ]]', [['KEY', 'value with [nested] brackets']]),

    # Mixed delimiters
    ('KEY1: value1; KEY2:value2', [['KEY1', 'value1'], ['KEY2', 'value2']]),
    ('KEY1: value1\nKEY2:value2', [['KEY1', 'value1'], ['KEY2', 'value2']]),

    # Case sensitivity
    ('key: value', [['key', 'value']]),
    ('KEY: value', [['KEY', 'value']]),

    # Special characters in values
    ('KEY: value:with:colons', [['KEY', 'value:with:colons']]),

    # Empty keys (should probably be rejected by the parser but good to test)
    (': value without key', [['', 'value without key']]),


    # Mixed line endings
    ('KEY1: value1\r\nKEY2: value2', [['KEY1', 'value1'], ['KEY2', 'value2']]),

    # Multiline with comments
    ('''KEY: [[
    multiline # not a comment
    value
    ]] # this is a comment''', [['KEY', 'multiline # not a comment\n    value']]),

    # Multiple multiline values
    ('''KEY1: [[
    first multiline
    ]]
    KEY2: [[
    second multiline
    ]]''', [['KEY1', 'first multiline'], ['KEY2', 'second multiline']]),

    # TODO: Should escaped characters be supported?
    # Escaped characters
    ('KEY: value with \\"quotes\\"', [['KEY', 'value with \\"quotes\\"']]),
    ('KEY: value with \\n newline', [['KEY', 'value with \\n newline']]),

    # Multiple keys with same name (should preserve all)
    ('KEY: value1\nKEY: value2', [['KEY', 'value1'], ['KEY', 'value2']]),

    # Keys with spaces or unusual characters (if supported)
    ('KEY WITH SPACES: value', [['KEY WITH SPACES', 'value']]),
    ('KEY-WITH-DASHES: value', [['KEY-WITH-DASHES', 'value']]),
    ('KEY_WITH_UNDERSCORES: value', [['KEY_WITH_UNDERSCORES', 'value']]),

    # TODO: should this be supported?
    # # Mixed line continuation
    # ('''KEY: value that \
    # continues on next line''', [['KEY', 'value that continues on next line']]),

    # Completely empty input
    ('', []),

    # Just whitespace
    ('   \n  \t  ', []),

    # Just comments
    ('# comment1\n# comment2', []),

    # Comments
    ('KEY1: value 1 # ; KEY2: value2', [['KEY1', 'value 1']])

)


@pytest.mark.parametrize('sample, result', tokenize_test_data)
def test_tokenize_data(sample, result):
    print(f'\nTesting: {sample}')
    parser = EventParser(sample, EVENT_LEXICON, MANDATORY_KEYS)
    tokens = parser.tokenize()
    print('Computed tokens:', tokens)
    assert tokens == result


tokenizer_error_test_data = (
    # Unclosed multiline blocks
    ('''KEY: [[
    unclosed multiline
    ''', 'Unclosed double bracket'),

    ('KEY: value;with;semicolons', 'Could not find key/value pair'),

)


@pytest.mark.parametrize('sample, error_message', tokenizer_error_test_data)
def test_tokenizer_errors(sample, error_message):
    print(f'\nTesting: {sample}')
    parser = EventParser(sample, EVENT_LEXICON, MANDATORY_KEYS)
    with pytest.raises(ParserError, match=error_message):
        tokens = parser.tokenize()
        print('Computed tokens:', tokens)


def test_parse_i():
    result = EventParser(sample_event_data_i, EVENT_LEXICON, MANDATORY_KEYS).run()

    expected_result = {
        'summary': 'This is a description',
        'location': 'Timbuktu',
        'categories': ['Birthday', 'Shopping', 'Training'],
        'timezone': ZoneInfo('Europe/Lisbon'),
        'dtstart': datetime(2024, 1, 20, 9, 0),
        'dtend': datetime(2024, 1, 20, 9, 45),
        'description': 'Once upon a time,\n        There was a little lamb'
    }

    assert result['summary'] == expected_result['summary']
    assert result['location'] == expected_result['location']
    assert result['categories'] == expected_result['categories']
    assert result['description'] == expected_result['description']
    assert result['dtstart'] == expected_result['dtstart']
    assert result['dtend'] == expected_result['dtend']
    assert result['timezone'] == expected_result['timezone']


def test_parse_ii():
    result = EventParser(sample_event_data_ii, EVENT_LEXICON, MANDATORY_KEYS).run()

    expected_result = {
        'summary': 'Example summary',
        'location': '',
        'categories': [],
        'timezone': ZoneInfo('Europe/Lisbon'),
        'dtstart': datetime(2024, 12, 30, 9, 0),
        'dtend': datetime(2024, 12, 30, 9, 45),
        'description': ''
    }

    assert result['summary'] == expected_result['summary']
    assert 'location' not in result
    assert 'categories' not in result
    assert 'description' not in result
    assert result['dtstart'] == expected_result['dtstart']
    assert result['dtend'] == expected_result['dtend']
    assert result['timezone'] == expected_result['timezone']


def test_check_if_naive():
    naive_date = datetime(2024, 1, 20, 9, 0)
    tz = ZoneInfo('Europe/Lisbon')
    localized_date = check_if_naive(naive_date, tz)

    assert f'{localized_date.tzinfo}' == 'Europe/Lisbon'
    assert localized_date.utcoffset() == tz.utcoffset(naive_date)


def test_parse_event_with_naive_dates(default_timezone):
    event_with_naive_dates = (
        """
        SUMMARY: Test Event
        LOCATION: Timbuktu
        TIMEZONE: Europe/Lisbon
        DTSTART: 2024-01-20 09:00
        DTEND: 2024-01-20 09:45Z  # UTC date
        """
    )

    result = parse_event(event_with_naive_dates, default_timezone)
    tz = ZoneInfo('Europe/Lisbon')

    assert result['dtstart'].tzinfo == tz
    assert result['dtend'].tzinfo == timezone.utc


def test_unknown_key():
    event_with_unknown_key = (
        """
        SUMMARY: Test Event
        UNKNOWN_KEY: This should fail
        """
    )
    parser = EventParser(event_with_unknown_key, EVENT_LEXICON, MANDATORY_KEYS)

    with pytest.raises(ParserError, match='unknown key:'):
        parser.run()


def test_invalid_date():
    event_with_invalid_date = (
        """
        SUMMARY: Test Event
        DTSTART: invalid-date
        """
    )

    parser = EventParser(event_with_invalid_date, EVENT_LEXICON, MANDATORY_KEYS)

    with pytest.raises(ParserError, match='Invalid date format'):
        parser.run()


def test_event_no_timezone_i():
    sample_event_no_timezone = '''# Mandatory
    SUMMARY: Example summary
    DTSTART: 2024-12-30 09:00
    DTEND: 2024-12-30 09:45'''

    result = parse_event(sample_event_no_timezone, ZoneInfo('Europe/Lisbon'))

    assert f'{result['dtstart'].tzinfo}' == 'Europe/Lisbon'
    assert f'{result['dtend'].tzinfo}' == 'Europe/Lisbon'


def test_event_no_timezone_ii():
    sample_event_no_timezone = '''# Mandatory
    SUMMARY: Example summary
    DTSTART: 2024-12-30 09:00
    DTEND: 2024-12-30 09:45

    # Optional
    LOCATION:
    CATEGORIES:
    TIMEZONE:
    PRIORITY: 5
    ALARM: P0D
    RRULE:
    DESCRIPTION: '''

    result = parse_event(sample_event_no_timezone, ZoneInfo('Europe/Lisbon'))

    assert f'{result['dtstart'].tzinfo}' == 'Europe/Lisbon'
    assert f'{result['dtend'].tzinfo}' == 'Europe/Lisbon'


def test_event_empty_event():
    sample_event_empty = ''

    with pytest.raises(ParserError,
                       match='Missing mandatory key: "dtstart"'):
        parse_event(sample_event_empty, ZoneInfo('Europe/Lisbon'))
