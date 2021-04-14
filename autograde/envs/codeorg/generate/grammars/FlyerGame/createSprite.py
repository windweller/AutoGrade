import random
import string
from copy import copy
from ideaToText import Decision
import numpy as np
"""
var {name} = createSprite({x_coord}, {y_coord});
player.setAnimation({player_to_animate});
player.scale = {scale};
player.velocityX = {velocityX};
player.velocityY = {velocityY};
"""
"""
class Player(Decision):
	def registerChoices(self):
		# TODO: Study appropriate ranges, anticipate student mistakes, adjust rubric accordingly.
		self.addChoice('x_coord', dict(
			[(str(i), 1) for i in range(-1000, 1000)]
		))

		self.addChoice('y_coord', dict(
			[(str(i), 1) for i in range(-1000, 1000)]
		))

		# I believe choice of animation is arbtirary, but i'll start by defining the
		# fly bot as the target and the other two as the obstacles.
		self.addChoice('player_to_animate', {
			'fly_bot': 20,
			'coin': 2,
			'rock': 2,
			'other': 2
			}
		)

		self.addChoice('scale', dict(
			[(str(round(num, 2)), 1) for num in list(np.linspace(0, 100, 1000))]
		))

		self.addChoice('velocityX', dict(
			[(str(round(num, 2)), 1) for num in list(np.linspace(0, 100, 1000))]
		))

		self.addChoice('velocityY', dict(
			[(str(round(num, 2)), 1) for num in list(np.linspace(0, 100, 1000))]
		))

	# NOTE: RUBRIC Should vary based on piece being created.
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
		# Maybe we can define this by choosing an arbitrary length of time that the player should have to react before losing the game
		# due to inactivity, though this seems like overkill for the purposes of code.org.
		if(float(self.getChoice('velocityX')) > 100 or float(self.getChoice('velocityX')) < 0):
			self.turnOnRubric("Inappropriate X velocty")

		if(float(self.getChoice('velocityY')) > 100 or float(self.getChoice('velocityY')) < 0):
			self.turnOnRubric("Inappropriate Y velocty")

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
"""