import string
from ideaToText import Decision

class Start(Decision):
	def registerChoices(self):
		self.addChoice('player', {
			# Choices
		})

	 def updateRubric(self):
	 	

	 def render(self):
	 	#TODO: Replace template with FlyerGame Template
	 	template = """
		// GAME SETUP
		// create player, target, and obstacles
		var player = createSprite(200, 100);
		player.setAnimation("fly_bot");
		player.scale = 0.8;
		player.velocityY = 4;
		"""

		blocks = []

		# 1. Create player
		player = self.getChoice("player")
        player_code = self.expand(player)
        blocks.append(player)

        random.shuffle(blocks)

        return "".join(blocks)

