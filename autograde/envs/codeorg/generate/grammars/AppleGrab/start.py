# Kinda want to model: 1. recursive expansion of snippets
# 2. the fact that some lines can appear anywhere

# Make sure that

import random
import string
from ideaToText import Decision


# "Start" is a special decision which is invoked by the Sampler
# to generate a single sample.
class Start(Decision):

    def registerChoices(self):
        # This sentence creator starts with two choices.
        # One choice is important (the mood). The other
        # choice is unimportant (if the pharse has punctuation)
        self.addChoice('scores', {
            'ZeroScore': 20,
            'OtherScore': 5,
            'EmptyScore': 5,
        })

        self.addChoice('lives', {
            'ThreeLives': 20,
            'OtherLives': 5,
            'EmptyLives': 5,
        })

    def updateRubric(self):
        # update rubric is a space for you to separate the
        # important choices from the unimportant ones
        if self.getChoice('scores') == 'OtherScore':
            self.turnOnRubric('Wrong start score')
        if self.getChoice('lives') == 'OtherLives':
            self.turnOnRubric("Wrong lives")

    def render(self):
        # once choices have been made, you now have to turn
        # those ideas into text

        template = """
        var score = 0;
        onEvent("apple", "click", function() {
          score += 1;
          setText("score_label", score)
          setPosition("apple", randomNumber(50,280), randomNumber(50, 350));
        });
        
        var lives = 3;
        
        onEvent("background", "click", function() {
          lives -= 1;
          setText("lives_label", lives)
        })
        """

        blocks = []

        # 1. var score = 0;
        score = self.getChoice("scores")
        score_code = self.expand(score)
        blocks.append(score_code)

        # 2. onEvent("apple", "click", function() {}
        apple_click_code = self.expand('AppleClickEvent')
        blocks.append(apple_click_code)

        # 3.  var lives = 3;
        lives = self.getChoice("lives")
        lives_code = self.expand(lives)
        blocks.append(lives_code)

        # 4. onEvent("background", "click", function() {}
        bkg_click_code = self.expand('BackgroundClickEvent')
        blocks.append(bkg_click_code)

        random.shuffle(blocks)

        return "".join(blocks)


class EmptyScore(Decision):
    def updateRubric(self):
        self.turnOnRubric('Score Variable is missing')

    def render(self):
        return ""


class EmptyLives(Decision):
    def updateRubric(self):
        self.turnOnRubric('Lives Variable is missing')

    def render(self):
        return ""


class ScoreVarName(Decision):
    def registerChoices(self):
        values = {}
        for _ in range(20):
            name = ''.join(random.choices(string.ascii_lowercase, k=5))
            values[name] = 2

        values['scores'] = 200
        values['score'] = 20
        values['Scores'] = 20
        values['Scs'] = 20
        values['Scres'] = 20

        self.addChoice('score_var_name', values)

    def render(self):
        return self.getChoice("score_var_name")


class LivesVarName(Decision):
    def registerChoices(self):
        values = {}
        for _ in range(20):
            name = ''.join(random.choices(string.ascii_lowercase, k=5))
            values[name] = 2

        values['lives'] = 200
        values['live'] = 20
        values['lifes'] = 20
        values['life'] = 20
        values['Lives'] = 20
        values['Live'] = 20

        self.addChoice('lives_var_name', values)

    def render(self):
        return self.getChoice("lives_var_name")

class ThreeLives(Decision):
    def render(self):
        varname = self.expand("LivesVarName")
        return f"var {varname} = 3; \n"


class OtherLives(Decision):
    def registerChoices(self):
        values = {}
        for num in range(1, 10000):
            values[num] = 1

        self.addChoice('wrong_lives_score', values)

    def render(self):
        wrong_score = self.getChoice('wrong_lives_score')
        varname = self.expand("LivesVarName")
        return "var {} = {}; \n".format(varname, wrong_score)


class ZeroScore(Decision):
    def render(self):
        scores_var_name = self.expand('ScoreVarName')
        # scores_var_name = self.getChoice("score_var_name")
        return f"var {scores_var_name} = 0; \n"


class OtherScore(Decision):
    def registerChoices(self):
        values = {}
        for num in range(1, 10000):
            values[num] = 1

        self.addChoice('wrong_start_score', values)

    def render(self):
        wrong_score = self.getChoice('wrong_start_score')
        scores_var_name = self.expand('ScoreVarName')
        return "var {} = {}; \n".format(scores_var_name, wrong_score)

