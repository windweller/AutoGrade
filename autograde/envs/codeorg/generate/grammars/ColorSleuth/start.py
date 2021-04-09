"""
Goal: be as modularized as you can
Use context/params to
"""

import random
import string
from ideaToText import Decision
from .utils import wrap_params_for_RandomVarName, wrap_params_for_AssignmentValue

class Start(Decision):
    def registerChoices(self):
        pass

    def updateRubric(self):
        pass

    def render(self):
        blocks = []

        # var currentPlayer = 1;

        # var p1Score = 0;
        code = self.expand('CreatePlayerScore', params={'player_num': 1})
        blocks.append(code)

        # var p2Score = 0;
        code = self.expand('CreatePlayerScore', params={'player_num': 2})
        blocks.append(code)

        # var randButtonId;

        # setBoard();

        return "".join(blocks)

def get_default_player_score_var_names(player_num):
    return {
            f'p{player_num}Score': 50,
            f'p{player_num}score': 40,
            f'player{player_num}_score': 20,
            f'player{player_num}Score': 5,
            f'player{player_num}score': 5,
            f'player_score_{player_num}': 10
        }

# var p1Score = 0;
class CreatePlayerScore(Decision):

    def render(self):
        # var p1Score=0;
        player_num = self.params['player_num']

        varname = self.expand('RandomVarName', params=wrap_params_for_RandomVarName(f'p{player_num}score', get_default_player_score_var_names(player_num)))
        init_value = self.expand('AssignmentValue', params=wrap_params_for_AssignmentValue('0', '0', '95', f'p{player_num}score'))
        code = f'var {varname} = {init_value}; \n'

        return code
