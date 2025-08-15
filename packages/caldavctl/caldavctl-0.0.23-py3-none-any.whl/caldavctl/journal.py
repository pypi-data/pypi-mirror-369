# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime, timedelta

import click

from caldavctl import dav
from caldavctl.click_utils import create_compatibility_check
from caldavctl.utils import edit_text_with_editor, to_datetime

exclusive_option = create_compatibility_check(
    ['today', 'week', 'dtstart', 'dtend'],
    [['dtstart', 'dtend']])


@click.command('list')
@click.option('-t', '--today',
              is_flag=True, show_default=True, default=False,
              callback=exclusive_option, help='Today\'s journals',)
@click.option('-w', '--week',
              is_flag=True, show_default=True, default=False,
              callback=exclusive_option, help='This week\'s journals')
@click.option('-s', '--dtstart',
              callback=exclusive_option, help='Date range, start date')
@click.option('-e', '--dtend',
              callback=exclusive_option, help='Date range, end date')
@click.option('-d', '--show_description',
              is_flag=True, show_default=True, default=False,
              help='Show the journal\'s description.')
@click.pass_obj
def list_journals(context, today, week, dtstart, dtend, show_description):
    '''
    List journals from the server list.
    '''
    raise click.UsageError('caldav does not support journal searching. '
                           'https://github.com/python-caldav/caldav/issues/237')

    tz = context['config'].tz()
    start_date = None
    end_date = None

    if today:
        start_date = datetime.now().replace(hour=0, minute=0, second=0)
        end_date = datetime.now().replace(hour=23, minute=59, second=59)
    elif week:
        today_date = datetime.now().replace(hour=0, minute=0, second=0)
        start_date = today_date - timedelta(days=today_date.weekday())
        end_date = start_date + timedelta(days=6)
        end_date = end_date.replace(hour=23, minute=59, second=59)
    elif dtstart and dtend:
        if dtstart:
            start_date = to_datetime(dtstart, tz)
        else:
            start_date = datetime(1900, 1, 1, tzinfo=tz)
        if dtend:
            end_date = to_datetime(dtend, tz)
        else:
            end_date = datetime(5000, 1, 1, tzinfo=tz)
    else:
        raise click.UsageError('You have to specify a time frame, for example with -t or -w.')

    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    with dav.caldav_calendar(server, calendar_id) as calendar:
        # Check if the calendar supports journals:
        if 'VJOURNAL' not in calendar.get_supported_components():
            raise click.UsageError('This calendar does not support journals.')

        # Get journals in time range
        journals = calendar.search(
            start=start_date,
            end=end_date,
            journal=True,
            expand=True,
            sort_keys=['dtstart']
        )
        for journal in journals:
            ev = journal.icalendar_component
            date = ev.get('dtstart').dt
            summary = ev.get('summary', '')
            description = ev.get('description', '')
            uid = ev.get('uid')

            if isinstance(date, datetime):
                print(f'{date.strftime('%Y-%m-%d %H:%M')} - {summary} - {uid}')
            else:
                print(f'{date} (day) - {summary} - {uid}')
            if show_description and description.strip():
                print(description)
