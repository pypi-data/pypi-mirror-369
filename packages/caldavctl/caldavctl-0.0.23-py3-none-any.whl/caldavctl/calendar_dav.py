# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import caldav
import click
from caldav.lib import error

from caldavctl import dav, get_name
from caldavctl.templates import render
from caldavctl.utils import (
    ESCAPE_SEQUENCES,
)


# CALENDARS

@click.command('list', options_metavar='[options]')
@click.option('-tf', '--template-file', default='calendar.txt',
              help='Template used to format the output', metavar='<file>')
@click.option('--json',
              is_flag=True, show_default=True, default=False,
              help='Output JSON instead of using a template')
@click.pass_obj
def list_calendars(context, template_file, json):
    '''
    List the available calendars present on the server or servers

    caldavctl uses templates to display the list command output by default. If
    not specified otherwise it uses the `calendar.txt` template. The used
    template can be specified using the -tf/--template-file option. First we
    check the current directory for the existence of the template file. If it's
    not found we check the `<share>/caldavctl/templates` directory.

    Currently we have the following templates:

    \b
        * calendar.txt - output with colors (default)
        * calendar-nocolor.txt
        * calendar.html

    If the --json flag is used, the list command will output JSON. This output
    does not go through the template system, and any template options will be
    ignored when using --json.
    '''
    calendar_list = []
    for name, server in context['config'].servers():
        with caldav.DAVClient(**server) as client:
            for calendar in client.principal().calendars():
                calendar_list.append({
                    'server': name,
                    'name': calendar.name,
                    'id': calendar.id,
                    'components': calendar.get_supported_components(),
                    'url': f'{calendar.url}',
                })

    if json:
        import json
        click.echo(json.dumps(calendar_list))
        return

    # Template output
    template_context = {
        'calendar_list': calendar_list,
    }
    template_context.update(ESCAPE_SEQUENCES)

    txt = render(get_name(), template_file, template_context)
    click.echo(txt.strip())


@click.command('create', options_metavar='[options]')
@click.argument('name', metavar='<calendar>')
@click.option('--cal-id', help='Calendar UID to use in the new calendar', metavar='<uid>')
@click.pass_obj
def create_calendar(context, name, cal_id=None):
    '''
    Create a calendar on the default server or optionally in another server

    <calendar> - calendar name
    '''
    _, server = context['config'].get_server()

    with caldav.DAVClient(**server) as client:
        principal = client.principal()
        try:
            new_calendar = principal.make_calendar(name=name, cal_id=cal_id)
        except error.AuthorizationError as msg:
            raise click.UsageError(f'Error creating the calendar (maybe duplicate UID?) with: {msg}')

        print(f'Calendar "{name}" created.')
    return new_calendar


@click.command('delete', options_metavar='[options]')
@click.argument('calendar-id', metavar='<uid>')
@click.pass_obj
def delete_calendar(context, calendar_id):
    '''
    Delete a calendar from the default server or optionally from another
    server. It's possible to have calendars with the same name, so we use the
    id to identify the calendar to delete.
    '''
    _, server = context['config'].get_server()

    with dav.caldav_calendar(server, calendar_id) as calendar:
        name = calendar.name
        calendar.delete()
        print(f'Calendar "{name}" deleted.')
