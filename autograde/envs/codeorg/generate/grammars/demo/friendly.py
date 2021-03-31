from ideaToText import Decision

class Friendly(Decision):
    def registerChoices(self):
        self.addChoice('friendlyPhrase',{
            'good morning':1,
            'welcome':1,
            '{Youre} beautiful':1,
            'What a wonderful day':1,
            'I really appreciate you':1
        })

    def render(self):
    	# if the string you return has a Decision name 
    	# in brackets, the sampler will auto expand itß
        return self.getChoice('friendlyPhrase')