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
        #   self.turnOnRubric("Inappropriate scale for sprite")

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
        sub_blocks = []
        player_var_name = self.expand('PlayerVarName')
        player_var_code = f"var {player_var_name} = createSprite({x_coord}, {y_coord}); \n"
        blocks.append(player_var_code)

        player_animation_code = f"{player_var_name}.setAnimation(\"{player_to_animate}\"); \n"
        sub_blocks.append(player_animation_code)

        player_scale_code = f"{player_var_name}.scale = {scale}; \n"
        sub_blocks.append(player_scale_code)

        player_velocityX_code = f"{player_var_name}.velocityX = {velocityX}; \n"
        sub_blocks.append(player_velocityX_code)

        player_velocityY_code = f"{player_var_name}.velocityY = {velocityY}; \n"
        sub_blocks.append(player_velocityY_code)

        random.shuffle(sub_blocks)
        blocks.extend(sub_blocks)
        blocks.append("\n")
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

    #def updateRubric(self):
    # Nothing to grade here. As long as a name is chosen, the choice doesn't really matter.

    def render(self):
        return self.getChoice("player_var_name")
"""
var coin = createSprite(randomNumber(50, 350), randomNumber(50, 350));
coin.setAnimation("coin");
"""
class Coin(Decision):
    def registerChoices(self):
        self.addChoice('x_coord', dict(
            [(str(i), 1) for i in range(-1000, 1000)]
        ))

        self.addChoice('y_coord', dict(
            [(str(i), 1) for i in range(-1000, 1000)]
        ))

        self.addChoice('player_to_animate', {
            'fly_bot': 2,
            'coin': 20,
            'rock': 2,
            'other': 2
            }
        )

    def updateRubric(self):
        # X and Y coordinates might need to be even more narrow than we have defined here.
        if(self.getChoice('x_coord') not in range(0, 400)):
            self.turnOnRubric("X coordinate out of bounds")
        if(self.getChoice('y_coord') not in range(0, 400)):
            self.turnOnRubric("Y coordinate out of bounds")

        if(self.getChoice('player_to_animate') != 'coin'):
            self.turnOnRubric("Coin not selected. Wrong item animated.")

    def render(self):
        x_coord = self.getChoice('x_coord')
        y_coord = self.getChoice('y_coord')
        player_to_animate = self.getChoice('player_to_animate')

        blocks = []

        coin_var_name = self.expand('CoinVarName')
        coin_var_code = f"var {coin_var_name} = createSprite({x_coord}, {y_coord}); \n"
        blocks.append(coin_var_code)

        player_animation_code = f"{coin_var_name}.setAnimation(\"{player_to_animate}\"); \n"
        blocks.append(player_animation_code)
        blocks.append("\n")
        return ''.join(blocks)

class CoinVarName(Decision):
    def registerChoices(self):
        values = {}
        for _ in range(20):
            name = ''.join(random.choices(string.ascii_lowercase, k=5))
            values[name] = 2

        # How should these weights be assigned?
        values['coin'] = 200
        values['Coin'] = 20
        values['Coins'] = 20
        values['coins'] = 20
        values['c'] = 20
        values['C'] = 20

        self.addChoice('coin_var_name', values)

    #def updateRubric(self):
    # Nothing to grade here. As long as a name is chosen, the choice doesn't really matter.

    def render(self):
        return self.getChoice("coin_var_name")

"""
var rockX = createSprite(0, randomNumber(50, 350));
rockX.setAnimation("rock");
rockX.velocityX = 4;
"""
class RockX(Decision):
    def registerChoices(self):
        self.addChoice('x_coord', dict(
            [(str(i), 1) for i in range(-1000, 1000)]
        ))

        self.addChoice('y_coord', dict(
            [(str(i), 1) for i in range(-1000, 1000)]
        ))

        self.addChoice('player_to_animate', {
            'fly_bot': 2,
            'coin': 2,
            'rock': 20,
            'other': 2
            }
        )

        self.addChoice('velocityX', dict(
            [(str(round(num, 2)), 1) for num in list(np.linspace(0, 100, 1000))]
        ))

        self.addChoice('velocityY', dict(
            [(str(round(num, 2)), 1) for num in list(np.linspace(0, 100, 1000))]
        ))

    def updateRubric(self):
        # X and Y coordinates might need to be even more narrow than we have defined here.
        if(self.getChoice('x_coord') not in range(0, 400)):
            self.turnOnRubric("X coordinate out of bounds")
        if(self.getChoice('y_coord') not in range(0, 400)):
            self.turnOnRubric("Y coordinate out of bounds")

        if(float(self.getChoice('velocityX')) > 100 or float(self.getChoice('velocityX')) < 0):
            self.turnOnRubric("Inappropriate X velocty")

        if(float(self.getChoice('velocityY')) != 0):
            self.turnOnRubric("Y velocity should be zero for rock_x")

        if(self.getChoice('player_to_animate') != 'rock'):
            self.turnOnRubric("Rock not selected. Wrong item animated.")

    def render(self):
        x_coord = self.getChoice('x_coord')
        y_coord = self.getChoice('y_coord')
        x_velocity = self.getChoice('velocityX')
        y_velocity = self.getChoice('velocityY')
        player_to_animate = self.getChoice('player_to_animate')

        blocks = []
        sub_blocks = []
        rockX_var_name = self.expand('RockXVarName')
        rockX_var_code = "var {} = createSprite({}, {}); \n".format(rockX_var_name, x_coord, y_coord)
        blocks.append(rockX_var_code)

        player_animation_code = f"{rockX_var_name}.setAnimation(\"{player_to_animate}\"); \n"
        sub_blocks.append(player_animation_code)

        rockX_velocityX_code = f"{rockX_var_name}.velocityX = {x_velocity}; \n"
        sub_blocks.append(rockX_velocityX_code)

        random.shuffle(sub_blocks)
        blocks.extend(sub_blocks)
        blocks.append("\n")
        return ''.join(blocks)

class RockXVarName(Decision):
    def registerChoices(self):
        values = {}
        for _ in range(20):
            name = ''.join(random.choices(string.ascii_lowercase, k=5))
            values[name] = 2

        # How should these weights be assigned?
        values['rock1'] = 20
        values['rockX'] = 200
        values['rock2'] = 20
        values['r'] = 20
        values['Rock1'] = 20
        values['RockX'] = 200
        values['Rock2'] = 20
        values['R'] = 20

        self.addChoice('rockX_var_name', values)

    #def updateRubric(self):
    # Nothing to grade here. As long as a name is chosen, the choice doesn't really matter.

    def render(self):
        return self.getChoice("rockX_var_name")

"""
var rockY = createSprite(randomNumber(50, 350), 0);
rockY.setAnimation("rock");
rockY.velocityY = 4;
"""
class RockY(Decision):
    def registerChoices(self):
        self.addChoice('x_coord', dict(
            [(str(i), 1) for i in range(-1000, 1000)]
        ))

        self.addChoice('y_coord', dict(
            [(str(i), 1) for i in range(-1000, 1000)]
        ))

        self.addChoice('player_to_animate', {
            'fly_bot': 2,
            'coin': 2,
            'rock': 20,
            'other': 2
            }
        )

        self.addChoice('velocityX', dict(
            [(str(round(num, 2)), 1) for num in list(np.linspace(0, 100, 1000))]
        ))

        self.addChoice('velocityY', dict(
            [(str(round(num, 2)), 1) for num in list(np.linspace(0, 100, 1000))]
        ))

    def updateRubric(self):
        # X and Y coordinates might need to be even more narrow than we have defined here.
        if(self.getChoice('x_coord') not in range(0, 400)):
            self.turnOnRubric("X coordinate out of bounds")
        if(self.getChoice('y_coord') not in range(0, 400)):
            self.turnOnRubric("Y coordinate out of bounds")

        if(float(self.getChoice('velocityX')) > 100 or float(self.getChoice('velocityX')) < 0):
            self.turnOnRubric("Inappropriate X velocty")

        if(float(self.getChoice('velocityX')) != 0):
            self.turnOnRubric("Y velocity should be zero for rock_x")

        if(self.getChoice('player_to_animate') != 'rock'):
            self.turnOnRubric("Rock not selected. Wrong item animated.")

    def render(self):
        x_coord = self.getChoice('x_coord')
        y_coord = self.getChoice('y_coord')
        x_velocity = self.getChoice('velocityX')
        y_velocity = self.getChoice('velocityY')
        player_to_animate = self.getChoice('player_to_animate')

        blocks = []

        rockY_var_name = self.expand('RockYVarName')
        rockY_var_code = f"var {rockY_var_name} = createSprite({x_coord}, {y_coord}); \n"
        blocks.append(rockY_var_code)

        player_animation_code = f"{rockY_var_name}.setAnimation(\"{player_to_animate}\"); \n"
        blocks.append(player_animation_code)

        rockY_velocityY_code = f"{rockY_var_name}.velocityY = {y_velocity}; \n"
        blocks.append(rockY_velocityY_code)
        
        random.shuffle(blocks)

        return ''.join(blocks)

class RockYVarName(Decision):
    def registerChoices(self):
        values = {}
        for _ in range(20):
            name = ''.join(random.choices(string.ascii_lowercase, k=5))
            values[name] = 2

        # How should these weights be assigned?
        values['rock1'] = 20
        values['rockY'] = 200
        values['rock2'] = 20
        values['r'] = 20
        values['Rock1'] = 20
        values['RockY'] = 200
        values['Rock2'] = 20
        values['R'] = 20

        self.addChoice('rockY_var_name', values)

    #def updateRubric(self):
    # Nothing to grade here. As long as a name is chosen, the choice doesn't really matter.

    def render(self):
        return self.getChoice("rockY_var_name")