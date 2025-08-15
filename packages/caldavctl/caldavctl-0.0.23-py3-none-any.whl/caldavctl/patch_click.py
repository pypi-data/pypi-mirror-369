# From:
# https://github.com/pallets/click/issues/2676

# The above issue is related to numerical negative arguments. I've adapted that
# solution to allow negative numbers in options with optional values

from gettext import ngettext
from click.parser import OptionParser, _flag_needs_value, BadOptionUsage


def _is_number(arg: str) -> bool:
    try:
        _ = int(arg, 0)
    except ValueError:
        try:
            _ = float(arg)
        except ValueError:
            return False
    return True


# Allow negative numbers in options with optional values
#
# Based on click/parser.py v8.1.8
#
def _get_value_from_state(
    self, option_name, option, state
):
    nargs = option.nargs

    if len(state.rargs) < nargs:
        if option.obj._flag_needs_value:
            # Option allows omitting the value.
            value = _flag_needs_value
        else:
            raise BadOptionUsage(
                option_name,
                ngettext(
                    "Option {name!r} requires an argument.",
                    "Option {name!r} requires {nargs} arguments.",
                    nargs,
                ).format(name=option_name, nargs=nargs),
            )
    elif nargs == 1:
        next_rarg = state.rargs[0]

        if (
            option.obj._flag_needs_value
            and isinstance(next_rarg, str)
            and next_rarg[:1] in self._opt_prefixes
            and len(next_rarg) > 1
            and not _is_number(next_rarg)
        ):
            # The next arg looks like the start of an option, don't
            # use it as the value if omitting the value is allowed.
            value = _flag_needs_value
        else:
            value = state.rargs.pop(0)
    else:
        value = tuple(state.rargs[:nargs])
        del state.rargs[:nargs]

    return value


# Monkey-patch the OptionParser class
#
OptionParser._get_value_from_state = _get_value_from_state
