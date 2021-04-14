import numpy as np
import random
import string
from copy import copy
from ideaToText import Decision
import numpy as np
"""
Rock Loop Template
if (rockX.x > 450) {
    rockX.x = -50;
    rockX.y = randomNumber(50, 350);
  }

if (rockY.y > 450) {
   rockY.y = -50;
   rockY.x = randomNumber(50, 350);
}
"""
class RockLoop(Decision):
	# def registerChoices(self):
 	# def updateRubric(self):
 	def render(self):
 		blocks = []

 		rock_x_check = self.expand('RockCheck', params={'rock_to_check': 'x'})
 		blocks.append(rock_x_check)

 		rock_y_check = self.expand('RockCheck', params={'rock_to_check': 'y'})
 		blocks.append(rock_y_check)

 		random.shuffle(blocks)
 		blocks.append("\n")
 		return ' '.join(blocks)

class RockCheck(Decision):
	def registerChoices(self):
		self.addChoice('direction', {
			self.params['rock_to_check'] : 1
		})
		
		self.addChoice('comparator', {
			'>': 10,
			'<': 10,
			'>=' : 8,
			'<=' : 8,
			'==': 5,
			'=': 1,
			'!=': 2,
			'=!': 1
		})
		
		vals = {i : 2 for i in range(-1000, 1000)}
		vals[450] = 20
		vals[449] = 5
		vals[-450] = 5
		vals[451] = 5
		vals[-449] = 5
		self.addChoice('limit', vals)

		vals[450] = 2
		vals[-50] = 20
		vals[50] = 5
		vals[-49] = 5
		vals[-51] = 5
		self.addChoice('first_pos', vals)

		# The following lists can be refined a bit further.
		vals = {i : 2 for i in range(-1000, 1000)}
		vals[50] = 20
		self.addChoice('second_pos_lower', vals)

		vals[50] = 2
		vals[350] = 20
		self.addChoice('second_pos_upper', vals)

	#def updateRubric(self):

	def render(self):
		blocks = []
		inner = []

		if_block_code = "\t if ("
		rock_name = ""
		if(self.params['rock_to_check'] == 'x'):
			blocks.append("\t// Rock X Loop Check \n")
			rock_name = '{RockXVarName}'
			if_block_code += rock_name
			if_block_code += ".x "
		else:
			blocks.append("\t// Rock Y Loop Check \n")
			rock_name = self.expand('RockYVarName')
			if_block_code += rock_name
			if_block_code += ".y "

		# TODO: shuffle in-line comparison direction.
		if_block_code += self.getChoice('comparator') + " "
		if_block_code += str(self.getChoice('limit')) + ") {{ \n"
		blocks.append(if_block_code)

		first_pos_code = "\t\t" + rock_name
		second_pos_code = "\t\t" + rock_name
		if(self.params['rock_to_check'] == 'x'):
			first_pos_code += ".x = "
			second_pos_code += ".y = "
		else:
			first_pos_code += ".y = "
			second_pos_code += ".x = "
		first_pos_code += str(self.getChoice('first_pos'))
		first_pos_code += "; \n"
		inner.append(first_pos_code)

		second_pos_code += "randomNumber("
		second_pos_code += str(self.getChoice('second_pos_lower')) + ", "
		second_pos_code += str(self.getChoice('second_pos_upper'))
		second_pos_code += "); \n"
		inner.append(second_pos_code)

		random.shuffle(inner)
		blocks.extend(inner)

		blocks.append("\t}} \n")
		return ''.join(blocks)
