# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import uuid

import click
import icalendar
from caldav.lib import error

from caldavctl import dav, get_name, get_version

# Commands:


@click.command('backup')
@click.option('-f', '--file', type=click.File('w'), default=sys.stdout,
              metavar='<file>', help='Output file')
@click.pass_obj
def backup_calendar(context, file):
    '''
    Backup calendar to iCalendar file (ics)

    This command outputs the calendar's backup to stdout. Optionally the output
    can be redirected to a file using the -f/--file option.

    ⚠️ Use with care, this feature is highly experimental ⚠️
    '''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()

    calendar_bck = icalendar.Calendar()
    calendar_bck.add('version', '2.0')
    calendar_bck.add('prodid', f'-//NA//{get_name()} V{get_version()}//EN')

    with dav.caldav_calendar(server, calendar_id) as calendar:
        for obj in calendar.objects(load_objects=True):
            # Parse the event's data into a Calendar object
            event_ical = icalendar.Calendar.from_ical(obj.icalendar_instance.to_ical())
            for component in event_ical.walk():
                if component.name in ('VEVENT', 'VTODO', 'VJOURNAL'):  # Filter desired components
                    calendar_bck.add_component(component)

    file.write(str(calendar_bck.to_ical(), 'utf-8'))


@click.command('restore')
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin,
              metavar='<file>', help='Input file')
@click.pass_obj
def restore_calendar(context, file):
    '''
    Restore calendar from an iCalendar file (ics)

    This command restores an ics backup file to the selected calendar. It reads
    its input from stdin. Optionally it can restore the backup from a file
    using the -f/--file option.

    ⚠️ Use with care, this feature is highly experimental ⚠️
    '''
    # Read the ICS file
    ics_content = file.read()

    # Parse the ICS file
    try:
        calendar_rst = icalendar.Calendar.from_ical(ics_content)
    except ValueError as msg:
        raise click.UsageError(f'Error reading the ics file: {msg}')

    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    with dav.caldav_calendar(server, calendar_id) as calendar:
        for component in calendar_rst.walk():
            if component.name in ('VEVENT', 'VTODO', 'VJOURNAL'):
                obj = icalendar.Calendar()
                obj.add('version', '2.0')
                obj.add('prodid', f'-//NA//{get_name()} V{get_version()}//EN')
                org_uid = component["uid"]
                component.uid = str(uuid.uuid4())
                obj.add_component(component)
                obj_string = obj.to_ical().decode('utf-8')
                try:
                    if component.name == 'VEVENT':
                        calendar.save_event(obj_string)
                    elif component.name == 'VTODO':
                        calendar.save_todo(obj_string)
                    elif component.name == 'VJOURNAL':
                        calendar.save_journal(obj_string)
                except error.AuthorizationError as msg:
                    print(f'Error restoring object with uid {org_uid}. '
                          f'with message "{msg}" Skipping.')

    print('Restored.')
