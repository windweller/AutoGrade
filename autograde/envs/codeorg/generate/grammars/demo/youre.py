from ideaToText import Decision

class Youre(Decision):
    def registerChoices(self):
        self.addChoice(self.getName(),{
            'you are':1,
            "you're":1,
        })

    def render(self):
    	return self.getChoice(self.getName())
        