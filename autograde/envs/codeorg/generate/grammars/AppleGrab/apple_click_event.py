import random
import string
from copy import copy
from ideaToText import Decision

"""
onEvent("apple", "click", function() {
          score += 1;
          setText("score_label", score)
          setPosition("apple", randomNumber(50,280), randomNumber(50, 350));
});
"""

"""
This context grammar is hard to cover things like:
score += 1;
is equivalent to
new_score = score;
new_score += 1;
(Actually, this is possible, but harder to write on our end)
(and do not bring semantic/behavioral difference in the game)

Also
setPosition("apple", randomNumber(256,79), randomNumber(256,79)); 
Can be replace by
deleteElement(id)
image(id)
showElement(id)
setPosition(id)

We are not considering this situation 
(Which makes our goal of just capturing all (x, y) of objects much harder)
"""


class AppleClickEvent(Decision):
    def registerChoices(self):
        # do not name choice "non-terminal" with underscore
        self.addChoice('apple_click_event_id',
                       {'apple': 100,
                        'background': 2,
                        'image1': 2,
                        'lives_description': 2,
                        'score_description': 2,
                        'lives_label': 2,
                        'score_label': 2,
                        'screen1': 2,
                        'screen2': 2})

        self.addChoice('apple_click_event_type',
                       {'click': 100,
                        'change': 2,
                        'keyup': 2,
                        'keydown': 2,
                        'keypress': 2,
                        'mousemove': 2,
                        'mousedown': 2,
                        'mouseup': 2,
                        'mouseover': 2,
                        'mouseout': 2,
                        'input': 2})

        self.addChoice('apple_click_event_inc_score',
                       {'IncScore': 40,
                        'DecScore': 10,
                        'EmptyIncScore': 20})

        self.addChoice('apple_click_event_set_text_id',
                       {'apple': 2,
                        'background': 2,
                        'image1': 2,
                        'lives_description': 2,
                        'score_description': 2,
                        'lives_label': 2,
                        'score_label': 100,
                        'screen1': 2,
                        'screen2': 2})

        self.addChoice('apple_click_event_set_text_value',
                       {'ScoreVarName': 50,
                        'LivesVarName': 10})

        self.addChoice('apple_click_event_set_pos',
                       {'correct': 50,
                        'missing': 20})

        self.addChoice('apple_click_event_set_pos_id',
                       {'apple': 100,
                        'background': 2,
                        'image1': 2,
                        'lives_description': 2,
                        'score_description': 2,
                        'lives_label': 2,
                        'score_label': 2,
                        'screen1': 2,
                        'screen2': 2})

        self.addChoice('apple_click_event_set_pos_pos1',
                       {'RandomNumberFunc': 50,
                        'FixedNumber': 10})

        self.addChoice('apple_click_event_set_pos_pos2',
                       {'RandomNumberFunc': 50,
                        'FixedNumber': 10})

        # we should update score first, then update visual
        self.addChoice('apple_click_event_flip_var_update',
                       {'flip': 10, 'correct': 30})

    def updateRubric(self):
        if self.getChoice('apple_click_event_id') != 'apple':
            self.turnOnRubric('AppleClickEventID is wrong, not "apple"')

        if self.getChoice('apple_click_event_type') != 'click':
            self.turnOnRubric('AppleClickEventType is wrong, not "click"')

        if self.getChoice('apple_click_event_set_text_value') != 'ScoreVarName':
            # it's nested because when both are true, no line is shown,
            # therefore this error shouldn't appear
            if self.getChoice('lives') != 'EmptyLives':
                self.turnOnRubric('Wrong variable name for score update')

        if self.getChoice('apple_click_event_set_pos_pos1') == 'FixedNumber' and \
                self.getChoice('apple_click_event_set_pos_pos2') == 'FixedNumber':
            self.turnOnRubric('Apple should randomly appear, not always in a fixed place')

        if self.getChoice('scores') != 'EmptyScore':
            if self.getChoice('apple_click_event_set_text_value') == 'LivesVarName' and self.getChoice(
                    'lives') == 'EmptyLives':
                pass
            elif self.getChoice('apple_click_event_flip_var_update') == 'flip':
                self.turnOnRubric('Need to update score variable BEFORE updating interface text')

        if self.getChoice('apple_click_event_set_pos') == 'missing':
            self.turnOnRubric("Apple's position is not updated, setPosition() missing")

    def render(self):
        apple_click_event_id = self.getChoice('apple_click_event_id')
        apple_click_event_type = self.getChoice('apple_click_event_type')

        code = 'onEvent("' + apple_click_event_id + '", "' + apple_click_event_type + '", function() {{ \n'

        blocks = []
        if self.getChoice('scores') != 'EmptyScore':
            # score += 1;
            score_inc_line = self.expand(self.getChoice('apple_click_event_inc_score'))
            blocks.append(score_inc_line)

            # setText("score_label", score);
            apple_click_event_set_text_id = self.getChoice('apple_click_event_set_text_id')
            apple_click_event_set_text_value = self.expand(self.getChoice('apple_click_event_set_text_value'))

            # prevent the case where we setText to lives, but didn't define lives
            if self.getChoice('apple_click_event_set_text_value') == 'LivesVarName' and self.getChoice(
                    'lives') == 'EmptyLives':
                pass
            else:
                score_set_text_line = '\t setText("' + apple_click_event_set_text_id + '", ' + apple_click_event_set_text_value + '); \n'

                if self.getChoice('apple_click_event_flip_var_update') == 'flip':
                    blocks = [score_set_text_line, score_inc_line]
                else:
                    blocks = [score_inc_line, score_set_text_line]

        # setPosition("apple", randomNumber(50,280), randomNumber(50, 350));
        if self.getChoice('apple_click_event_set_pos') != 'missing':
            pos_id = self.getChoice('apple_click_event_set_pos_id')
            num_1 = self.expand(self.getChoice('apple_click_event_set_pos_pos1'), params={'pos': 1})
            num_2 = self.expand(self.getChoice('apple_click_event_set_pos_pos2'), params={'pos': 2})
            line = '\t setPosition("{}", {}, {}); \n'.format(pos_id, num_1, num_2)

            blocks.append(line)

        end_code = "}}); \n"

        return code + ''.join(blocks) + end_code


class FixedNumber(Decision):
    def registerChoices(self):
        values = {}
        # maybe we should expand this range?
        # but then it becomes very hard to test
        for num in range(50, 280):
            values[str(num)] = 1
        self.addChoice('AppleClickNewFixedPos{}'.format(self.params['pos']), values)

    # def updateRubric(self):
    #     if self.params['pos'] == 1 or self.params['pos'] == 2:
    #         self.turnOnRubric('Apple should randomly appear, not always in a fixed place')

    def render(self):
        return self.getChoice('AppleClickNewFixedPos{}'.format(self.params['pos']))


class RandomNumberFunc(Decision):
    def registerChoices(self):
        self.addChoice('AppleClickFixedRange', {
            'fixed_range': 20,
            'random_range': 5
        })

    def render(self):
        # randomNumber(50,280)
        if self.getChoice('AppleClickFixedRange') == 'random_range':
            num_3 = self.expand('FixedNumber', params={'pos': 3})
            num_4 = self.expand('FixedNumber', params={'pos': 4})
        else:
            num_3, num_4 = 50, 280

        return "randomNumber({},{})".format(num_3, num_4)


class IncScore(Decision):
    def registerChoices(self):
        values = {}
        for num in range(0, 100):
            values[num] = 1

        values[1] = 100
        self.addChoice('apple_click_inc_num', values)

    def updateRubric(self):
        if self.getChoice('apple_click_inc_num') != 1:
            self.turnOnRubric('AppleClickEvent Increased by wrong number, not 1')

    def render(self):
        num = self.getChoice('apple_click_inc_num')
        code = '\t {} += {}; \n'.format(self.expand('ScoreVarName'), num)
        return code


class DecScore(Decision):
    def registerChoices(self):
        values = {}
        for num in range(0, 100):
            values[num] = 1

        self.addChoice('apple_click_dec_num', values)

    def updateRubric(self):
        self.turnOnRubric('AppleClickEvent score decreased, not increased')

    def render(self):
        num = self.getChoice('apple_click_dec_num')
        code = '\t {} -= {}; \n'.format(self.expand('ScoreVarName'), num)
        return code


class EmptyIncScore(Decision):
    def updateRubric(self):
        self.turnOnRubric('AppleClickEvent score not increased')

    def render(self):
        return ''
