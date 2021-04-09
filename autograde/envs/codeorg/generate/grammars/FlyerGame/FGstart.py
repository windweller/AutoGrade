import string
from ideaToText import Decision
import random

class Start(Decision):
	#def registerChoices(self):
	#def updateRubric(self):
	def render(self):
		#TODO: Replace template with FlyerGame Template as necessary
		blocks = []
		# 1. Player setup
		player_code = self.expand('Player')
		blocks.append(player_code)

		# 2. Coin setup
		coin_code = self.expand('Coin')
		blocks.append(coin_code)

		# 3. RockX setup
		rockX_code = self.expand('RockX')
		blocks.append(rockX_code)

		# 3. RockY setup
		rockY_code = self.expand('RockY')
		blocks.append(rockY_code)

		random.shuffle(blocks)

		return ''.join(blocks)

