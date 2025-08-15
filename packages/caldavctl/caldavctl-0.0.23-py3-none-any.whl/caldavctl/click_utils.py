# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@paxjulia.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from itertools import combinations


class OptionsCompatibility:
    def __init__(self, option_list):
        '''
        The `option_list` is a list of options that can't be used together.
        '''
        self.option_list = list(set(option_list))
        self.set_compatibility()

    def set_compatibility(self):
        incomp = {}
        for option in self.option_list:
            incomp[option] = {opt: False for opt in self.option_list if opt != option}
        self.compatibility = incomp

    def set_exception(self, options):
        for opt1, opt2 in combinations(options, 2):
            self.compatibility[opt1][opt2] = True
            self.compatibility[opt2][opt1] = True

    def check(self, opt1, opt2):
        return self.compatibility[opt1][opt2]


def create_compatibility_check(options, exceptions):
    '''
    options - list of options that are incompatible
    exclusions - list of exclusions, it's a list of lists
    '''
    compatibility = OptionsCompatibility(options)
    for exception in exceptions:
        compatibility.set_exception(exception)

    def exclusive_option(context, param, value):
        if value is not None:
            context.obj['option'].append(param.name)
        if len(context.obj['option']) > 1:
            for opt1, opt2 in combinations(context.obj['option'], 2):
                if not compatibility.check(opt1, opt2):
                    context.exit('Error, the options '
                                 f'"{opt1}" and "{opt2}" can\'t be used together.')
        return value

    return exclusive_option
