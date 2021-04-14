import numpy as np
import random
import string
from copy import copy
from ideaToText import Decision
import numpy as np

class SpriteInteractions(Decision):
  def render(self):
    blocks = []

    coin_reset_code = self.expand('CoinReset')
    blocks.append(coin_reset_code)

    solid_obstacles_code = self.expand('SolidObstacles')
    blocks.append(solid_obstacles_code)

    random.shuffle(blocks)
    return ''.join(blocks)

class CoinReset(Decision):
  def registerChoices(self):
    self.addChoice('interaction_function', {
      'isTouching': 10,
      'bounce' : 1,
      'bounceOff': 1,
      'collide': 1,
      'displace':1,
      'setCollider':1, 
    })

    self.addChoice('lower_bound', dict(
      [(str(i), 1) for i in range(-1000, 1000)]
    ))

    self.addChoice('upper_bound', dict(
      [(str(i), 1) for i in range(-1000, 1000)]
    ))

  #def updateRubric(self):
    # Check that interaction_function == isTouching
    # Check that both lower bound and upper bound are within 25-375
    # Check that lower bound < upper bound

  def render(self):
    """
    // reset the coin when the player touches it
    if (player.isTouching(coin)) {
      coin.x = randomNumber(50, 350);
      coin.y = randomNumber(50, 350);
    }
    """
    player_name = self.expand('PlayerVarName')
    interaction_function = self.getChoice('interaction_function')
    coin_var_name = self.expand('CoinVarName')
    lower_bound = self.getChoice('lower_bound')
    upper_bound = self.getChoice('upper_bound')

    blocks = []

    if_start_line = f"\tif ({player_name}.{interaction_function}({coin_var_name})) " + "{{\n"
    blocks.append(if_start_line)

    sub_blocks = []
    coin_x_line = f"\t\t{coin_var_name}.x = randomNumber({lower_bound}, {upper_bound}); \n"
    sub_blocks.append(coin_x_line)

    coin_y_line = f"\t\t{coin_var_name}.y = randomNumber({lower_bound}, {upper_bound}); \n"
    sub_blocks.append(coin_y_line)

    random.shuffle(sub_blocks)
    blocks.extend(sub_blocks)

    blocks.append("\t}}\n\n")
    return ''.join(blocks)



class SolidObstacles(Decision):
  def registerChoices(self):
    self.addChoice('interaction_function', {
      'isTouching': 10,
      'bounce' : 1,
      'bounceOff': 1,
      'collide': 1,
      'displace':1,
      'setCollider':1, 
    })

    self.addChoice('displace_function', {
      'isTouching': 11,
      'bounce' : 1,
      'bounceOff': 1,
      'collide': 1,
      'displace': 10,
      'setCollider':1, 
    })

  def render(self):
    """
    // make the obstacles push the player
    if (rockX.isTouching(player)) {
     rockX.displace(player);
    }

    if (rockY.isTouching(player)) {
      rockY.displace(player);
    }
    """
    player_name = self.expand('PlayerVarName')
    rock_x_var_name = self.expand('RockXVarName')
    rock_y_var_name = self.expand('RockYVarName')
    interaction_function = self.getChoice('interaction_function')
    displace_function = self.getChoice('displace_function')

    blocks = []

    x_blocks = []
    start_if_line = f"\tif ({rock_x_var_name}.{interaction_function}({player_name})) " + "{{\n"
    x_blocks.append(start_if_line)

    displacement_line = f"\t\t{rock_x_var_name}.{displace_function}({player_name}); \n"
    x_blocks.append((displacement_line))

    x_blocks.append("\t}}\n\n")

    y_blocks = []
    start_if_line = f"\tif ({rock_y_var_name}.{interaction_function}({player_name})) " + "{{\n"
    y_blocks.append(start_if_line)

    displacement_line = f"\t\t{rock_y_var_name}.{displace_function}({player_name}); \n"
    y_blocks.append((displacement_line))

    y_blocks.append("\t}}\n\n")

    blocks.append(x_blocks)
    blocks.append(y_blocks)

    random.shuffle(blocks)
    new_blocks = [''.join(block) for block in blocks]
    return ''.join(new_blocks)

class GameOver(Decision):
  def render(self):
    """
    // GAME OVER
    if (player.x < -50 || player.x > 450 || player.y < -50 || player.y > 450) {
      background("black");
      textSize(50);
      fill("green");
      text("Game Over!", 50, 200);
    }
    """
    player_name = self.expand('PlayerVarName')
    blocks = []
    start_if_line = f"\tif ({player_name}.x < -50 || {player_name}.x > 450 || {player_name}.y < -50 || {player_name}.y > 450) " + "{{ \n"
    blocks.append(start_if_line)
    blocks.append("\t\tbackground(\"black\");\n")
    blocks.append("\t\ttextSize(50);\n")
    blocks.append("\t\tfill(\"green\");\n")
    blocks.append("\t\ttext(\"GameOver!\", 50, 200); \n")
    blocks.append("\t}}\n\n")

    return ''.join(blocks)
