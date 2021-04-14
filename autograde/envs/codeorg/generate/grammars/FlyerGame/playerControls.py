import numpy as np
import random
import string
from copy import copy
from ideaToText import Decision
import numpy as np

class PlayerControls(Decision):
  #def registerChoices(self):
  #def updateRubric(self):
  def render(self):
    blocks = []
    blocks.append("\n")

    key_up_code = self.expand('KeyUp')
    blocks.append(key_up_code)

    key_left_code = self.expand('KeyLeft')
    blocks.append(key_left_code)

    key_right_code = self.expand('KeyRight')
    blocks.append(key_right_code)

    random.shuffle(blocks)
    return ''.join(blocks)

class KeyUp(Decision):
  def registerChoices(self):
    self.addChoice("feature_to_decrease", {
      "velocityY" : 10,
      "velocityX" : 4,
      "scale" : 1, 
      "visible" : 1,
      "rotationSpeed" : 1,
      "x" : 2,
      "y" : 4,
    })

    self.addChoice("jump_speed",
      dict(
        [(str(i), 1) for i in range(-20, 20)]
      ))

    self.addChoice("feature_to_increase", {
      "velocityY" : 10,
      "velocityX" : 4,
      "scale" : 1, 
      "visible" : 1,
      "rotationSpeed" : 1,
      "x" : 2,
      "y" : 4,
    })

    self.addChoice("upper_bound",
      dict(
        [(str(i), 1) for i in range(-20, 20)]
      ))

    self.addChoice('comparator', {
      '>=': 10,
      '<=': 10,
      '<' : 8,
      '>' : 8,
      '==': 5,
      '=': 1,
      '!=': 2,
      '=!': 1
    })

    self.addChoice('increase_size',
      dict(
        [(str(i), 1) for i in range(-10, 10)]
      ))

    self.addChoice('increase_operation', {
      '+' : 1,
      '-' : 1,
      '+=' : 4,
      '-=' : 2,
      '=': 1  
    })

  def updateRubric(self):
    if(self.getChoice("feature_to_decrease") != "velocityY"):
      self.turnOnRubric("Decreasing wrong feature when falling. Should have decreased velocityY") 

    if(int(self.getChoice('jump_speed')) >= 0):
      self.turnOnRubric("Made sprite fall faster instead of jumping.")

    comparator = self.getChoice('comparator')
    if(comparator != '<' and comparator != '<=' and comparator != '>=' and comparator != '>'):
      self.turnOnRubric("Not using an appropriate comparator. Should be checking for an upper or lower bound.")

    if((comparator == '<=' or comparator == '<') and int(self.getChoice('upper_bound')) < 0): # <= -1
      self.turnOnRubric("Checking if velocity is <= negative (rather than positive) number.")
    
    if((comparator == '>=' or comparator == '>') and int(self.getChoice('upper_bound')) > 0): # >= 1
      self.turnOnRubric("Checking if velocity is >= positve (rather than negative) number.")
    
    increase_operation = self.getChoice('increase_operation')
    if(increase_operation != '+=' and increase_operation != '-='):
      self.turnOnRubric("Not doing a linear decrement or increment during up key.")

    increase_size = int(self.getChoice('increase_size'))
    if(increase_operation == '+=' and increase_size <= 0):
      self.turnOnRubric("Decreasing Y velocity on upclick instead of increasing.")

    if(increase_operation == '-=' and increase_size >= 0):
      self.turnOnRubric("Decreasing Y velocity on upclick instead of increasing.")

  def render(self):
    """
    Player Controls Template
    if (keyDown("up")) {
      player.velocityY = -10;
    } else {
      if (player.velocityY <= 10) {
        player.velocityY += 1;
      }
    }
   """
    feature_to_decrease = self.getChoice("feature_to_decrease")
    jump_speed = self.getChoice("jump_speed")
    feature_to_increase = self.getChoice("feature_to_increase")
    comparator = self.getChoice("comparator")
    upper_bound = self.getChoice("upper_bound")
    increase_operation = self.getChoice("increase_operation")
    increase_size = self.getChoice("increase_size")

    blocks = []

    blocks.append("\t// Up click functionality \n")
    start_line = "\tif (keyDown(\"up\")) {{ \n"
    blocks.append(start_line)
    
    player_name = str({'PlayerVarName'})
    subtract_y_velocity = f"\t\t{player_name}.{feature_to_decrease} = {jump_speed}; \n"
    blocks.append(subtract_y_velocity)

    else_line = "\t}} else {{\n"
    blocks.append(else_line)

    check_max_line = f"\t\tif({player_name}.{feature_to_increase} {comparator} {upper_bound}) " + "{{ \n"
    blocks.append(check_max_line)

    increase_y_velocity_code = f"\t\t\t{player_name}.{feature_to_increase} {increase_operation} {increase_size}; \n"
    blocks.append(increase_y_velocity_code)

    blocks.append("\t\t}}\n")
    blocks.append("\t}}\n")
    blocks.append("\n")

    return ''.join(blocks)

class KeyLeft(Decision):
  """
  // decrease the x velocity when user clicks "left"

  if (keyDown("left")) {
    if (player.velocityX > -2) {
      player.velocityX -= 0.2;
    }
  }
  """
  def registerChoices(self):
    self.addChoice("feature_to_increase", {
      "velocityY" : 4,
      "velocityX" : 10,
      "scale" : 1, 
      "visible" : 1,
      "rotationSpeed" : 1,
      "x" : 4,
      "y" : 2,
    })

    self.addChoice('comparator', {
      '>=': 10,
      '<=': 10,
      '<' : 8,
      '>' : 8,
      '==': 5,
      '=': 1,
      '!=': 2,
      '=!': 1
    })

    self.addChoice('lower_bound', dict(
      [(str(i), 1) for i in range(-20, 20)]
    ))

    self.addChoice('speed_change', dict(
      [(str(i), 1) for i in range(-20, 20)]
    ))

    self.addChoice('speed_change_operation', {
      '+' : 1,
      '-' : 1,
      '+=' : 4,
      '-=' : 2,
      '=': 1  
    })

  #def updateRubcric(self):
  def render(self):
    player_name = str({'PlayerVarName'})
    feature_to_increase = self.getChoice('feature_to_increase')
    comparator = self.getChoice('comparator')
    lower_bound = self.getChoice('lower_bound')
    speed_change = self.getChoice('speed_change')
    speed_change_operation = self.getChoice('speed_change_operation')

    blocks = []
    
    blocks.append("\t// Left click functionality \n")
    start_line = "\tif (keyDown(\"left\")) {{ \n"
    blocks.append(start_line)

    comparison_line = f"\t\tif({player_name}.{feature_to_increase} {comparator} {lower_bound}) " + "{{ \n"
    blocks.append(comparison_line)

    increase_x_velocity_code = f"\t\t\t{player_name}.{feature_to_increase} {speed_change_operation} {speed_change}; \n"
    blocks.append(increase_x_velocity_code)

    blocks.append("\t\t}}\n")
    blocks.append("\t}}\n")
    blocks.append("\n")

    return ''.join(blocks)

class KeyRight(Decision):
  def registerChoices(self):
    self.addChoice("feature_to_increase", {
      "velocityY" : 4,
      "velocityX" : 10,
      "scale" : 1, 
      "visible" : 1,
      "rotationSpeed" : 1,
      "x" : 4,
      "y" : 2,
    })

    self.addChoice('comparator', {
      '>=': 10,
      '<=': 10,
      '<' : 8,
      '>' : 8,
      '==': 5,
      '=': 1,
      '!=': 2,
      '=!': 1
    })

    self.addChoice('lower_bound', dict(
      [(str(i), 1) for i in range(-20, 20)]
    ))

    self.addChoice('speed_change', dict(
      [(str(i), 1) for i in range(-20, 20)]
    ))

    self.addChoice('speed_change_operation', {
      '+' : 1,
      '-' : 1,
      '+=' : 4,
      '-=' : 2,
      '=': 1  
    })

  #def updateRubcric(self):
  def render(self):
    """
  // increase the x velocity when the user clicks "right"
  if (keyDown("right")) {
    if (player.velocityX < -2) {
      player.velocityX += 0.2;
    } else {
      player.velocityX = 2;
    }
  }
  """
    player_name = str({'PlayerVarName'})
    feature_to_increase = self.getChoice('feature_to_increase')
    comparator = self.getChoice('comparator')
    lower_bound = self.getChoice('lower_bound')
    speed_change = self.getChoice('speed_change')
    speed_change_operation = self.getChoice('speed_change_operation')

    blocks = []
    blocks.append("\t// Right click functionality \n")
    start_line = "\tif (keyDown(\"right\")) {{ \n"
    blocks.append(start_line)

    comparison_line = f"\t\tif({player_name}.{feature_to_increase} {comparator} {lower_bound})" + " {{ \n"
    blocks.append(comparison_line)

    increase_x_velocity_code = f"\t\t\t{player_name}.{feature_to_increase} {speed_change_operation} {speed_change}; \n"
    blocks.append(increase_x_velocity_code)

    blocks.append("\t\t}}\n")
    blocks.append("\t}}\n")
    blocks.append("\n")

    return ''.join(blocks)