# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from zoneinfo import ZoneInfo

import pytest

import click

from unittest.mock import patch, mock_open
from caldavctl.config import Config


EMPTY_CONFIG = '''
option = []

[default]
calendar = "default_calendar"
server = "default_server"
timezone = "UTC"

[server.default]
username = "default_user"
password = "default_pass"
url = "http://default.url"
'''


@pytest.fixture
def mock_user_config_dir(tmp_path):
    """Mock the user configuration directory."""
    config_dir = tmp_path / 'caldavctl'
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def default_config_file(mock_user_config_dir):
    """Create a default configuration file."""
    config_file = mock_user_config_dir / 'config.toml'
    with open(config_file, 'w') as f:
        f.write(EMPTY_CONFIG)
    return config_file


@patch('caldavctl.config.user_config_dir')
@patch('os.stat')
def test_load_config_file(mock_stat, mock_user_config_dir_func, default_config_file):
    mock_user_config_dir_func.return_value = str(default_config_file.parent)
    mock_stat.return_value.st_mode = 0o600  # Valid permissions

    config = Config(None)

    assert config.config['default']['calendar'] == 'default_calendar'
    assert config.config['default']['server'] == 'default_server'
    assert config.config['default']['timezone'] == ZoneInfo('UTC')
    assert 'default' in config.config['server']
    assert config.config['server']['default']['username'] == 'default_user'
    assert config.config['server']['default']['password'] == 'default_pass'
    assert config.config['server']['default']['url'] == 'http://default.url'


@patch('os.stat')
def test_check_file_permission(mock_stat, default_config_file):
    mock_stat.return_value.st_mode = 0o600  # Valid permissions
    config = Config(default_config_file)
    assert config.config is not None

    mock_stat.return_value.st_mode = 0o644  # Invalid permissions
    with pytest.raises(click.UsageError,
                       match=r'The configuration .* file must be readable only by the user.'):
        config.check_file_permission(str(default_config_file))


@patch('builtins.open', new_callable=mock_open, read_data=b'invalid toml')
@patch('os.stat')
def test_load_config_file_invalid_toml(mock_stat, mock_file):
    mock_stat.return_value.st_mode = 0o600  # Valid permissions
    with pytest.raises(click.UsageError, match='Invalid configuration file'):
        Config('dummy_config_file.toml')


@patch('os.path.exists', return_value=False)
def test_load_config_file_not_found(mock_exists):
    config = Config('dummy_config_file.toml')
    assert config.config['default']['calendar'] is None
    assert config.config['default']['server'] is None
    assert config.config['default']['timezone'] == ZoneInfo('UTC')


@patch('os.stat')
@patch('caldavctl.config.user_config_dir')
def test_merge_server(mock_user_config_dir_func, mock_stat, default_config_file):
    mock_user_config_dir_func.return_value = str(default_config_file.parent)
    mock_stat.return_value.st_mode = 0o600  # Valid permissions
    config = Config(None, name='new_server', username='new_user',
                    password='new_pass', url='http://new.url')

    assert 'new_server' in config.config['server']
    assert config.config['server']['new_server']['username'] == 'new_user'
    assert config.config['server']['new_server']['password'] == 'new_pass'
    assert config.config['server']['new_server']['url'] == 'http://new.url'


@patch('os.stat')
@patch('caldavctl.config.user_config_dir')
def test_merge_defaults(mock_user_config_dir_func, mock_stat, default_config_file):
    mock_user_config_dir_func.return_value = str(default_config_file.parent)
    mock_stat.return_value.st_mode = 0o600  # Valid permissions
    config = Config(None, default_server='new_default_server',
                    default_calendar='new_default_calendar',
                    timezone='Europe/Lisbon')

    assert config.config['default']['server'] == 'new_default_server'
    assert config.config['default']['calendar'] == 'new_default_calendar'
    assert config.config['default']['timezone'] == ZoneInfo('Europe/Lisbon')
