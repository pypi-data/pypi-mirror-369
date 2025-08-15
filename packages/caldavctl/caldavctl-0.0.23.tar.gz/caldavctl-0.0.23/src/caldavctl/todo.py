# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
import uuid

import click

from caldavctl import dav, get_name
from caldavctl.templates import render
from caldavctl.utils import ESCAPE_SEQUENCES

from icalendar import Todo


@click.command('list', options_metavar='[options]')
@click.option('-sd', '--show-description', is_flag=True, show_default=True, default=False,
              help='Show the todo\'s description.')
@click.option('-si', '--show-uid', is_flag=True, show_default=True, default=False,
              help='Show the todo\'s UID.')
@click.option('-a', '--all', is_flag=True, show_default=True, default=False,
              help='Show all todos, including completed todos.')
@click.option('-tf', '--template-file', default='todo.txt',
              help='Template used to format the output', metavar='<file>')
@click.option('--json',
              is_flag=True, show_default=True, default=False,
              help='Output JSON instead of using a template')
@click.pass_obj
def list_todos(context, show_description, show_uid, all, template_file, json):
    '''
    List todos from the default server and default calendar

    caldavctl uses templates to display the list command output by default. If
    not specified otherwise it uses the `todo.txt` template. The used template
    can be specified using the -tf/--template-file option. First we check the
    current directory for the existence of the file. If it's not found we check
    the `<share>/caldavctl/templates` directory.

    Currently we have the following templates:

    \b
        * todo.txt - output with colors (default)
        * todo-nocolor.txt
        * todo.html

    If the --json flag is used, the list command will output JSON. This output
    does not go through the template system, and any template options will be
    ignored when using --json.
    '''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    todo_list = []
    with dav.caldav_calendar(server, calendar_id) as calendar:
        # Check if the calendar supports events:
        if 'VTODO' not in calendar.get_supported_components():
            raise click.UsageError(f'This calendar "{calendar.name}" does not support todos.')
        # Get events in time range
        todos = calendar.todos(include_completed=all)
        for todo in todos:
            td = todo.icalendar_component
            todo_context = {
                'summary': td.get('summary'),
                'status': td.get('status', ''),
                'completed': bool(td.get('status', '')),
                'percent': td.get('percent-complete', 0),
                'description': td.get('description', ''),
                'uid': td.get('uid'),
            }
            todo_list.append(todo_context)

    if json:
        import json
        click.echo(json.dumps(todo_list))
        return

    # Template output
    template_context = {
        'show_uid': show_uid,
        'show_description': show_description,
        'todo_list': todo_list,
    }
    template_context.update(ESCAPE_SEQUENCES)

    txt = render(get_name(), template_file, template_context)
    click.echo(txt.strip())


@click.command('create', options_metavar='[options]')
@click.argument('summary', metavar='<summary>')
@click.option('--description', metavar='<description>')
@click.option('--due-date', metavar='<yyyy-mm-dd>')
@click.option('--priority', metavar='<int>')
@click.pass_obj
def create_todo(context, summary, description, due_date, priority):
    '''Create a todo on the server'''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    tz = context['config'].tz()

    with dav.caldav_calendar(server, calendar_id) as calendar:
        todo = Todo()

        todo.add('uid', str(uuid.uuid4()))
        todo.add('summary', summary)
        if description:
            todo.add('description', description)
        if due_date:
            try:
                dt = datetime.fromisoformat(due_date).replace(tzinfo=tz)
            except ValueError:
                raise click.UsageError(f'Invalid value for due date "{due_date}"')
            todo.add('due', dt)
        if priority:
            todo.add('priority', priority)
        todo.add('created', datetime.now(tz))
        todo.add('last-modified', datetime.now(tz))

        # Convert the todo to a string
        todo_string = todo.to_ical().decode('utf-8')

        try:
            calendar.save_event(todo_string)
            click.echo(f"todo created successfully: {summary}")
        except Exception as e:
            click.echo(f"Error creating todo: {e}")


@click.command('delete', options_metavar='[options]')
@click.argument('todo_id', metavar='<uid>')
@click.pass_obj
def delete_todo(context, todo_id):
    '''Delete a todo on the server'''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()

    with dav.caldav_calendar_todo(server, calendar_id, todo_id) as todo:
        todo.delete()
    click.echo('Todo deleted')


@click.command('toggle', options_metavar='[options]')
@click.argument('todo_id', metavar='<uid>')
@click.pass_obj
def toggle_todo_complete(context, todo_id):
    '''Toggle todo completed'''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    tz = context['config'].tz()

    with dav.caldav_calendar_todo(server, calendar_id, todo_id) as todo:
        if todo.icalendar_component.get('status', ''):
            del todo.icalendar_component['status']
            del todo.icalendar_component['completed']
            click.echo('Todo is pending')
        else:
            todo.icalendar_component.add('status', 'COMPLETED')
            todo.icalendar_component.add('completed', datetime.now(tz))
            click.echo('Todo completed')
        todo.save()


@click.command('percentage', options_metavar='[options]')
@click.argument('todo_id', metavar='<uid>')
@click.argument('percent', type=click.IntRange(0, 100), metavar='<int>')
@click.pass_obj
def percentage_complete(context, todo_id, percent):
    '''Set percentage completed'''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    tz = context['config'].tz()

    with dav.caldav_calendar_todo(server, calendar_id, todo_id) as todo:
        if percent == todo.icalendar_component.get('percent-complete', 0):
            click.echo('No change!')
            return
        if 'percent-complete' in todo.icalendar_component:
            del todo.icalendar_component['percent-complete']
        todo.icalendar_component.add('percent-complete', percent)
        if todo.icalendar_component.get('status', ''):
            del todo.icalendar_component['status']
            del todo.icalendar_component['completed']
        if percent == 100:
            todo.icalendar_component.add('status', 'COMPLETED')
            todo.icalendar_component.add('completed', datetime.now(tz))
            click.echo('Todo completed')
        else:
            click.echo('Percentage set')
        todo.save()
