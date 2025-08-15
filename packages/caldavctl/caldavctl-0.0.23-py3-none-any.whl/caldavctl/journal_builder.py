# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid
from datetime import datetime

from icalendar import Calendar, Journal

from caldavctl import get_name, get_version
from caldavctl.object_parser import DATE, INTEGER, LIST, STRING, TZ, ObjectParser
from caldavctl.utils import check_if_naive

JOURNAL_LEXICON = {
    # token: (type, optional?)
    'summary': (STRING, True),
    'categories': (LIST, True),
    'dtstart': (DATE, False),
    'description': (STRING, True),
    'percentage': (INTEGER, True),
    'timezone': (TZ, True),
    'priority': (INTEGER, True),
}


def parse_journal(journal_icalendar, timezone):
    result = ObjectParser(journal_icalendar, JOURNAL_LEXICON).run()

    # Check if the start and/or end dates are naïve
    tz = timezone if 'timezone' not in result else result['timezone']
    result['dtstart'] = check_if_naive(result['dtstart'], tz)
    result['dtend'] = check_if_naive(result['dtend'], tz)

    return result


def journal_builder(journal_data, tz):
    journal_optional_keys = (
        'summary',
        'location',
        'priority',
        'description',
        'categories',
    )

    calendar = Calendar()
    calendar.add('version', '2.0')
    calendar.add('prodid', f'-//NA//{get_name()} V{get_version()}//EN')

    journal = Journal()
    # Mandatory keys in a VJOURNAL object
    journal.add('uid', str(uuid.uuid4()))
    journal.add('dtstamp', datetime.now(tz))
    journal.add('dtstart', journal_data.get('dtstart'))
    # Optional keys:
    for key in journal_optional_keys:
        if key in journal_data:
            if key == 'categories':
                for category in journal_data.get('categories'):
                    journal.add('categories', category)
            else:
                journal.add(key, journal_data.get(key))

    calendar.add_component(journal)

    return calendar.to_ical().decode('utf-8')
