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


class BackgroundClickEvent(Decision):
    def registerChoices(self):
        # do not name choice "non-terminal" with underscore
        self.addChoice('bkg_click_event_id',
                       {'apple': 2,
                        'background': 100,
                        'image1': 2,
                        'lives_description': 2,
                        'score_description': 2,
                        'lives_label': 2,
                        'score_label': 2,
                        'screen1': 2,
                        'screen2': 2})

        self.addChoice('bkg_click_event_type',
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

        self.addChoice('bkg_click_event_inc_score',
                       {'IncLives': 10,
                        'DecLives': 40,
                        'EmptyDecLives': 20})

        self.addChoice('bkg_click_event_set_text_id',
                       {'apple': 2,
                        'background': 2,
                        'image1': 2,
                        'lives_description': 2,
                        'score_description': 2,
                        'lives_label': 100,
                        'score_label': 2,
                        'screen1': 2,
                        'screen2': 2})

        self.addChoice('bkg_click_event_set_text_value',
                       {'LivesVarName': 50,
                        'ScoreVarName': 10})

        # we should update score first, then update visual
        self.addChoice('bkg_click_event_flip_var_update',
                       {'flip': 10, 'correct': 30})

    def updateRubric(self):
        if self.getChoice('bkg_click_event_id') != 'background':
            self.turnOnRubric('BkgClickEventID is wrong, not "background"')

        if self.getChoice('bkg_click_event_type') != 'click':
            self.turnOnRubric('BkgClickEventType is wrong, not "click"')

        if self.getChoice('bkg_click_event_set_text_value') != 'LivesVarName':
            # it's nested because when both are true, no line is shown,
            # therefore this error shouldn't appear
            if self.getChoice('lives') != 'EmptyLives':
                self.turnOnRubric('Wrong variable name for lives update')

        if self.getChoice('scores') != 'EmptyScore':
            if self.getChoice('bkg_click_event_set_text_value') == 'LivesVarName' and self.getChoice(
                    'lives') == 'EmptyLives':
                pass
            elif self.getChoice('bkg_click_event_flip_var_update') == 'flip':
                self.turnOnRubric('Need to update score variable BEFORE updating interface text')


    def render(self):
        bkg_click_event_id = self.getChoice('bkg_click_event_id')
        bkg_click_event_type = self.getChoice('bkg_click_event_type')

        code = 'onEvent("' + bkg_click_event_id + '", "' + bkg_click_event_type + '", function() {{ \n'

        blocks = []
        if self.getChoice('scores') != 'EmptyScore':
            # score += 1;
            lives_dec_line = self.expand(self.getChoice('bkg_click_event_inc_score'))
            blocks.append(lives_dec_line)

            # setText("score_label", score);
            bkg_click_event_set_text_id = self.getChoice('bkg_click_event_set_text_id')
            bkg_click_event_set_text_value = self.expand(self.getChoice('bkg_click_event_set_text_value'))

            # prevent the case where we setText to lives, but didn't define lives
            if self.getChoice('bkg_click_event_set_text_value') == 'ScoreVarName' and self.getChoice(
                    'scores') == 'EmptyScore':
                pass
            else:
                lives_set_text_line = '\t setText("' + bkg_click_event_set_text_id + '", ' + bkg_click_event_set_text_value + '); \n'

                if self.getChoice('bkg_click_event_flip_var_update') == 'flip':
                    blocks = [lives_set_text_line, lives_dec_line]
                else:
                    blocks = [lives_dec_line, lives_set_text_line]

        end_code = "}}); \n"

        return code + ''.join(blocks) + end_code


class BkgFixedNumber(Decision):
    def registerChoices(self):
        values = {}
        # maybe we should expand this range?
        # but then it becomes very hard to test
        for num in range(50, 280):
            values[str(num)] = 1
        self.addChoice('BkgClickNewFixedPos{}'.format(self.params['pos']), values)

    # def updateRubric(self):
    #     if self.params['pos'] == 1 or self.params['pos'] == 2:
    #         self.turnOnRubric('Apple should randomly appear, not always in a fixed place')

    def render(self):
        return self.getChoice('BkgClickNewFixedPos{}'.format(self.params['pos']))


class BkgRandomNumberFunc(Decision):
    def registerChoices(self):
        self.addChoice('BkgClickFixedRange', {
            'fixed_range': 20,
            'random_range': 5
        })

    def render(self):
        # randomNumber(50,280)
        if self.getChoice('BkgClickFixedRange') == 'random_range':
            num_3 = self.expand('FixedNumber', params={'pos': 3})
            num_4 = self.expand('FixedNumber', params={'pos': 4})
        else:
            num_3, num_4 = 50, 280

        return "randomNumber({},{})".format(num_3, num_4)


class IncLives(Decision):
    def registerChoices(self):
        values = {}
        for num in range(0, 100):
            values[num] = 1

        values[1] = 100
        self.addChoice('bkg_click_inc_num', values)

    def updateRubric(self):
        self.turnOnRubric('BkgClickEvent score increased, not decreased')

    def render(self):
        num = self.getChoice('bkg_click_inc_num')
        code = '\t {} += {}; \n'.format(self.expand('LivesVarName'), num)
        return code


class DecLives(Decision):
    def registerChoices(self):
        values = {}
        for num in range(0, 100):
            values[num] = 1

        self.addChoice('bkg_click_dec_num', values)

    def updateRubric(self):
        if self.getChoice('bkg_click_dec_num') != 1:
            self.turnOnRubric('BkgClickEvent decreased by wrong number, not 1')


    def render(self):
        num = self.getChoice('bkg_click_dec_num')
        code = '\t {} -= {}; \n'.format(self.expand('LivesVarName'), num)
        return code


class EmptyDecLives(Decision):
    def updateRubric(self):
        self.turnOnRubric('BackgroundClickEvent lives not decreased')

    def render(self):
        return ''
