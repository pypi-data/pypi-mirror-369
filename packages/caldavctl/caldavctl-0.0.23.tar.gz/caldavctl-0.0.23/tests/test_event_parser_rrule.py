# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime

import pytest

from caldavctl.object_parser import ParserError
from caldavctl.event_builder import RRuleValueParser, RRuleParser

rrule_test_data = (
    # Basic frequency tests
    ("FREQ=DAILY", {"freq": "DAILY"}),
    ("FREQ=WEEKLY", {"freq": "WEEKLY"}),
    ("FREQ=MONTHLY", {"freq": "MONTHLY"}),
    ("FREQ=YEARLY", {"freq": "YEARLY"}),
    ("FREQ=HOURLY", {"freq": "HOURLY"}),
    ("FREQ=MINUTELY", {"freq": "MINUTELY"}),
    ("FREQ=SECONDLY", {"freq": "SECONDLY"}),

    # Interval tests
    ("FREQ=DAILY;INTERVAL=1", {"freq": "DAILY", "interval": 1}),
    ("FREQ=WEEKLY;INTERVAL=2", {"freq": "WEEKLY", "interval": 2}),
    ("FREQ=MONTHLY;INTERVAL=3", {"freq": "MONTHLY", "interval": 3}),
    ("FREQ=YEARLY;INTERVAL=10", {"freq": "YEARLY", "interval": 10}),

    # Count tests
    ("FREQ=DAILY;COUNT=5", {"freq": "DAILY", "count": 5}),
    ("FREQ=WEEKLY;COUNT=10", {"freq": "WEEKLY", "count": 10}),

    # Until tests
    ("FREQ=DAILY;UNTIL=20250501T000000Z",
     {"freq": "DAILY",
      "until": datetime.datetime(2025, 5, 1, 0, 0, tzinfo=datetime.timezone.utc)}),
    ("FREQ=MONTHLY;UNTIL=20251231T235959Z",
     {"freq": "MONTHLY",
      "until": datetime.datetime(2025, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)}),

    # ByMonth tests
    ("FREQ=YEARLY;BYMONTH=1", {"freq": "YEARLY", "bymonth": [1]}),
    ("FREQ=YEARLY;BYMONTH=1,2,3", {"freq": "YEARLY", "bymonth": [1, 2, 3]}),
    ("FREQ=YEARLY;BYMONTH=1, 3, 5, 7, 9, 11", {"freq": "YEARLY", "bymonth": [1, 3, 5, 7, 9, 11]}),

    # ByMonthDay tests
    ("FREQ=MONTHLY;BYMONTHDAY=1", {"freq": "MONTHLY", "bymonthday": [1]}),
    ("FREQ=MONTHLY;BYMONTHDAY=1,15", {"freq": "MONTHLY", "bymonthday": [1, 15]}),
    ("FREQ=MONTHLY;BYMONTHDAY=-1", {"freq": "MONTHLY", "bymonthday": [-1]}),  # Last day of month
    ("FREQ=MONTHLY;BYMONTHDAY=1,-1", {"freq": "MONTHLY", "bymonthday": [1, -1]}),  # First and last day

    # ByDay tests
    ("FREQ=WEEKLY;BYDAY=MO", {"freq": "WEEKLY", "byday": ["MO"]}),
    ("FREQ=WEEKLY;BYDAY=MO,WE,FR", {"freq": "WEEKLY", "byday": ["MO", "WE", "FR"]}),
    ("FREQ=MONTHLY;BYDAY=1MO", {"freq": "MONTHLY", "byday": ["1MO"]}),  # First Monday
    ("FREQ=MONTHLY;BYDAY=-1FR", {"freq": "MONTHLY", "byday": ["-1FR"]}),  # Last Friday
    ("FREQ=MONTHLY;BYDAY=1MO,-1FR", {"freq": "MONTHLY", "byday": ["1MO", "-1FR"]}),  # First Monday and last Friday

    # ByYearDay tests
    ("FREQ=YEARLY;BYYEARDAY=1", {"freq": "YEARLY", "byyearday": [1]}),
    ("FREQ=YEARLY;BYYEARDAY=1,100,200", {"freq": "YEARLY", "byyearday": [1, 100, 200]}),
    ("FREQ=YEARLY;BYYEARDAY=-1", {"freq": "YEARLY", "byyearday": [-1]}),  # Last day of year
    ("FREQ=YEARLY;BYYEARDAY=1,-1", {"freq": "YEARLY", "byyearday": [1, -1]}),  # First and last day

    # ByWeekNo tests
    ("FREQ=YEARLY;BYWEEKNO=1", {"freq": "YEARLY", "byweekno": [1]}),
    ("FREQ=YEARLY;BYWEEKNO=1,10,20", {"freq": "YEARLY", "byweekno": [1, 10, 20]}),
    ("FREQ=YEARLY;BYWEEKNO=-1", {"freq": "YEARLY", "byweekno": [-1]}),  # Last week of year
    ("FREQ=YEARLY;BYWEEKNO=1,-1", {"freq": "YEARLY", "byweekno": [1, -1]}),  # First and last week

    # ByHour tests
    ("FREQ=DAILY;BYHOUR=9", {"freq": "DAILY", "byhour": [9]}),
    ("FREQ=DAILY;BYHOUR=9,12,17", {"freq": "DAILY", "byhour": [9, 12, 17]}),
    ("FREQ=DAILY;BYHOUR=10, 22", {"freq": "DAILY", "byhour": [10, 22]}),  # With space after comma

    # ByMinute tests
    ("FREQ=HOURLY;BYMINUTE=0", {"freq": "HOURLY", "byminute": [0]}),
    ("FREQ=HOURLY;BYMINUTE=0,15,30,45", {"freq": "HOURLY", "byminute": [0, 15, 30, 45]}),
    ("FREQ=HOURLY;BYMINUTE=0, 30", {"freq": "HOURLY", "byminute": [0, 30]}),  # With space after comma

    # BySecond tests
    ("FREQ=MINUTELY;BYSECOND=0", {"freq": "MINUTELY", "bysecond": [0]}),
    ("FREQ=MINUTELY;BYSECOND=0,15,30,45", {"freq": "MINUTELY", "bysecond": [0, 15, 30, 45]}),

    # BySetPos tests
    ("FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=1",
     {"freq": "MONTHLY", "byday": ["MO", "TU", "WE", "TH", "FR"], "bysetpos": [1]}),
    ("FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=1,-1",
     {"freq": "MONTHLY", "byday": ["MO", "TU", "WE", "TH", "FR"], "bysetpos": [1, -1]}),

    # WKST tests
    ("FREQ=WEEKLY;INTERVAL=1;WKST=SU", {"freq": "WEEKLY", "interval": 1, "wkst": "SU"}),
    ("FREQ=WEEKLY;INTERVAL=1;WKST=MO", {"freq": "WEEKLY", "interval": 1, "wkst": "MO"}),

    # Complex combinations
    ("FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=1;COUNT=3",
     {"freq": "MONTHLY", "byday": ["MO", "TU", "WE", "TH", "FR"], "bysetpos": [1], "count": 3}),
    ("FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1;UNTIL=20261231T235959Z",
     {"freq": "YEARLY",
      "bymonth": [1],
      "bymonthday": [1],
      "until": datetime.datetime(2026, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
      }),
    ("FREQ=WEEKLY;INTERVAL=2;BYDAY=MO,WE,FR;WKST=SU;COUNT=10",
     {"freq": "WEEKLY", "interval": 2, "byday": ["MO", "WE", "FR"], "wkst": "SU", "count": 10}),
    ("FREQ=DAILY;INTERVAL=1;BYHOUR=9,17;BYMINUTE=0,30",
     {"freq": "DAILY", "interval": 1, "byhour": [9, 17], "byminute": [0, 30]}),

    # Case insensitivity tests
    ("freq=daily", {"freq": "DAILY"}),
    ("Freq=Daily;Interval=1", {"freq": "DAILY", "interval": 1}),

    # Whitespace handling
    ("FREQ=DAILY; INTERVAL=1", {"freq": "DAILY", "interval": 1}),
    ("FREQ=DAILY ; INTERVAL = 1", {"freq": "DAILY", "interval": 1}),

    # Empty values (if applicable)
    ("FREQ=DAILY;BYDAY=", {"freq": "DAILY"}),

    # Multiple semicolons
    (";;FREQ=MINUTELY;", {"freq": "MINUTELY"}),
    ("FREQ=DAILY;;INTERVAL=1", {"freq": "DAILY", "interval": 1}),

    # Trailing semicolon
    ("FREQ=DAILY;", {"freq": "DAILY"}),
    # Leading semicolon
    (";FREQ=DAILY", {"freq": "DAILY"}),
)


@pytest.mark.parametrize('sample, result', rrule_test_data)
def test_rrule_data(sample, result):
    print(f'\nTesting RRULE: {sample}')

    LEXICON = RRuleValueParser.LEXICON
    MANDATORY_KEYS = RRuleValueParser.MANDATORY_KEYS
    tokens = RRuleParser(sample, LEXICON, MANDATORY_KEYS).run()

    print('Computed tokens:', tokens)
    assert tokens == result


rrule_error_test_data = (
    # Invalid frequency value
    ('freq=DIÁRIO', 'Error evaluating key "FREQ": Element DIÁRIO not in allowed values'),

    # Missing mandatory FREQ key
    ('COUNT=5', 'Missing mandatory key: "freq"'),

    # Invalid until date
    ('FREQ=daily;UNTIL=2025FEB',
     'Error evaluating key "UNTIL": Invalid date format for: "2025FEB"'),

    # Invalid day name
    ("FREQ=WEEKLY;BYDAY=FU", 'Error evaluating key "BYDAY": Invalid week day "FU"'),

    # Invalid month number
    ("FREQ=YEARLY;BYMONTH=13",
     'Error evaluating key "BYMONTH": the value is greater than the maximum value'),

    # Both COUNT and UNTIL (should be exclusive)
    ("FREQ=DAILY;COUNT=5;UNTIL=20250501T000000Z",
     'Only one of these keys can be present: count, until'),

    # Invalid INTERVAL (negative value)
    ("FREQ=DAILY;INTERVAL=-1",
     'Error evaluating key "INTERVAL": the value is less than the minimum value'),

    # Multiple equal signs
    ("FREQ==DAILY", 'Error evaluating key "FREQ": Element =DAILY not in allowed values'),
)


@pytest.mark.parametrize('sample, error_message', rrule_error_test_data)
def test_rrule_errors(sample, error_message):
    print(f'\nTesting RRULE: {sample}')
    LEXICON = RRuleValueParser.LEXICON
    MANDATORY_KEYS = RRuleValueParser.MANDATORY_KEYS
    EXLUSIVE_KEYS = RRuleValueParser.EXCLUSIVE_KEYS

    with pytest.raises(ParserError, match=error_message):
        RRuleParser(sample, LEXICON, MANDATORY_KEYS, EXLUSIVE_KEYS).run()
