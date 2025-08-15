# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import contextmanager

import caldav
import caldav.elements.ical
import click
from caldav.lib.error import AuthorizationError
from requests import ConnectionError


@contextmanager
def caldav_calendar(server, calendar_id):
    '''
    Open a connection to a server and return the calendar object
    '''
    # Code to acquire resource, e.g.:
    client = caldav.DAVClient(**server)

    # Retrieve all calendars for the principal
    try:
        principal = client.principal()
    except ConnectionError:
        raise click.UsageError('Connection error, check your server url')
    except AuthorizationError:
        raise click.UsageError('Authorization error, check your user name and password')
    calendars = principal.calendars()

    # Find the calendar by URL or iterate through all calendars
    for cal in calendars:
        if cal.id == calendar_id:  # Match the desired calendar URL
            calendar = cal
            break
    else:
        raise click.UsageError(f'Calendar with id "{calendar_id}" not found')

    # Yield the calendar and close it if appropriate
    try:
        yield calendar
    finally:
        client.close()


@contextmanager
def caldav_calendar_todo(server, calendar_id, todo_id):
    '''
    Open a connection to a server, select a calendar and return a todo object
    '''
    with caldav_calendar(server, calendar_id) as calendar:
        try:
            todo = calendar.todo_by_uid(todo_id)
        except caldav.lib.error.NotFoundError:
            raise click.UsageError(f'Could not find todo {todo_id}.')
        yield todo


@contextmanager
def caldav_calendar_event(server, calendar_id, event_id):
    '''
    Open a connection to a server, select a calendar and return a event object
    '''
    with caldav_calendar(server, calendar_id) as calendar:
        try:
            event = calendar.event_by_uid(event_id)
        except caldav.lib.error.NotFoundError:
            raise click.UsageError(f'Could not find event {event_id}.')
        yield event


@contextmanager
def caldav_calendar_journal(server, calendar_id, journal_id):
    '''
    Open a connection to a server, select a calendar and return a journal object
    '''
    with caldav_calendar(server, calendar_id) as calendar:
        try:
            journal = calendar.journal_by_uid(journal_id)
        except caldav.lib.error.NotFoundError:
            raise click.UsageError(f'Could not find journal {journal_id}.')
        yield journal
