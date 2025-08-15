# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from zoneinfo import ZoneInfo

import pytest

from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from caldavctl.todo import (
    list_todos, create_todo, delete_todo, toggle_todo_complete, percentage_complete
)


@pytest.fixture
def mock_context():
    """Fixture for the CLI context."""
    return {
        "config": MagicMock(
            servers=MagicMock(return_value=[("default", {"url": "testserver.com"})]),
            get_server=MagicMock(return_value=("default", {"url": "testserver.com"})),
            tz=MagicMock(return_value=ZoneInfo('Europe/Lisbon'))
        )
    }


@patch("caldavctl.dav.caldav_calendar")
def test_list_todos(mock_caldav_calendar, mock_context):

    class mock_calendar:
        name = "Test Calendar"
        id = "123"
        url = "http://testserver.com/calendar/123"
        get_supported_components = MagicMock(return_value=["VEVENT", "VTODO"])
        todos = MagicMock(return_value=[
            MagicMock(icalendar_component={
                'summary': 'Test Todo',
                'status': '',
                'percent-complete': 50,
                'description': 'Test Description',
                'uid': '1234'
                })
        ])

    mock_caldav_calendar.return_value.__enter__.return_value = mock_calendar()

    runner = CliRunner()
    result = runner.invoke(list_todos, ['--show-description', '--show-uid'], obj=mock_context)

    assert result.exit_code == 0
    assert '[ ]  50% Test Todo - 1234' in result.output
    assert 'Test Description' in result.output


@patch("caldavctl.dav.caldav_calendar")
def test_create_todo(mock_caldav_calendar, mock_context):
    runner = CliRunner()
    mock_calendar = MagicMock()
    mock_caldav_calendar.return_value.__enter__.return_value = mock_calendar

    result = runner.invoke(
        create_todo, [
            'Test Todo',
            '--description', 'Test Description',
            '--due-date', '2024-12-31T23:59:59',
            '--priority', '1'
        ],
        obj=mock_context
    )

    assert result.exit_code == 0
    assert 'todo created successfully: Test Todo' in result.output
    assert mock_calendar.save_event.called


@patch("caldavctl.dav.caldav_calendar_todo")
def test_delete_todo(mock_caldav_calendar_todo, mock_context):
    runner = CliRunner()
    mock_todo = MagicMock()

    mock_caldav_calendar_todo.return_value.__enter__.return_value = mock_todo
    result = runner.invoke(delete_todo, ['1234'], obj=mock_context)

    assert result.exit_code == 0
    assert 'Todo deleted' in result.output
    assert mock_todo.delete.called


@patch("caldavctl.dav.caldav_calendar_todo")
def test_toggle_todo_complete(mock_caldav_calendar_todo, mock_context):
    runner = CliRunner()
    mock_todo = MagicMock()

    # Test marking as completed
    mock_todo.icalendar_component.get.return_value = ''

    mock_caldav_calendar_todo.return_value.__enter__.return_value = mock_todo
    result = runner.invoke(toggle_todo_complete, ['1234'], obj=mock_context)

    assert result.exit_code == 0
    assert 'Todo completed' in result.output
    mock_todo.save.assert_called()

    # Test marking as not completed
    mock_todo.icalendar_component.get.return_value = 'COMPLETED'

    mock_caldav_calendar_todo.return_value.__enter__.return_value = mock_todo
    result = runner.invoke(toggle_todo_complete, ['1234'], obj=mock_context)

    assert result.exit_code == 0
    assert 'Todo is pending' in result.output
    mock_todo.save.assert_called()


@patch("caldavctl.dav.caldav_calendar_todo")
def test_percentage_complete(mock_caldav_calendar_todo, mock_context):
    runner = CliRunner()
    mock_todo = MagicMock()
    mock_todo.icalendar_component.get.side_effect = lambda key, default: {
        'percent-complete': 50
    }.get(key, default)

    mock_caldav_calendar_todo.return_value.__enter__.return_value = mock_todo
    result = runner.invoke(percentage_complete, ['1234', '75'], obj=mock_context)

    assert result.exit_code == 0
    assert 'Percentage set' in result.output
    mock_todo.save.assert_called()
