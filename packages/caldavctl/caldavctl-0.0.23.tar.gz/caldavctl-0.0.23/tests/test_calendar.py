# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from caldavctl.calendar_dav import list_calendars, create_calendar, delete_calendar


@pytest.fixture
def mock_context():
    """Fixture for the CLI context."""
    return {
        "config": MagicMock(
            servers=MagicMock(return_value=[("default", {"url": "testserver.com"})]),
            get_server=MagicMock(return_value=("default", {"url": "testserver.com"}))
        )
    }


@patch("caldav.DAVClient")
def test_list_calendars(mock_davclient, mock_context):
    """Test listing calendars."""
    # Mock principal and calendars
    mock_principal = MagicMock()

    class mock_calendar:
        name = "Test Calendar"
        id = "123"
        url = "http://testserver.com/calendar/123"
        get_supported_components = MagicMock(return_value=["VEVENT", "VTODO"])

    mock_principal.calendars.return_value = [mock_calendar]
    mock_davclient.return_value.__enter__.return_value.principal.return_value = mock_principal

    runner = CliRunner()
    result = runner.invoke(list_calendars, obj=mock_context)

    assert result.exit_code == 0
    assert "Server \"default\"" in result.output
    assert "CALENDAR = Test Calendar" in result.output
    assert "ID = 123" in result.output
    assert "COMPONENTS = VEVENT, VTODO" in result.output
    assert "URL = http://testserver.com/calendar/123" in result.output


@patch("caldav.DAVClient")
def test_create_calendar(mock_davclient, mock_context):
    """Test creating a calendar."""
    mock_principal = MagicMock()
    mock_davclient.return_value.__enter__.return_value.principal.return_value = mock_principal

    runner = CliRunner()
    result = runner.invoke(
        create_calendar,
        ["New Calendar"],
        obj=mock_context,
    )

    assert result.exit_code == 0
    assert 'Calendar "New Calendar" created.' in result.output
    mock_principal.make_calendar.assert_called_once_with(name="New Calendar", cal_id=None)


@patch("caldav.DAVClient")
@patch("caldavctl.dav.caldav_calendar")
def test_delete_calendar(mock_caldav_calendar, mock_davclient, mock_context):
    """Test deleting a calendar."""
    class mock_calendar:
        name = "Test Calendar"
        delete = MagicMock()

    mock_caldav_calendar.return_value.__enter__.return_value = mock_calendar

    runner = CliRunner()
    result = runner.invoke(
        delete_calendar,
        ["bdcbe606-b68c-11ef-b03f-d4f32d4b839a"],
        obj=mock_context,
    )

    assert result.exit_code == 0
    assert 'Calendar "Test Calendar" deleted.' in result.output
    mock_caldav_calendar.assert_called_once_with({"url": "testserver.com"},
                                                 "bdcbe606-b68c-11ef-b03f-d4f32d4b839a")
    mock_calendar.delete.assert_called_once()
