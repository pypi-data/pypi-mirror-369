# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid
from datetime import datetime

from icalendar import Alarm, Calendar, Event, vRecur

from caldavctl import get_name, get_version
from caldavctl.object_parser import (
    DatetimeParser,
    EventParser,
    ParserError,
    RRuleParser,
    TimezoneParser,
    ValueParser,
    choices_parser,
    integer_list_parser,
    integer_parser,
    list_parser,
    string_parser,
)
from caldavctl.utils import check_if_naive, duration_to_timedelta, duration_validation


class AlarmParser(ValueParser):
    def tokenize(self):
        self.tokens = self.txt.split(maxsplit=1)

    def validate(self):
        duration = self.tokens[0].upper().strip()
        if not duration_validation(duration):
            raise ParserError(f'Invalid duration "{self.tokens[0]}" for alarm trigger.')
        self.tokens[0] = duration_to_timedelta(duration)

        alarm = Alarm()
        alarm.add('trigger', self.tokens[0])
        if len(self.tokens) == 2:
            alarm.add('description', self.tokens[1])
        else:
            alarm.add('description', 'Default caldavctl description')
        alarm.add('action', 'display')

        self.value = alarm


class DurationParser(ValueParser):
    def tokenize(self):
        self.tokens = self.txt

    def validate(self):
        duration = self.tokens.upper().strip()
        if not duration_validation(duration):
            raise ParserError(f'Invalid duration "{self.tokens}".')
        self.value = duration_to_timedelta(duration)


class ByDayParser(ValueParser):
    WEEKDAYS = ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA']

    def tokenize(self):
        self.tokens = [el.strip() for el in self.txt.split(',')]

    def validate(self):
        for wday in self.tokens:
            week_day = wday[-2:].upper()
            if week_day not in self.WEEKDAYS:
                raise ParserError(f'Invalid week day "{week_day}"')
            ordwk = wday[:-2]
            if ordwk:
                try:
                    ordwk = int(ordwk)
                except ValueError:
                    raise ParserError(f'Invalid week number "{ordwk}"')
                if abs(ordwk) > 53 or ordwk == 0:
                    raise ParserError(f'Out of range week number "{ordwk}"')

        self.value = self.tokens


class RRuleValueParser(ValueParser):
    LEXICON = {
        'freq': choices_parser(['SECONDLY', 'MINUTELY', 'HOURLY', 'DAILY',
                                'WEEKLY', 'MONTHLY', 'YEARLY']),
        'until': DatetimeParser,
        'count': integer_parser(min=1),
        'interval': integer_parser(min=1),
        'bysecond': integer_list_parser(0, 60),
        'byminute': integer_list_parser(0, 59),
        'byhour': integer_list_parser(0, 23),
        'byday': ByDayParser,
        'bymonthday': integer_list_parser(-31, 31, exception=[0]),
        'byyearday': integer_list_parser(-366, 366, exception=[0]),
        'byweekno': integer_list_parser(-53, 53, exception=[0]),
        'bymonth': integer_list_parser(1, 12),
        'bysetpos': integer_list_parser(-366, 366, exception=[0]),
        'wkst': choices_parser(['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'])
    }

    MANDATORY_KEYS = ('freq',)

    EXCLUSIVE_KEYS = (['count', 'until'],)  # Only one of this keys may be present

    def tokenize(self):
        self.tokens = RRuleParser(
            self.txt,
            self.LEXICON,
            self.MANDATORY_KEYS,
            self.EXCLUSIVE_KEYS).run()

    def validate(self):
        self.value = vRecur(self.tokens)


EVENT_LEXICON = {
    # token: type
    'summary': string_parser(),
    'location': string_parser(),
    'categories': list_parser(),
    'dtstart': DatetimeParser,
    'dtend': DatetimeParser,
    'duration': DurationParser,
    'description': string_parser(),
    'percentage': integer_parser(min=0, max=100),
    'timezone': TimezoneParser,
    'priority': integer_parser(min=1, max=9),
    'alarm': AlarmParser,
    'rrule': RRuleValueParser,
}

OPTIONAL_KEYS = (
    'summary',
    'location',
    'categories',
    'description',
    'percentage',
    'timezone',
    'priority',
    'alarm',
    'rrule',
)

MANDATORY_KEYS = (
    'dtstart',
    ['dtend', 'duration'],  # One of these key must exist
)


def parse_event(event_icalendar, timezone):
    result = EventParser(event_icalendar, EVENT_LEXICON, MANDATORY_KEYS).run()

    # Check if the start and/or end dates are naïve
    tz = timezone if 'timezone' not in result else result['timezone']
    result['dtstart'] = check_if_naive(result['dtstart'], tz)
    if 'dtend' in result:
        result['dtend'] = check_if_naive(result['dtend'], tz)

    return result


def event_builder(event_data, tz):
    calendar = Calendar()
    calendar.add('version', '2.0')
    calendar.add('prodid', f'-//NA//{get_name()} V{get_version()}//EN')

    event = Event()
    # Mandatory keys in a VEVENT object
    event.add('uid', str(uuid.uuid4()))
    event.add('dtstamp', datetime.now(tz))
    event.add('dtstart', event_data['dtstart'])
    if 'dtend' in event_data:
        event.add('dtend', event_data['dtend'])
    elif 'duration' in event_data:
        event.add('duration', event_data['duration'])
    # Optional keys:
    for key in OPTIONAL_KEYS:
        if key in event_data:
            if isinstance(event_data[key], list):
                for value in event_data[key]:
                    if key == 'alarm':
                        event.add_component(value)
                    else:
                        event.add(key, value)
            else:
                if key == 'alarm':
                    event.add_component(event_data[key])
                else:
                    event.add(key, event_data[key])

    calendar.add_component(event)

    return calendar.to_ical().decode('utf-8')
