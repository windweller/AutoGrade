"""
We define some functions that are sharable
across other modules

Note that these Decisions must be very close to the leaf decision
Otherwise, changing context / parameters might affect too many other decisions
"""

import random
import string
import warnings
from ideaToText import Decision


def wrap_params_for_RandomVarName(var_name, predef_set=None):
    if predef_set is None:
        return {'var_name': var_name}
    else:
        return {'var_name': var_name, 'predef_set': predef_set}


def get_choice_name_for_RandomVarName(var_name):
    return f'{var_name}_VarName'


# need to always use self.expand() on this variable
# and always pass in parameters
class RandomVarName(Decision):
    def registerChoices(self):
        values = {}
        for _ in range(20):
            name = ''.join(random.choices(string.ascii_lowercase, k=5))
            values[name] = 2

        # now we fetch pre-defined names passed from context
        # we override any randomly generated varnames with varnames provided
        # in our pre-defined set
        if 'predef_set' in self.params:
            for k, v in self.params['predef_set'].items():
                values[k] = v

        rvn_id = self.params['var_name']
        # like: "ScoreVarName"
        self.addChoice(f'{rvn_id}_VarName', values)

    def render(self):
        var_name = self.params['var_name']
        return self.getChoice(f'{var_name}_VarName')


def wrap_params_for_AssignmentValue(correct_value, low, high, var_name):
    return {'correct_value': correct_value,
            'low': low,
            'high': high,
            'var_name': var_name}


def get_choice_name_for_AssignmentValue(var_name):
    return f'{var_name}_wrong_value'


class WrongAssignmentValue(Decision):
    def registerChoices(self):
        correct_value = self.params['correct_value']
        low = self.params['low']
        high = self.params['high']
        values = {}
        for num in range(int(low), int(high)):
            if num == correct_value:
                continue
            values[str(num)] = 1

        var_name = self.params['var_name']
        self.addChoice(f'{var_name}_wrong_value', values)

    def updateRubric(self):
        var_name = self.params['var_name']
        correct_value = self.params['correct_value']
        self.turnOnRubric(f'{var_name} Variable has wrong initial value, should be {correct_value}')

    def render(self):
        var_name = self.params['var_name']
        return self.getChoice(f'{var_name}_wrong_value')

class AssignmentValue(Decision):
    def registerChoices(self):
        var_name = self.params['var_name']

        self.addChoice(f'{var_name}_value_choice', {
            'correct_value': 30,
            'wrong_value': 10
        })

    def render(self):
        var_name = self.params['var_name']
        correct_value = self.params['correct_value']
        low = self.params['low']
        high = self.params['high']

        if self.getChoice(f'{var_name}_value_choice') == 'correct_value':
            return correct_value
        else:
            return self.expand('WrongAssignmentValue', wrap_params_for_AssignmentValue(correct_value,
                                                                                       low, high, var_name))

