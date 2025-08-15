# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

'''
CalDAV tool
'''

import click

import caldavctl.calendar_dav as calendar
import caldavctl.event as event
import caldavctl.todo as todo
import caldavctl.journal as journal
import caldavctl.ics as ics
import caldavctl.backup as backup
import caldavctl.utilities as utils

from caldavctl import get_version
from caldavctl.config import Config


def print_version(context, param, value):
    # See https://click.palletsprojects.com/en/stable/options/#callbacks-and-eager-options
    if not value or context.resilient_parsing:
        return
    click.echo(f'caldavctl v{get_version()}')
    context.exit(0)


# General options

@click.group(options_metavar='[options]')
@click.option('-c', '--config', 'config_file', envvar='CALDAV_CONFIG', help='Configuration file', metavar='<file>')
@click.option('--name', envvar='CALDAV_NAME', help='Server nickname', metavar='<nickname>')
@click.option('--username', envvar='CALDAV_USERNAME', help='Username on the CalDAV server', metavar='<username>')
@click.option('--passwd', envvar='CALDAV_PASSWD', help='Password on the CalDAV server', metavar='<passwd>')
@click.option('--url', envvar='CALDAV_URL', help='Calendar CalDAV url', metavar='<url>')
@click.option('--timezone', envvar='CALDAV_TIMEZONE', help='Your time zone', metavar='<timezone>')
@click.option('--server', help='Default server (use nickname)', metavar='<nickname>')
@click.option('--calendar', help='Default calendar id', metavar='<uid>')
@click.option('--version', is_flag=True, is_eager=True, expose_value=False, callback=print_version,
              help='caldavctl version')
@click.pass_context
def cli_group(context,
              config_file,
              name, username, passwd, url, timezone,
              server, calendar):
    '''
    caldavctl - command line CalDAV client
    '''

    config = Config(
        config_file,
        name,
        username,
        passwd,
        url,
        timezone,
        server,
        calendar
    )

    context.obj = {
        'config': config,
        'option': []
    }


# CALENDAR

@cli_group.group('calendar', options_metavar='[options]')
@click.pass_context
def calendar_commands(context):
    '''Commands that deal with the calendars on the server'''
    pass


calendar_commands.add_command(calendar.list_calendars)
calendar_commands.add_command(calendar.create_calendar)
calendar_commands.add_command(calendar.delete_calendar)


# EVENTS

@cli_group.group('event', options_metavar='[options]')
@click.pass_context
def event_commands(context):
    '''Event management'''
    pass


event_commands.add_command(event.list_events)
event_commands.add_command(event.create_event)
event_commands.add_command(event.delete_event)


# TODOS

@cli_group.group('todo', options_metavar='[options]')
@click.pass_context
def todo_commands(context):
    '''Todo management'''
    pass


todo_commands.add_command(todo.list_todos)
todo_commands.add_command(todo.create_todo)
todo_commands.add_command(todo.delete_todo)
todo_commands.add_command(todo.toggle_todo_complete)
todo_commands.add_command(todo.percentage_complete)


# JOURNALS

# caldav does not support journal searching. https://github.com/python-caldav/caldav/issues/237
# @cli_group.group('journal', options_metavar='[options]')
# @click.pass_context
# def journal_commands(context):
#     '''Journal management'''
#     pass
#
#
# journal_commands.add_command(journal.list_journals)


# ICS

@cli_group.group('ics', options_metavar='[options]')
@click.pass_context
def ics_commands(context):
    '''iCalendar file operations'''
    pass


ics_commands.add_command(ics.get_todo)
ics_commands.add_command(ics.create_todo)
ics_commands.add_command(ics.get_event)
ics_commands.add_command(ics.create_event)


# Backup

@cli_group.group('br', options_metavar='[options]')
@click.pass_context
def backup_and_restore_commands(context):
    '''Backup or restore a calendar

    ⚠️ Use with care, these features are highly experimental. ⚠️
    '''
    pass


backup_and_restore_commands.add_command(backup.backup_calendar)
backup_and_restore_commands.add_command(backup.restore_calendar)


# Utils

@cli_group.group('utils', options_metavar='[options]')
@click.pass_context
def utilities(context):
    '''Utility commands'''
    pass


utilities.add_command(utils.list_timezones)
utilities.add_command(utils.config_file)
utilities.add_command(utils.current_config)
utilities.add_command(utils.template_directories)


def main():
    cli_group()
