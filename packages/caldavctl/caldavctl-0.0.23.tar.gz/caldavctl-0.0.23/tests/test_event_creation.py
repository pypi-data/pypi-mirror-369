# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import MagicMock
from click.testing import CliRunner
from caldavctl.event import create_event
from zoneinfo import ZoneInfo


@pytest.fixture
def mock_context():
    """Fixture for the CLI context."""
    return {
        "config": MagicMock(
            servers=MagicMock(return_value=[("default", {"url": "testserver.com"})]),
            get_server=MagicMock(return_value=("default", {"url": "testserver.com"})),
            tz=MagicMock(return_value=ZoneInfo("Europe/London"))
        )
    }


def test_create_event_one_alarm(mock_context, tmp_path, monkeypatch):
    """Test listing calendars."""
    event_data = """
        SUMMARY: This is a description
        LOCATION: [[Timbuktu]] # With a comment
        CATEGORIES: Birthday, Shopping, Training
        TIMEZONE: Europe/Madrid
        DTSTART: 2024-01-20 09:00
        DTEND: 2024-01-20 09:45
        ALARM: P0D One alarm
        DESCRIPTION: [[
        Once upon a time,
        There was a little lamb
        ]]
        """
    # Create a temporary file
    temp_file = tmp_path / "event.txt"
    temp_file.write_text(event_data)

    runner = CliRunner()
    result = runner.invoke(create_event, ['--dry-run', "--file", str(temp_file)], obj=mock_context)

    assert result.exit_code == 0
    assert "BEGIN:VALARM\nACTION:display\nDESCRIPTION:One alarm\nTRIGGER:P0D" in result.output


def test_create_event_two_alarms(mock_context, tmp_path, monkeypatch):
    """Test listing calendars."""
    event_data = """
        SUMMARY: This is a description
        LOCATION: [[Timbuktu]] # With a comment
        CATEGORIES: Birthday, Shopping, Training
        TIMEZONE: Europe/Madrid
        DTSTART: 2024-01-20 09:00
        DTEND: 2024-01-20 09:45
        ALARM: P0D One alarm
        ALARM: -PT1H Another alarm
        DESCRIPTION: [[
        Once upon a time,
        There was a little lamb
        ]]
        """
    # Create a temporary file
    temp_file = tmp_path / "event.txt"
    temp_file.write_text(event_data)

    runner = CliRunner()
    result = runner.invoke(create_event, ['--dry-run', "--file", str(temp_file)], obj=mock_context)

    assert result.exit_code == 0
    assert "BEGIN:VALARM\nACTION:display\nDESCRIPTION:One alarm\nTRIGGER:P0D" in result.output
    assert "BEGIN:VALARM\nACTION:display\nDESCRIPTION:Another alarm\nTRIGGER:-PT1H\nEND:VALARM" in result.output

