import numpy as np
import random
import string
from copy import copy
from ideaToText import Decision
import numpy as np
"""
// reset the coin when the player touches it
  if (player.isTouching(coin)) {
    coin.x = randomNumber(50, 350);
    coin.y = randomNumber(50, 350);
  }

  // make the obstacles push the player

  if (rockX.isTouching(player)) {
    rockX.displace(player);
  }

  if (rockY.isTouching(player)) {
    rockY.displace(player);
  }

  // DRAW SPRITES
  drawSprites();

  // GAME OVER
  if (player.x < -50 || player.x > 450 || player.y < -50 || player.y > 450) {
    background("black");
    textSize(50);
    fill("green");
    text("Game Over!", 50, 200);
  }
}
"""