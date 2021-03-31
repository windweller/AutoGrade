from ideaToText import Decision

class Grumpy(Decision):

    def registerChoices(self):
        self.addChoice('grumpyPhrase',{
            'leave me alone':1,
            '{Youre} bloopy':1,
            'grrrr':1,
            'im tired':1
        })

    def render(self):
        return self.getChoice('grumpyPhrase')