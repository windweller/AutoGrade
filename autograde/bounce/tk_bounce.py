"""
This is a transition file
where we kinda take breakout-tk and modify it to bounce

Because this is the fastest way
Then we will modularize this
"""

import sys

import math

from autograde.bounce.graphics import Canvas
import random
import time

import tkinter

from PIL import ImageTk

"""
Dimensions of the canvas, in pixels
These should be used when setting up the initial size of the game,
but in later calculations you should use canvas.get_canvas_width() and 
canvas.get_canvas_height() rather than these constants for accurate size information.
"""

# TODO: it's possible that we can actually scale this down quite drastically

CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400

# Stage 1: Set up the Bricks

# Number of bricks in each row
NBRICK_COLUMNS = 10

# Number of rows of bricks
NBRICK_ROWS = 10

# Separation between neighboring bricks, in pixels
BRICK_SEP = 4

# Width of each brick, in pixels
BRICK_WIDTH = math.floor((CANVAS_WIDTH - (NBRICK_COLUMNS + 1.0) * BRICK_SEP) / NBRICK_COLUMNS)

# Height of each brick, in pixels
BRICK_HEIGHT = 8

# Offset of the top brick row from the top, in pixels
BRICK_Y_OFFSET = 70

# Stage 2: Create the Bouncing Ball

# Radius of the ball in pixels
BALL_RADIUS = 10

# The ball's vertical velocity.
VELOCITY_Y = 6.0

# The ball's minimum and maximum horizontal velocity; the bounds of the
# initial random velocity that you should choose (randomly +/-).
VELOCITY_X_MIN = 2.0
VELOCITY_X_MAX = 6.0

# Animation delay or pause time between ball moves (in seconds)
DELAY = 1 / 60

# Stage 3: Create the Paddle

# Dimensions of the paddle
PADDLE_WIDTH = 60
PADDLE_HEIGHT = 10

# Offset of the paddle up from the bottom
PADDLE_Y_OFFSET = 30

# Stage 5: Polish and Finishing Up

# Number of turns
NTURNS = 3

total_wall_width = 7

# TODO: start with game logic:
# TODO: 2. Multi-ball situation (need some serious rewrite (might do it with step 3)
# TODO: 3. Re-package it into modular rep, so we can load JSON and configure on the fly
# TODO:    JSON ignores all commands on theme change though

def setup_background(canvas: Canvas, path):
    img = tkinter.PhotoImage(file=path)
    background_label = tkinter.Label(canvas.main_window, image=img)
    background_label.place(x=0, y=0, anchor='nw', relwidth=1.0, relheight=1.0)
    canvas.pack()
    canvas.update()

# these will be inside a Class
def main():
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    canvas.set_canvas_title("Bounce")

    # set up background
    # setup_background(canvas, "./bounce_assets/background.png")
    # canvas.create_image(0, 0, "./bounce_assets/background.png")
    # canvas.create_image_with_size(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, "./bounce_assets/wall.png")

    canvas.set_canvas_background_color('floral white')

    setup_walls(canvas)

    # setup_bricks(canvas)
    paddle = setup_paddle(canvas)
    ball = setup_ball(canvas)
    # ball2 = setup_ball(canvas)

    # canvas.main_window.bind("<LEFT>", move_left(canvas, paddle))
    # canvas.main_window.bind("<RIGHT>", move_left(canvas, paddle))

    canvas.wait_for_click()

    play_game(canvas, ball, paddle)

    # canvas.mainloop()

def setup_walls(canvas):

    # left wall
    brick = canvas.create_rectangle(0, 0, total_wall_width, 400)
    canvas.set_color(brick, 'red')

    # right wall
    brick = canvas.create_rectangle(CANVAS_WIDTH - total_wall_width, 0, CANVAS_WIDTH, 400)
    canvas.set_color(brick, 'red')

    # top left wall
    brick = canvas.create_rectangle(total_wall_width, 0, 125, total_wall_width)
    canvas.set_color(brick, 'red')

    # top right wall
    brick = canvas.create_rectangle(275, 0, CANVAS_WIDTH-total_wall_width, total_wall_width)
    canvas.set_color(brick, 'red')

# -- STAGE 1 (Bricks) --

def setup_bricks(canvas):
    """
    Draws the grid of multicolored bricks on the screen.
    The bricks are centered horizontally and drawn according
    to the brick constants for size, location and number.
    """

    # The bricks as a whole should be centered horizontally
    total_bricks_width = NBRICK_COLUMNS * BRICK_WIDTH + (NBRICK_COLUMNS - 1) * BRICK_SEP
    row_x = (canvas.get_canvas_width() - total_bricks_width) / 2

    for row in range(NBRICK_ROWS):
        # row_color = get_row_color(row)
        draw_brick_row(canvas, row_x, BRICK_Y_OFFSET + row * (BRICK_HEIGHT + BRICK_SEP), 'black')



def draw_brick_row(canvas, start_x, start_y, color):
    """
    Draws a row of bricks starting at the given coordinate, with the given fill color.
    """
    for col in range(NBRICK_COLUMNS):
        brick_x = start_x + col * (BRICK_WIDTH + BRICK_SEP)
        brick = canvas.create_rectangle(brick_x, start_y,
                                        brick_x + BRICK_WIDTH, start_y + BRICK_HEIGHT)
        canvas.set_color(brick, color)


# -- STAGE 2 (Ball) --

def initialize_ball_velocity():
    """
    Returns an initial x velocity value and y velocity value.  The x velocity
    is a random value between the min and max x velocity, and randomly positive or
    negative.  The y velocity is VELOCITY_Y.
    """
    velocity_x = random.uniform(VELOCITY_X_MIN, VELOCITY_X_MAX)
    if random.random() < 0.5:
        velocity_x *= -1
    return velocity_x, VELOCITY_Y


def setup_ball(canvas):
    """
    Creates the ball on-screen, centered, with the size
    as specified by BALL_RADIUS.  Returns the ball.
    """
    ball_x = canvas.get_canvas_width() / 2 - BALL_RADIUS
    ball_y = canvas.get_canvas_height() / 2 - BALL_RADIUS
    ball = canvas.create_oval(ball_x, ball_y,
                              ball_x + 2 * BALL_RADIUS, ball_y + 2 * BALL_RADIUS)

    # img = tkinter.PhotoImage(file='./bounce_assets/ball.png')
    # ball = canvas.create_image_with_size(ball_x, ball_y, 2 * BALL_RADIUS + 2, 2 * BALL_RADIUS + 2, './bounce_assets/ball.png')

    canvas.set_color(ball, 'black')
    return ball


# -- STAGE 3 (Paddle) --


def setup_paddle(canvas):
    """
    Creates the paddle on screen at the location and size specified in
    the paddle constants. Returns the paddle.
    """
    paddle_x = (canvas.get_canvas_width() - PADDLE_WIDTH) / 2
    paddle_y = canvas.get_canvas_height() - PADDLE_Y_OFFSET - PADDLE_HEIGHT
    paddle = canvas.create_rectangle(paddle_x, paddle_y,
                                     paddle_x + PADDLE_WIDTH, paddle_y + PADDLE_HEIGHT)
    canvas.set_color(paddle, 'black')
    return paddle


def move_paddle(canvas, paddle):
    """
    Updates the paddle location to track the location of the mouse.  Specifically,
    sets the paddle location to keep the same y coordinate, but set the x coordinate
    such that the paddle is centered around the mouse.  Constrains the paddle to be
    entirely onscreen at all times.
    """
    new_paddle_x = canvas.get_mouse_x() - PADDLE_WIDTH / 2
    new_paddle_x = max(total_wall_width, min((canvas.get_canvas_width() - total_wall_width) - PADDLE_WIDTH, new_paddle_x))
    canvas.moveto(paddle, new_paddle_x, canvas.get_top_y(paddle))

def move_left(canvas, paddle):
    """
    """
    # new_paddle_x = canvas.get_mouse_x() - PADDLE_WIDTH / 2
    old_paddle_x = canvas.get_left_x(paddle)
    new_paddle_x = old_paddle_x - 10
    new_paddle_x = max(total_wall_width, min((canvas.get_canvas_width() - total_wall_width) - PADDLE_WIDTH, new_paddle_x))
    canvas.moveto(paddle, new_paddle_x, canvas.get_top_y(paddle))

def move_right(canvas, paddle):
    """
    """
    old_paddle_x = canvas.get_left_x(paddle)
    new_paddle_x = old_paddle_x + 10
    # new_paddle_x = canvas.get_mouse_x() - PADDLE_WIDTH / 2
    new_paddle_x = max(total_wall_width, min((canvas.get_canvas_width() - total_wall_width) - PADDLE_WIDTH, new_paddle_x))
    canvas.moveto(paddle, new_paddle_x, canvas.get_top_y(paddle))

# -- STAGES 2, 4, 5 (Ball, Collisions, Finishing Touches)

def play_game(canvas, ball, paddle):
    """
    Plays the main breakout game by looping until either the player has removed all the bricks or
    they have run out of turns.  Each animation step, animate the ball and paddle and update the
    game state if the ball has collided with any walls or objects.
    """
    turns = NTURNS
    change_x, change_y = initialize_ball_velocity()
    # change_x2, change_y2 = initialize_ball_velocity()
    brick_count = NBRICK_COLUMNS * NBRICK_ROWS

    # animation loop
    while turns > 0: # and brick_count > 0:

        canvas.move(ball, change_x, change_y)
        # canvas.move(ball2, change_x2, change_y2)

        # only enter here when a new key is pressed

        # if len(canvas.key_presses) > 0:
        #     if canvas.key_presses[-1].keysym == 'Left':
        #         move_left(canvas, paddle)
        #     elif canvas.key_presses[-1].keysym == 'Right':
        #         move_right(canvas, paddle)

        move_paddle(canvas, paddle)

        change_x, change_y, ball_onscreen = bounce_off_walls(canvas, ball, change_x, change_y)

        # If the ball went off-screen, the user loses a turn
        if not ball_onscreen:
            turns -= 1
            if turns > 0:
                # Reset for another turn
                canvas.moveto(ball, canvas.get_canvas_width() / 2 - BALL_RADIUS,
                              canvas.get_canvas_height() / 2 - BALL_RADIUS)
                change_x, change_y = initialize_ball_velocity()
                canvas.wait_for_click()
        else:
            change_x, change_y, bricks_removed = check_collisions(canvas, ball, paddle, change_x, change_y)
            brick_count -= bricks_removed

        canvas.update()
        time.sleep(DELAY)

    end_game(canvas, ball, paddle, brick_count)
    canvas.update()

def bounce_off_walls(canvas, ball, change_x, change_y):
    """
    Checks collisions between the ball and walls.  If the ball is at the left/right/top walls, bounce.
    Returns the new x and y velocities, followed by True if the ball is still on screen, and False if
    it went off the bottom.
    """
    new_change_x = change_x
    new_change_y = change_y

    ball_x_right = canvas.get_left_x(ball) + canvas.get_width(ball)
    ball_y_bottom = canvas.get_top_y(ball) + canvas.get_height(ball)

    # need to account for wall thickness
    # >= 125 and <= 275 create sticky border situation
    # > 125 and < 275 create sticky border situation as well...
    if canvas.get_top_y(ball) < total_wall_width and canvas.get_left_x(ball) > 125 - 1 and ball_x_right < 275 + 1:
        # in goal!!
        # wait till it passes through
        if canvas.get_top_y(ball) < - BALL_RADIUS:
            return new_change_x, new_change_y, False

    # left wall, rightr wall
    elif canvas.get_left_x(ball) < total_wall_width or ball_x_right >= canvas.get_canvas_width() - total_wall_width:
        # Bounce horizontally
        new_change_x *= -1
    # top wall
    elif canvas.get_top_y(ball) < total_wall_width:
        # Bounce vertically
        new_change_y *= -1
    elif ball_y_bottom >= canvas.get_canvas_height():
        # Ball went off the bottom of the screen
        return new_change_x, new_change_y, False

    return new_change_x, new_change_y, True


def check_collisions(canvas, ball, paddle, change_x, change_y):
    """
    Checks collisions between the ball and other objects.  If the ball collided
    with the paddle and is going down, bounce.  If the ball collided
    with a brick, remove it.  Returns the updated ball velocities and how many bricks
    were removed.
    """

    new_change_x = change_x
    new_change_y = change_y
    bricks_removed = 0

    # this graphics method gets the location of the ball as a list
    ball_coords = canvas.coords(ball)

    # the list has four elements:
    ball_x_left = ball_coords[0]
    ball_y_top = ball_coords[1]
    ball_x_right = ball_coords[2]
    ball_y_bottom = ball_coords[3]

    # check if we collided with an object
    colliding_list = canvas.find_overlapping(ball_x_left, ball_y_top, ball_x_right, ball_y_bottom)
    for collider in colliding_list:
        if collider == paddle:
            # If colliding with the paddle, bounce only if going down
            if change_y > 0:
                new_change_y = -change_y
            break
        # elif collider != ball:
        #     # If colliding with a brick, remove it and bounce
        #     # canvas.delete(collider)
        #
        #     bricks_removed += 1
        #     new_change_y = -change_y  # without np.abs, this is actually sticky on wall
        #     break

    return new_change_x, new_change_y, bricks_removed


def end_game(canvas, ball, paddle, brick_count):
    """
    At the end of the game, checks if the user has won or lost.
    Remove the ball and paddle and add either a win or lose message.
    """
    canvas.delete(ball)
    canvas.delete(paddle)
    message = "YOU WIN!"
    if brick_count != 0:
        message = "YOU LOSE"

    canvas.create_text(canvas.get_canvas_width() / 2, canvas.get_canvas_height() / 2, message)


if __name__ == '__main__':
    main()
