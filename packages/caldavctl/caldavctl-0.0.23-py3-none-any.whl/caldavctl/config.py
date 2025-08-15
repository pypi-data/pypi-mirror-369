# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

'''
Configuration Management
'''

import os
import os.path
import platform
import tomllib
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import click
from platformdirs import user_config_dir

from caldavctl.utils import deep_merge_dict


class Config:
    def __init__(self, config_file, name=None, username=None, password=None,
                 url=None, timezone=None, default_server=None,
                 default_calendar=None):
        # Load the configuration file
        self.config = self.load_config_file(config_file)
        # Set the timezone:
        tz_name = self.config['default']['timezone']
        if isinstance(tz_name, str):
            try:
                self.config['default']['timezone'] = ZoneInfo(tz_name)
            except ZoneInfoNotFoundError:
                raise click.UsageError(f'Unknown timezone "{tz_name}"')
        # Add a server from the command line or environment variables if it exists
        self.merge_server(name, username, password, url)
        # Merge defaults from the command line if they exist
        self.merge_defaults(default_server, default_calendar, timezone)

    def check_file_permission(self, config_file):
        '''Check if the configuration file has 400 or 600 permissions'''
        if platform.system() == 'Windows':
            return
        file_perm = os.stat(config_file).st_mode & 0o777
        if file_perm != 0o400 and file_perm != 0o600:
            raise click.UsageError(f'The configuration {config_file} file must be readable '
                                   'only by the user.')

    def validate_config(self, config):
        def check_allowed_keys(allowed, real):
            if not real.issubset(allowed):
                unknown = ','.join(list(real - allowed))
                raise click.UsageError(f'Unknown configuration directive: {unknown}')

        # Check first level keys
        allowed_keys = {'server', 'default', 'option'}
        check_allowed_keys(allowed_keys, set(config.keys()))

        # Check defaults
        allowed_defaults = {'server', 'calendar', 'timezone'}
        if 'default' in config:
            check_allowed_keys(allowed_defaults, set(config['default'].keys()))

        # Check servers:
        allowed_server = {'username', 'password', 'url'}
        if 'server' in config:
            for server in config['server']:
                real = set(config['server'][server])
                check_allowed_keys(allowed_server, real)
                if allowed_server - real:
                    missing = ', '.join(list(allowed_server - real))
                    raise click.UsageError(f'Missing configuration keys: {missing}')

    def load_config_file(self, config_file):
        config = {
            'default': {
                'calendar': None,
                'server': None,
                'timezone': ZoneInfo('UTC'),
            },
            'server': {},
            'option': []
        }
        if not config_file:
            # If no configuration file is declared,
            # use the default ~/.config/caldavctl/config.toml
            # in most systems
            config_dir = user_config_dir('caldavctl')
            config_file = os.path.join(config_dir, 'config.toml')

        # Store the config file
        self.config_file = config_file

        if os.path.exists(config_file):
            self.check_file_permission(config_file)

            # Read the configuration file
            try:
                with open(config_file, 'rb') as f:
                    conf = tomllib.load(f)
                self.validate_config(conf)
                deep_merge_dict(conf, config)
            except tomllib.TOMLDecodeError as error:
                raise click.UsageError(f'Invalid configuration file: {error}')

        return config

    def merge_server(self, name, username, password, url):
        '''Merge a server with the configuration'''
        if name or username:
            name = name if name else 'default'
            self.config['server'][name] = {
                'username': username,
                'password': password,
                'url': url
            }

    def merge_defaults(self, server, calendar, timezone):
        if server:
            self.config['default']['server'] = server
        if calendar:
            self.config['default']['calendar'] = calendar
        if timezone:
            try:
                self.config['default']['timezone'] = ZoneInfo(timezone)
            except ZoneInfoNotFoundError:
                raise click.UsageError(f'Unknown timezone "{timezone}"')

    def tz(self):
        return self.config['default']['timezone']

    def servers(self):
        '''Iter all the servers'''
        for server_name in self.config['server']:
            yield self.get_server(server_name)

    def get_server(self, server_name=None):
        '''Get the default server or server_name'''
        if not server_name:
            try:
                server_name = self.config['default']['server']
                if not server_name:
                    raise click.UsageError('There is no default server defined and you did not '
                                           'indicate one with the --server option.')
            except KeyError:
                raise click.UsageError('There is no default server defined and you did not '
                                       'indicate one with the --server option.')
        server = self.config['server'][server_name]
        return server_name, server

    def get_calendar(self, calendar=None):
        if not calendar:
            try:
                calendar = self.config['default']['calendar']
            except KeyError:
                raise click.UsageError('There is no default calendar defined and you did not '
                                       'indicate one with the --calendar option.')
        return calendar
