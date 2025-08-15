# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later


from caldavctl.click_utils import OptionsCompatibility

from click.testing import CliRunner

from caldavctl import cli


def test_click_utils_compatibility():
    compatibility = OptionsCompatibility(['today', 'week', 'dtstart', 'dtend'])
    compatibility.set_exception(['dtstart', 'dtend'])

    test_compatibility = {
        'today': {
            'week': False,
            'dtstart': False,
            'dtend': False,
        },
        'week': {
            'today': False,
            'dtstart': False,
            'dtend': False,
        },
        'dtstart': {
            'today': False,
            'week': False,
            'dtend': True,
        },
        'dtend': {
            'today': False,
            'week': False,
            'dtstart': True,
        },
    }

    assert test_compatibility == compatibility.compatibility


def test_click_utils_incompatible():
    '''
    Test incompatible options
    '''
    runner = CliRunner()
    result = runner.invoke(
        cli.cli_group,
        ['event', 'list', '-s', '2025-01-01', '--week', '1']
    )
    assert 'Error, the options "dtstart" and "week" can\'t be used together.' in result.output


def test_click_utils_incompatible_optional_value():
    '''
    Test incompatible options when one of the options has optional values using
    the default value.
    '''
    runner = CliRunner()
    result = runner.invoke(
        cli.cli_group,
        ['event', 'list', '-s', '2025-01-01', '--week']
    )
    assert 'Error, the options "dtstart" and "week" can\'t be used together.' in result.output
