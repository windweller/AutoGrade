import random
import string
from copy import copy
from ideaToText import Decision
import numpy as np
"""
var player = createSprite(200, 100);
player.setAnimation("fly_bot");
player.scale = 0.8;
player.velocityY = 4;
"""
class Player(Decision):
	def registerChoices(self):
		# TODO: Study appropriate ranges, anticipate student mistakes, adjust rubric accordingly.
		self.addChoice('x_coord', range(-1000, 1000))

		self.addChoice('y_coord', range(-1000, 1000))

		# I believe choice of animation is arbtirary, but i'll start by defining the
		# fly bot as the target and the other two as the obstacles.
		self.addChoice('player_to_animate', 
			'fly_bot',
			'coin',
			'rock',
			'other'
		)

		self.addChoice('scale', list(np.linspace(0, 100, 1000)))

		self.addChoice('velocityX', list(np.linspace(0, 10, 100)))

		self.addChoice('velocityY', list(np.linspace(0, 10, 100)))

	def updateRubric(self):
		# X and Y coordinates might need to be even more narrow than we have defined here.
		if(self.getChoice('x_coord') not in range(0, 400)):
			self.turnOnRubric("X coordinate out of bounds")
		if(self.getChoice('y_coord') not in range(0, 400)):
			self.turnOnRubric("Y coordinate out of bounds")

		if(self.getChoice('player_to_animate') != 'fly_bot'):
			self.turnOnRubric("Fly Bot not selected. Wrong item animated.")

		# We should define some range  for the scale and velocity that we feel comfortable referring to as a "correct" submission
		# Maybe we can define the maximum scale of the player to be something arbitrary like 1/3rd of the window size?
		#if(self.getChoce('scale') not in range(start, end)):
		#	self.turnOnRubric("Inappropriate scale for sprite")

		# We should define some range  for the scale and velocity that we feel comfortable referring to as a "correct" submission
		if(self.getChoce('velocityX') not in range(start, end)):
		#	self.turnOnRubric("Inappropriate X velocty")

	def render(self):
		x_coord = self.getChoice('x_coord')
		y_coord = self.getChoice('y_coord')
		player_to_animate = self.getChoice('player_to_animate')
		scale = self.getChoice('scale')
		velocityX = self.getChoice('velocityX')
		velocityY = self.getChoice('velocityY')

		blocks = []

		player_var_name = self.expand('PlayerVarName')
		player_var_code = f"var {player_var_name} = createSprite({x_coord}, {y_coord}); \n"
		blocks.append(player_var_code)

		player_animation_code = f"{player_var_name}.setAnimation(\"{player_to_animate}\"); \n"
		blocks.append(player_animation_code)

		player_scale_code = f"{player_var_name}.scale = {scale}; \n"
		blocks.append(player_scale_code)

		player_velocityX_code = f"{player_var_name}.velocityX = {velocityX}; \n"
		blocks.append(player_velocityX_code)

		player_velocityY_code = f"{player_var_name}.velocityY = {velocityY}; \n"
		blocks.append(player_velocityY_code)

		return ''.join(blocks)

class PlayerVarName(Decision):
    def registerChoices(self):
        values = {}
        for _ in range(20):
            name = ''.join(random.choices(string.ascii_lowercase, k=5))
            values[name] = 2

        # How should these weights be assigned?
        values['player'] = 200
        values['players'] = 20
        values['Player'] = 20
        values['players'] = 20
        values['plyer'] = 20
        values['p'] = 20
        values['plyr'] = 20 

        self.addChoice('player_var_name', values)

    def updateRubric(self):
    	# Nothing to grade here. As long as a name is chosen, the choice doesn't really matter.

    def render(self):
        return self.getChoice("player_var_name")