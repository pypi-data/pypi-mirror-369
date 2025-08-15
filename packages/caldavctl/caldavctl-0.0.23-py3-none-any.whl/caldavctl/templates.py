# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
from pathlib import Path
from typing import Optional

import click
import jinja2
import markdown


def get_venv_share_directory(app_name: str) -> Optional[Path]:
    '''
    Find the share directory within the current virtual environment.

    Args:
        app_name: The name of your application

    Returns:
        Path object to the virtual environment share directory, or None if not
        in a venv
    '''
    # Check if running in a virtual environment
    if sys.prefix != sys.base_prefix:
        # Get the virtual environment root
        venv_root = Path(sys.prefix)

        # Common share directory locations in a venv
        possible_share_dirs = [
            venv_root / 'share',            # /venv/share
            venv_root / 'local' / 'share',  # /venv/local/share
            venv_root / 'var' / 'share',    # /venv/var/share
        ]

        # Check app-specific directories first
        for base_dir in possible_share_dirs:
            app_dir = base_dir / app_name
            yield app_dir

    return None


def share_directory_list(app_name):
    '''
    A list of possible share locations.

    Args:
        app_name: The name of your application

    Returns:
        A list of Path objects pointing to the share directories.
    '''
    # First check virtual environment (includes pipx environments)
    venv_share = get_venv_share_directory(app_name)

    # Get XDG_DATA_HOME from environment or use default
    xdg_data_home = os.environ.get('XDG_DATA_HOME', '~/.local/share')
    xdg_data_home = Path(xdg_data_home).expanduser()

    # Get XDG_DATA_DIRS from environment or use default
    xdg_data_dirs = os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share')
    data_dirs = [Path(p) for p in xdg_data_dirs.split(':')]

    # Order of preference for share directories
    search_paths = [
        *[p for p in venv_share],  # venv share directories
        xdg_data_home / app_name,  # ~/.local/share/<app_name>
        *[p / app_name for p in data_dirs]  # System-wide directories
    ]

    # Return the first directory that exists and contains data
    for path in search_paths:
        yield path


def filename_list(app_name, filename):
    # First test if the file name supplied exists
    yield filename
    # If unsuccessful try to open the file from other places
    for path in share_directory_list(app_name):
        yield path / 'templates' / filename


def load_template(app_name, filename):
    '''
    Loads a template stored in `filename`
    '''
    for fn in filename_list(app_name, filename):
        try:
            with open(fn, 'r') as f:
                template_str = f.read()
            return template_str
        except FileNotFoundError:
            pass
    raise click.UsageError(f'File "{filename}" not found')


def render(app_name, filename, context):
    template_str = load_template(app_name, filename)
    template = jinja2.Template(template_str)
    template.environment.filters["markdown"] = markdown.markdown
    return template.render(**context)
