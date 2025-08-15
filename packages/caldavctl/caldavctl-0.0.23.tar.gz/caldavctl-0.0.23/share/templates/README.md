# caldavctl templates

`caldavctl` uses Jinja2 to display templates.

## Variables made available in the templates

### Calendars

* `calendar_list`: list of calendars, on each calendar we have available:
    * `server`
    * `name`
    * `id`
    * `components`
    * `url`

### Events

* `event_list`: list of events, on each event we have available:
    * `start_date`
    * `start_date_tz`
    * `end_date`
    * `end_date_tz`
    * `summary`
    * `description`
    * `uid`

* Flags:
    * `show_uid`
    * `show_description`
    * `show_timezone`

### Todos

* `todo_list`: list of todos, on each todo we have available:
    * `summary`
    * `status`
    * `percent`
    * `description`
    * `uid`

* Flags:
    * `show_uid`
    * `show_description`
    * `todo_list`

### Formatting

ASCII escape sequences to format the output in the terminal:

* `newline`

* Colors:
    * `BLACK`
    * `RED`
    * `GREEN`
    * `YELLOW`
    * `BLUE`
    * `MAGENTA`
    * `CYAN`
    * `WHITE`
    * `DEFAULT`

* `RESET`: reset all modes (styles and colors)

See:

    * https://en.wikipedia.org/wiki/ANSI_escape_code
    * [ANSI Escape Sequences](https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797)

