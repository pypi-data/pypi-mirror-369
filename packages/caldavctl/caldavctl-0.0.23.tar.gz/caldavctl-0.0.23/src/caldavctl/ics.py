# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import uuid

import click
import icalendar

from caldavctl import dav


@click.command('get-todo', options_metavar='[options]')
@click.argument('todo_uid', metavar='<uid>')
@click.option('-f', '--file', type=click.File('w'), default=sys.stdout, metavar='<file>')
@click.pass_obj
def get_todo(context, todo_uid, file):
    '''Get the ICS file of a todo'''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()

    with dav.caldav_calendar_todo(server, calendar_id, todo_uid) as todo:
        file.write(str(todo.icalendar_instance.to_ical(), 'utf-8'))


@click.command('create-todo', options_metavar='[options]')
@click.argument('file', type=click.File('r'), default=sys.stdin, metavar='<file>')
@click.pass_obj
def create_todo(context, file):
    '''
    Create a todo from an existing ICS File

    If the ICS already has a UID, and if a todo already exists on the server
    with that ICS, them the server copy will be modified with the file
    contents.
    '''
    # Read the ICS file
    ics_content = file.read()

    # Parse the ICS file
    cal = icalendar.Calendar.from_ical(ics_content)

    # Find the first Todo component in the file
    todo = None
    for component in cal.walk():
        if component.name == 'VTODO':
            todo = component
            break

    if not todo:
        raise click.UsageError('No Todo found in the ICS file')

    # Ensure the todo has a unique identifier
    if 'uid' not in todo:
        todo['uid'] = str(uuid.uuid4())

    # Convert the todo back to a string
    todo_string = todo.to_ical().decode('utf-8')

    # Save the todo to the calendar
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    with dav.caldav_calendar(server, calendar_id) as calendar:
        calendar.save_event(todo_string)

    click.echo('Todo created successfully')


@click.command('get-event', options_metavar='[options]')
@click.argument('event_uid', metavar='<uid>')
@click.option('-f', '--file', type=click.File('w'), default=sys.stdout, help='Output file', metavar='<file>')
@click.pass_obj
def get_event(context, event_uid, file):
    '''Get the ICS file of a event'''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()

    with dav.caldav_calendar_event(server, calendar_id, event_uid) as event:
        file.write(str(event.icalendar_instance.to_ical(), 'utf-8'))


@click.command('create-event', options_metavar='[options]')
@click.argument('file', type=click.File('r'), default=sys.stdin, metavar='<file>')
@click.pass_obj
def create_event(context, file):
    '''
    Create an event from an existing ICS File

    If the ICS already has a UID, and if a event already exists on the server
    with that ICS, them the server copy will be modified with the file
    contents.
    '''
    # Read the ICS file
    ics_content = file.read()

    # Parse the ICS file
    cal = icalendar.Calendar.from_ical(ics_content)

    # Find the first Event component in the file
    event = None
    for component in cal.walk():
        if component.name == 'VEVENT':
            event = component
            break

    if not event:
        raise click.UsageError('No Event found in the ICS file')

    # Ensure the event has a unique identifier
    if 'uid' not in event:
        event['uid'] = str(uuid.uuid4())

    # Convert the event back to a string
    event_string = event.to_ical().decode('utf-8')

    # Save the todo to the calendar
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    with dav.caldav_calendar(server, calendar_id) as calendar:
        calendar.save_event(event_string)

    click.echo('Event created successfully')
