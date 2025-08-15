# caldavctl

[![PyPI - Version](https://img.shields.io/pypi/v/caldavctl.svg)](https://pypi.org/project/caldavctl)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/caldavctl.svg)](https://pypi.org/project/caldavctl)

-----

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [License](#license)

## Installation

To install:

    pipx install caldavctl

### Completion

Optionally enable completion:

* bash, add this to `~/.bashrc`:

    ```
    eval "$(_CALDAVCTL_COMPLETE=bash_source caldavctl)"
    ```

* zsh, add this to `~/.zshrc`:

    ```
    eval "$(_CALDAVCTL_COMPLETE=zsh_source caldavctl)"
    ```

* fish, add this to `~/.config/fish/completions/foo-bar.fish`:

    ```
    _CALDAVCTL_COMPLETE=fish_source caldavctl | source
    ```

## Configuration

`caldavctl` is configured in `$HOME/.config/caldavctl/config.toml` and on
windows `C:\Users\<user name>\AppData\Local\caldavctl\caldavctl\config.toml`:

```toml
[server.server_01_nickname]
username="your user"
password="your pass"
url="https://oneserver.org/cal"

[server.server_02_nickname]
username="your user"
password="your pass"
url="https://anotherserver.org/cal"

[default]
server="server_01_nickname"
calendar="Default"
timezone="Asia/Tokyo"
```

Make sure to make this file readable only by the user owner of the file
otherwise the configuration will not be read:

```bash
$ chmod go-rwx $HOME/.config/caldavctl/config.toml
```

**On windows this check is not made**, however it's good practice to make sure the
configuration is only readable by the user running caldavctl.

To be able to edit events, on windows, make sure you create an environment
variable called `VISUAL` pointing to an editor of your choice. For instance:

```
set VISUAL=nvim
```

or

```
set VISUAL=notepad
```

## Usage

`caldavctl` uses sub commands to expose its functionality:

```bash
$ caldavctl --help
Usage: caldavctl [options] COMMAND [ARGS]...

caldavctl - command line CalDAV client

Options:
-c, --config <file>    Configuration file
--name <nickname>      Server nickname
--username <username>  Username on the CalDAV server
--passwd <passwd>      Password on the CalDAV server
--url <url>            Calendar CalDAV url
--timezone <timezone>  Your time zone
--server <nickname>    Default server (use nickname)
--calendar <uid>       Default calendar id
--version              caldavctl version
--help                 Show this message and exit.

Commands:
br        Backup or restore a calendar
calendar  Commands that deal with the calendars on the server
event     Event management
ics       iCalendar file operations
todo      Todo management
utils     Utility commands
```
Notes:

* The options to the main command override the configuration file;
* By default the configuration file is `$HOME/.config/caldavctl/config.toml`;

To get help about a sub-command do:

```bash
$ caldavctl <sub-command> --help
```

For example:

```bash
$ caldavctl event --help
Usage: caldavctl event [OPTIONS] COMMAND [ARGS]...

  Event management

Options:
  --help  Show this message and exit.

Commands:
  create  Create new event
  delete  Delete an event on the server
  list    List events from the server list.
```

This holds true for sub-sub-commands:

```bash
$ caldavctl todo list --help
Usage: caldavctl todo list [options]

List todos from the default server and default calendar

caldavctl uses templates to display the list command output by default. If
not specified otherwise it uses the `todo.txt` template. The used template
can be specified using the -tf/--template-file option. First we check the
current directory for the existence of the file. If it's not found we check
the `<share>/caldavctl/templates` directory.

Currently we have the following templates:

    * todo.txt - output with colors (default)
    * todo-nocolor.txt
    * todo.html

If the --json flag is used, the list command will output JSON. This output
does not go through the template system, and any template options will be
ignored when using --json.

Options:
-sd, --show-description      Show the todo's description.
-si, --show-uid              Show the todo's UID.
-a, --all                    Show all todos, including completed todos.
-tf, --template-file <file>  Template used to format the output
--json                       Output JSON instead of using a template
--help                       Show this message and exit.
```

### The create event command

The `create event` command uses a simple `key: value` format to define the
elements of an event. If the `--edit` option is used without specifying a file,
an example file is opened on your `$EDITOR`.

Here's a minimal event:

```
DTSTART: 2025-02-02 09:00
DURATION: PT30M
SUMMARY: Just an example!
```
Read the documentation about the event definition format in [docs/caldav_event_config_format.md](docs/caldav_event_config_format.md).

### Templates

Certain command have their output formatted with a template. See, for example:

```bash
caldavctl event list --help
```
If you want to create your own templates read [docs/caldav_templates.md](docs/caldav_templates.md).

## License

`caldavctl` is distributed under the terms of the [GPL-3.0-or-later](https://spdx.org/licenses/GPL-3.0-or-later.html) license.
