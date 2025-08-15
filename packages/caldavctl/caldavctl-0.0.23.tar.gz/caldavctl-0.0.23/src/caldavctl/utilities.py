# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

'''
Utilities
'''

import zoneinfo
import pprint

import click

from caldavctl.templates import share_directory_list
from caldavctl import get_name


@click.command('list-timezones', options_metavar='[options]')
@click.option('-s', '--search',
              default=None, metavar='<query>', type=str,
              help='Search time zone')
@click.pass_obj
def list_timezones(context, search):
    '''
    List available time zones

    This command display the available time zones in python's zoneinfo module.
    Use the -s/--search option to search for a specific time zone.
    '''
    timezones = zoneinfo.available_timezones()

    if search:
        result = []
        for tz in timezones:
            if search.lower() in tz.lower():
                result.append(tz)
        if not result:
            result.append(f'No time zone "{search}" found.')
    else:
        result = list(timezones)

    result.sort()

    for tz in result:
        click.echo(tz)


@click.command('config-file')
@click.pass_obj
def config_file(context):
    '''
    Show the paths where the configuration files might reside
    '''
    click.echo(f'The configuration file used is:\n{context['config'].config_file}')


@click.command('current-config')
@click.pass_obj
def current_config(context):
    '''
    Current configuration
    '''
    click.echo('The current configuration is:')
    pprint.pprint(context['config'].config)


@click.command('template-directories')
@click.pass_obj
def template_directories(context):
    '''
    Show the paths from where the templates are read

    When searching for templates we first test for the existence of the
    template in the current directory. If the template is not found the
    template file is searched on the directories listed by this command.

    The existing directories are marked with an asterisk (*).
    '''
    app_name = get_name()
    click.echo('Besides the current durectory, the following paths are\n'
               'considered when searching for templates:\n')
    for path in share_directory_list(app_name):
        p = path / 'templates'
        click.echo(f'{p}{' *' if p.exists() else ''}')
