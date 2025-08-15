# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from datetime import datetime, timedelta

import click
from caldav.lib import error

import caldavctl.patch_click
from caldavctl import dav, get_name
from caldavctl.click_utils import create_compatibility_check
from caldavctl.event_builder import event_builder, parse_event
from caldavctl.object_parser import ParserError
from caldavctl.templates import render
from caldavctl.utils import (
    ESCAPE_SEQUENCES,
    calmonth,
    edit_text_with_editor,
    timedelta_to_duration,
    to_datetime)

# Configuration

EMPTY_EVENT = '''# Mandatory
DTSTART: %(start)s
DURATION: PT45M
# Use either DURATION or DTEND but not both
# DTEND: %(end)s

%(cal)s

# Recommended
SUMMARY:

# Optional
LOCATION:
CATEGORIES:
TIMEZONE:
PRIORITY: 5
ALARM: P0D
# RRULE: [[FREQ=DAILY;COUNT=3]]
DESCRIPTION: [[ ]]

# NOTES:
#
#   * Date and time:
#       * The dates must be in iso format, for instance: 2024-12-29 13:45;
#       * The timezone used is the one defined by default or the one defined in
#         the "TIMEZONE" key;
#       * The default time zone is "%(tz)s";
#       * You can use the command "caldavctl utils list-timezones" to list the
#         available time zones;
#       * The duration key has the format defined in:
#           https://www.rfc-editor.org/rfc/rfc5545#section-3.3.6
#       * The default duration is 45 minutes;
#   * Categories: the categories are a comma separated list;
#   * Priority: 1 - highest priority, 9 - lowest priority;
#   * Description: The description can be multi line, just make sure it's
#     delimited by [[ ]];
#   * Recurrence Rule (RRULE) allows scheduling recurring events. The syntaxe
#     used is defined in:
#     https://www.rfc-editor.org/rfc/rfc5545#section-3.3.10
#     The recurrence rule must be enclosed in [[ ]]
#   * Alarms:
#       * By default an alarm is defined the moment the event begins;
#       * The alarms are defined using:
#           ALARM: <trigger> [<description>]
#       * The trigger is defined according to:
#           https://www.rfc-editor.org/rfc/rfc5545#section-3.3.6
#       * For example, to trigger an alarm 30 minutes before the event start, use:
#           ALARM: -PT30M
#       * The alarm description is optional.
'''


# Commands:

exclusive_option = create_compatibility_check(
    ['today', 'week', 'dtstart', 'dtend', 'day'],  # Exclusive options
    [['dtstart', 'dtend']])  # Except these two that can be used together


@click.command('list', options_metavar='[options]')
@click.option('-t', '--today',
              is_flag=False, flag_value=0, default=None, type=int,
              callback=exclusive_option, help='Today\'s events', metavar='<offset>')
@click.option('-w', '--week',
              is_flag=False, flag_value=0, default=None, type=int,
              callback=exclusive_option, help='Week events', metavar='<offset>')
@click.option('-s', '--dtstart',
              callback=exclusive_option, help='Date range, start date', metavar='<yyyy-mm-dd>')
@click.option('-e', '--dtend',
              callback=exclusive_option, help='Date range, end date', metavar='<yyyy-mm-dd>')
@click.option('-d', '--day',
              callback=exclusive_option, help='Events on the day', metavar='<yyyy-mm-dd>')
@click.option('-sd', '--show-description',
              is_flag=True, show_default=True, default=False,
              help='Show the event\'s description.')
@click.option('-si', '--show-uid',
              is_flag=True, show_default=True, default=False,
              help='Show the event\'s UID.')
@click.option('-stz', '--show-timezone',
              is_flag=True, show_default=True, default=False,
              help='Show the event\'s time zones in the dates displayed.')
@click.option('-tf', '--template-file', default='event.txt',
              help='Template used to format the output', metavar='<file>')
@click.option('--json',
              is_flag=True, show_default=True, default=False,
              help='Output JSON instead of using a template')
@click.pass_obj
def list_events(context, today, week, dtstart, dtend, day, show_description, show_uid, show_timezone, template_file, json):
    '''
    List events from the server list

    The date range can be specified in several ways. The --week and --today
    options can take an integer offset, either positive or negative. For
    instace to see the events from last week we can use --week -1, to see the
    events for tomorrow use -t 1.

    caldavctl uses templates to display the list command output by default. If
    not specified otherwise  it uses the `event.txt` template. The used
    template can be specified using the -tf/--template-file option. First we
    check the current directory for the existence of the file. If it's not
    found a number of directories are checked for the template file. This
    command lists the template directories:

    ```
    caldavctl utils template-directories
    ```

    Currently we have the following templates:

    \b
        * event.txt - output with colors (default)
        * event-nocolor.txt
        * event.html
        * event-fancy.html

    If the --json flag is used, the list command will output JSON. This output
    does not go through the template system, and any template options will be
    ignored when using --json.
    '''
    tz = context['config'].tz()
    start_date = None
    end_date = None

    # Compute the start and end dates used on the search
    if today is not None:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, tzinfo=tz)
        end_date = datetime.now().replace(hour=23, minute=59, second=59, tzinfo=tz)
        # Apply day offset
        start_date += timedelta(days=today)
        end_date += timedelta(days=today)
    elif week is not None:
        today_date = datetime.now().replace(hour=0, minute=0, second=0, tzinfo=tz)
        start_date = today_date - timedelta(days=today_date.weekday())
        end_date = start_date + timedelta(days=6)
        end_date = end_date.replace(hour=23, minute=59, second=59)
        # Apply week offset
        start_date += timedelta(weeks=week)
        end_date += timedelta(weeks=week)
    elif dtstart or dtend:
        if dtstart:
            start_date = to_datetime(dtstart, tz)
        else:
            start_date = datetime(1900, 1, 1, tzinfo=tz)
        if dtend:
            end_date = to_datetime(dtend, tz)
        else:
            end_date = datetime(5000, 1, 1, tzinfo=tz)
    elif day:
        try:
            dt = datetime.fromisoformat(day)
            start_date = dt.replace(hour=0, minute=0, second=0, tzinfo=tz)
            end_date = dt.replace(hour=23, minute=59, second=59, tzinfo=tz)
        except ValueError:
            raise click.UsageError(f'Invalid date "{day}"')
    else:
        raise click.UsageError('You have to specify a time frame, for example with -t or -w.')

    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()
    event_list = []
    with dav.caldav_calendar(server, calendar_id) as calendar:
        # Check if the calendar supports events:
        if 'VEVENT' not in calendar.get_supported_components():
            raise click.UsageError('This calendar does not support events.')

        # Get events in time range
        events = calendar.search(
            start=start_date,
            end=end_date,
            event=True,
            expand=True,
            sort_keys=['dtstart']
        )
        for event in events:
            ev = event.icalendar_component
            ev_start_date = ev.get('dtstart').dt
            if isinstance(ev_start_date, datetime):
                ev_start_date = ev_start_date.astimezone(tz)
            if 'dtend' in ev:
                ev_end_date = ev.get('dtend').dt
                if isinstance(ev_end_date, datetime):
                    ev_end_date = ev_end_date.astimezone(tz)
                duration = ev_end_date - ev_start_date
            else:
                duration = ev.get('duration').dt
                ev_end_date = ev_start_date + duration
            event_context = {
                'start_date': ev_start_date.strftime('%Y-%m-%d %H:%M') if isinstance(ev_start_date, datetime) else f'{ev_start_date} (day)',
                'start_date_tz': f'{ev_start_date.tzinfo}' if isinstance(ev_start_date, datetime) else None,
                'end_date': ev_end_date.strftime('%Y-%m-%d %H:%M') if isinstance(ev_end_date, datetime) else f'{ev_end_date} (day)',
                'end_date_tz': f'{ev_end_date.tzinfo}' if isinstance(ev_end_date, datetime) else None,
                'duration': f'{duration}',
                'duration_st': timedelta_to_duration(duration),
                'summary': ev.get('summary', ''),
                'description': ev.get('description', ''),
                'categories': [
                    cat if isinstance(cat, str) else cat.cats[0]
                    for cat in ev.get('categories', [])],
                'location': ev.get('location', ''),
                'uid': ev.get('uid')
            }
            event_list.append(event_context)

    if json:
        import json
        click.echo(json.dumps(event_list))
        return

    # Template output
    template_context = {
        'show_uid': show_uid,
        'show_description': show_description,
        'show_timezone': show_timezone,
        'event_list': event_list,
    }
    template_context.update(ESCAPE_SEQUENCES)

    txt = render(get_name(), template_file, template_context)
    click.echo(txt.strip())


@click.command('create', options_metavar='[options]')
@click.option('-f', '--file',
              type=click.File('r'), default=sys.stdin,
              help='Create event from this file', metavar='<file>')
@click.option('-e', '--edit', is_flag=True, default=False, help='Edit the event on a text editor?')
@click.option('--dry-run', is_flag=True, default=False, help='Show only the iCalendar generated')
@click.pass_obj
def create_event(context, file, edit, dry_run):
    '''
    Create new event

    The event data can be read from stdin or from a file. Optionally the event
    can be edited using the default $EDITOR. If the option to edit is enabled
    and no file is defined using -f/--file, then an empty event is opened.

    \b
    CalDAV CLI Event Configuration File Format
    ==========================================

    This format is used to define or edit calendar events via a simple
    key-value configuration file.

    \b
    Overview
    --------

    \b
    - Each line defines a field using the format: `KEY: VALUE`.
    - Lines starting with `#` are treated as comments and ignored.
    - Multi-line values (e.g., `DESCRIPTION`, `RRULE`) must be enclosed in `[[ ]]`.

    \b
    Sections
    --------

    \b
    Mandatory Fields
    ----------------

    \b
    DTSTART :
        Start date and time of the event.
        Format: `YYYY-MM-DD HH:MM`
        Example: `DTSTART: 2025-08-05 09:00`

    \b
    DURATION :
        Duration of the event based in the ISO 8601 format.
        See: https://www.rfc-editor.org/rfc/rfc5545#section-3.3.6
        Example: `DURATION: PT45M`

    \b
    DTEND :
        End date and time of the event.
        Format: `YYYY-MM-DD HH:MM`

    \b
        Notes
        -----
        Either `DURATION` or `DTEND` must be provided, but not both.

    \b
    Recommended Fields
    ------------------

    \b
    SUMMARY :
        Short summary or title of the event.
        Example: `SUMMARY: Team Meeting`

    \b
    Optional Fields
    ---------------

    \b
    LOCATION :
        Location where the event takes place.
        Example: `LOCATION: Conference Room A`

    \b
    CATEGORIES :
        Comma-separated list of categories/tags.
        Example: `CATEGORIES: Work,Team`

    \b
    TIMEZONE :
        Time zone in which to interpret the date/time values.
        Example: `TIMEZONE: Europe/Lisbon`

    \b
    PRIORITY :
        Priority of the event (1 = highest, 9 = lowest).
        Example: `PRIORITY: 5`

    \b
    ALARM :
        Defines when a reminder is triggered for the event.
        Format: `ALARM: <TRIGGER> [<DESCRIPTION>]`
        Examples:
            - `ALARM: P0D` (trigger at start)
            - `ALARM: -PT30M Reminder: Prepare for meeting` (trigger half an
              hour before)

    \b
    RRULE :
        Recurrence rule using RFC 5545 format.
        Must be enclosed in `[[ ]]`.
        See: https://www.rfc-editor.org/rfc/rfc5545#section-3.3.10
        Example: `RRULE: [[FREQ=DAILY;COUNT=3]]`

    \b
    DESCRIPTION :
        Optional multi-line description of the event.
        Must be enclosed in `[[ ]]`.
        Example:
            ```
            DESCRIPTION: [[
            Planning session with the engineering team.
            Agenda:
            - Sprint Review
            - Roadmap discussion
            ]]
            ```

    \b
    Comment Syntax
    --------------

    Lines beginning with `#` are treated as comments and ignored.

    \b
    Other Notes
    -----------

    \b
    - Date/Time values must be in ISO format: `YYYY-MM-DD HH:MM`
    - DURATION follows ISO 8601 duration syntax (e.g., `PT45M`, `P1DT2H`)
    - Use `caldavctl utils list-timezones` to see all available time zones
    - Default values:
        - DURATION: 45 minutes
        - ALARM: P0D (triggers at event start)
    - DESCRIPTION may use double square brackets `[[ ]]` to support multi-line
      or special content
    - RRULE must use double square brackets `[[ ]]` to support multiple
      key-value pairs separated by semicolons

    \b
    Example
    -------

    \b
    ```
    DTSTART: 2025-08-05 09:00
    DURATION: PT45M
    SUMMARY: Weekly Standup
    LOCATION: Zoom
    CATEGORIES: Work,Remote
    TIMEZONE: Europe/Lisbon
    PRIORITY: 3
    ALARM: -PT15M Reminder: Standup in 15 minutes
    RRULE: [[FREQ=WEEKLY;BYDAY=MO;COUNT=10]]
    DESCRIPTION: [[
    Weekly check-in with the team to discuss progress
    and blockers for the current sprint.
    ]]
    ```
    '''
    tz = context['config'].tz()
    # Read the event definition
    if edit and file is sys.stdin:
        # No file specified using an empty event
        tomorrow = datetime.now() + timedelta(days=1)
        event_string = EMPTY_EVENT % {
            'tz': f'{tz}',
            'start': tomorrow.replace(hour=9, minute=0, second=0).strftime('%Y-%m-%d %H:%M'),
            'end': tomorrow.replace(hour=9, minute=45, second=0).strftime('%Y-%m-%d %H:%M'),
            'cal': '\n'.join([('# ' + ln).strip() for ln in calmonth(tomorrow.year, tomorrow.month, 3)])
        }
    else:
        event_string = file.read()

    if edit:
        # Edit the file in $VISUAL or $EDITOR
        old_string = event_string
        event_string = edit_text_with_editor(event_string, suffix='.calendar_event')
        if old_string == event_string:
            click.confirm('No changes made. Do you want to continue?', abort=True)

    try:
        event_data = parse_event(event_string, tz)
    except ParserError as msg:
        raise click.UsageError(msg)

    event_ics = event_builder(event_data, tz)

    if dry_run:
        click.echo(event_ics)
    else:
        # Save the event to the calendar
        _, server = context['config'].get_server()
        calendar_id = context['config'].get_calendar()
        with dav.caldav_calendar(server, calendar_id) as calendar:
            # Check if the calendar supports events:
            if 'VEVENT' not in calendar.get_supported_components():
                raise click.UsageError('This calendar does not support events.')
            try:
                calendar.save_event(event_ics)
            except error.AuthorizationError as msg:
                raise click.UsageError(f'Error saving the event to the server: {msg}')

        click.echo('Event created successfully')


@click.command('delete', options_metavar='[options]')
@click.argument('event_id', metavar='<uid>')
@click.pass_obj
def delete_event(context, event_id):
    '''Delete an event on the server'''
    _, server = context['config'].get_server()
    calendar_id = context['config'].get_calendar()

    with dav.caldav_calendar_event(server, calendar_id, event_id) as event:
        event.delete()
    print('Event deleted')
