import numpy as np
import random
import string
from copy import copy
from ideaToText import Decision
import numpy as np
"""
function draw() {
// Falling
// Player Controls
// Sprite Interactions
}
"""
class Draw(Decision):
    def registerChoices(self):
        return

    def updateRubric(self):
        return

    def render(self):
        # Generate decisions
        blocks = []

        # Append each decision code block to blocks.
        #draw_function_name = self.expand('DrawFunctionName') = {DrawFunctionName}
        draw_function_code = "function {DrawFunctionName}() {{ \n\n"
        blocks.append(draw_function_code)

        sub_blocks = []
        rock_loop_code = self.expand('RockLoop')
        sub_blocks.append(rock_loop_code)

        player_controls_code = self.expand('PlayerControls')
        sub_blocks.append(player_controls_code)

        sprite_interactions_code = self.expand('SpriteInteractions')
        sub_blocks.append(sprite_interactions_code)

        random.shuffle(sub_blocks)
        blocks.extend(sub_blocks)
        
        blocks.append('\t// Draw Sprites\n')
        blocks.append('\tdrawSprites(); \n\n')
        blocks.append('\t// Game Over\n')
        blocks.append(self.expand('GameOver'))

        blocks.append("}} \n\n")
        return ''.join(blocks)

class DrawFunctionName(Decision):
    def registerChoices(self):
        values = {}
        for _ in range(20):
            # NOTE: Consider coding this up to generate names in lower camel-case instead.
            name = ''.join(random.choices(string.ascii_lowercase, k=15))
            values[name] = 2

        # How should these weights be assigned?
        values['draw'] = 200
        values['Draw'] = 20
        values['draw_game'] = 20
        values['DrawGame'] = 20
        values['d'] = 20
        values['D'] = 20
        values['Draw_Game'] = 20

        self.addChoice('function_name', values)

    #def updateRubric(self):
    # Nothing to grade here. As long as a name is chosen, the choice doesn't really matter.

    def render(self):
        return self.getChoice("function_name")