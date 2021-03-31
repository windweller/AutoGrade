
from ideaToText import Decision

# "Start" is a special decision which is invoked by the Sampler
# to generate a single sample.
class Start(Decision):

    def registerChoices(self):
        # This sentence creator starts with two choices.
        # One choice is important (the mood). The other
        # choice is unimportant (if the pharse has punctuation)
        self.addChoice('mood', {
            'friendly':10,
            'grumpy':5
        })

        # Choices have two parts, an identifier and a dictionary
        # which maps possible outcomes to their relative likelihood
        self.addChoice('punct', {
            '':10,
            '.':5,
            '!':1
        })

    def updateRubric(self):
        # update rubric is a space for you to separate the
        # important choices from the unimportant ones
        if self.getChoice('mood') == 'grumpy':
            self.turnOnRubric('isGrumpy')

    def render(self):
        # once choices have been made, you now have to turn
        # those ideas into text
        punctuation = self.getChoice('punct')
        mood = self.getChoice('mood')
        if mood == 'friendly':
            phrase = self.expand('Friendly')
        if mood == 'grumpy':
            phrase = self.expand('Grumpy')
        return phrase + punctuation
