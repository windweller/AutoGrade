"""
Difference:
instead of PyMunk, we use simple physics similar in Breakout
We also do not use PyGame, but Tkinter
"""

import math

from autograde.bounce.graphics import Canvas
import random
import time

import os
import pathlib

import json
from abc import ABC, abstractmethod

try:
    from . import utils_seeding as seeding
except:
    import utils_seeding as seeding

# if os.environ.get('DISPLAY','') == '':
#     print('no display found. Using :0.0')
#     os.environ.__setitem__('DISPLAY', ':0.0')

# os.environ['SDL_VIDEODRIVER'] = 'dummy'

# ==== Settings ====

# HARDCOURT = 'hardcourt'
# RETRO = 'retro'
# RANDOM = 'random'

# we change speed to velocity instead
# and do one time update

# speed_text_available = ['random', 'very slow', 'slow', 'normal', 'fast', 'very fast']
# speed_choices = ['very slow', 'slow', 'normal', 'fast', 'very fast']  #
# speed_dict = {
#     'very slow': 100, 'slow': 200, 'normal': 300, 'fast': 400, 'very fast': 500
# }

# theme_choices = [HARDCOURT, RETRO]
# theme_dict = {
#     'retro': RETRO,
#     'hardcourt': HARDCOURT,
#     'random': RANDOM
# }

collision_types = {
    "ball": 1,  # many balls
    "goal": 2,
    "bottom": 3,
    "paddle": 4,
    "wall": 5  # many walls
}

screen_width = 400
screen_height = 400
distance_from_boundary = 17
fps = 50
# BALL_RADIUS = 14

wall_thickness = 15

game_name = "Bounce"
PAUSE = 'Pause'

# 1: move left
# 2: move right
# 3: bounce ball
# 4: score point
# 5: score opponent point
# 6: launch new ball
# 7: set "normal" paddle speed: ['random', 'very slow', 'slow', 'normal', 'fast', 'very fast']
# 8: set "normal" ball speed: ['random', 'very slow', 'slow', 'normal', 'fast', 'very fast']

# 1: set "hardcourt" scene: ['hardcourt', 'retro', 'random']
# 2: set "hardcourt" ball: ['hardcourt', 'retro', 'random']
# 3: set "hardcourt" paddle: ['hardcourt', 'retro', 'random']

MOVE_LEFT = "move left"
MOVE_RIGHT = "move right"
BOUNCE_BALL = "bounce ball"
SCORE_POINT = "score point"
SCORE_OPPO_POINT = "score opponent point"
LAUNCH_NEW_BALL = "launch new ball"

WHEN_RUN = 'when run'
WHEN_LEFT_ARROW = 'when left arrow'
WHEN_RIGHT_ARROW = 'when right arrow'

BALL_HIT_PADDLE = "when ball hits paddle"
BALL_HIT_WALL = "when ball hits wall"
BALL_IN_GOAL = "when ball in goal"
BALL_MISS_PADDLE = "when ball misses paddle"

BALL_DESTROYED = "ball destroyed"
BALL_ALREADY_IN_GOAL = "ball already in goal"

# Radius of the ball in pixels
BALL_RADIUS = 10

# The ball's vertical velocity.
VELOCITY_Y = 5.0

# The ball's minimum and maximum horizontal velocity; the bounds of the
# initial random velocity that you should choose (randomly +/-).
VELOCITY_X_MIN = 2.0
VELOCITY_X_MAX = 5.0

# Dimensions of the paddle
PADDLE_WIDTH = 60
PADDLE_HEIGHT = 10

# Offset of the paddle up from the bottom
PADDLE_Y_OFFSET = 30

total_wall_width = 7

# Number of turns
NTURNS = 5

CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400


class Config(object):
    def update(self):
        """
        This updates the self.config_dict, and set up attributes for the class
        :return:
        """
        for k, v in self.config_dict.items():
            self.__setattr__(k.replace(' ', "_"), v)

    def __getitem__(self, y):
        if "_" in y:
            y = y.replace("_", " ")
        return self.config_dict[y]

    def __setitem__(self, key, value):
        """
        :param key:
        :param value: be careful with value, it overrides things
        :return:
        """
        if "_" in key:
            key = key.replace("_", " ")
        self.config_dict[key] = value

    def save(self, file_name):
        json.dump(self.config_dict, open(file_name, "w"))

    def load(self, file_name):
        # this method overrides
        self.config_dict = json.load(open(file_name))
        self.update()

    def loads(self, json_obj):
        if type(json_obj) == str:
            result = None
            try:
                result = json.loads(json_obj)
            except:
                pass

            try:
                # we assume this is
                result = json.load(open(json_obj))
            except:
                pass

            assert result is not None, "We are not able to parse the obj you sent in"
            json_obj = result

        assert type(json_obj) == dict
        self.config_dict = json_obj
        self.update()


class Program(Config):
    def __init__(self):
        self.config_dict = {
            "when run": [],
            "when left arrow": [],
            "when right arrow": [],
            "when ball hits paddle": [],
            "when ball hits wall": [],
            "when ball in goal": [],
            "when ball misses paddle": []
        }
        self.update()

    def set_correct(self):
        # we generate a correct program
        self.config_dict['when run'].append(LAUNCH_NEW_BALL)
        self.config_dict['when left arrow'].append(MOVE_LEFT)
        self.config_dict['when right arrow'].append(MOVE_RIGHT)
        self.config_dict['when ball hits paddle'].append(BOUNCE_BALL)
        self.config_dict['when ball hits wall'].append(BOUNCE_BALL)
        self.config_dict['when ball in goal'].append(SCORE_POINT)
        self.config_dict['when ball in goal'].append(LAUNCH_NEW_BALL)
        self.config_dict['when ball misses paddle'].append(SCORE_OPPO_POINT)
        self.config_dict['when ball misses paddle'].append(LAUNCH_NEW_BALL)

    def to_features(self):
        # compile the program into a one-hot encoding
        # used for code-as-text classifier and
        # also can be used to compress/condense programs (hashing feature)
        pass



class AbstractGameObject(ABC):
    # @abstractmethod
    # def set_theme(self, theme_str):
    #     raise NotImplementedError

    # @abstractmethod
    # def destroy(self):
    #     raise NotImplementedError

    @property
    def tkinter_obj(self):
        # underlying Tkinter object
        raise NotImplementedError

    # @abstractmethod
    # def create(self):
    #     raise NotImplementedError


class Paddle(AbstractGameObject):
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.obj = self.setup_paddle()
        # need coords, velocity stuff

    def setup_paddle(self):
        """
        Creates the paddle on screen at the location and size specified in
        the paddle constants. Returns the paddle.
        """
        canvas = self.canvas
        paddle_x = (canvas.get_canvas_width() - PADDLE_WIDTH) / 2
        paddle_y = canvas.get_canvas_height() - PADDLE_Y_OFFSET - PADDLE_HEIGHT
        paddle = canvas.create_rectangle(paddle_x, paddle_y,
                                         paddle_x + PADDLE_WIDTH, paddle_y + PADDLE_HEIGHT, 'black')
        # canvas.set_color(paddle, 'black')
        return paddle

    def move_left(self):
        """
        """
        canvas = self.canvas
        paddle = self.obj
        old_paddle_x = canvas.get_left_x(paddle)
        new_paddle_x = old_paddle_x - 20

        # handle out of boundary situation
        new_paddle_x = max(total_wall_width,
                           min((canvas.get_canvas_width() - total_wall_width) - PADDLE_WIDTH, new_paddle_x))

        # # new_paddle_x = canvas.get_mouse_x() - PADDLE_WIDTH / 2
        # new_paddle_x = max(total_wall_width,
        #                    min((canvas.get_canvas_width() - total_wall_width) - PADDLE_WIDTH, new_paddle_x))

        canvas.moveto(paddle, new_paddle_x, canvas.get_top_y(paddle))

    def move_right(self):
        """
        """
        canvas = self.canvas
        paddle = self.obj
        old_paddle_x = canvas.get_left_x(paddle)
        new_paddle_x = old_paddle_x + 20

        # handle out of boundary situation
        new_paddle_x = max(total_wall_width,
                           min((canvas.get_canvas_width() - total_wall_width) - PADDLE_WIDTH, new_paddle_x))

        # # new_paddle_x = canvas.get_mouse_x() - PADDLE_WIDTH / 2
        # new_paddle_x = max(total_wall_width,
        #                    min((canvas.get_canvas_width() - total_wall_width) - PADDLE_WIDTH, new_paddle_x))

        canvas.moveto(paddle, new_paddle_x, canvas.get_top_y(paddle))

        # this means that the grid is of 20 movements...

        # change_x = 20
        # change_x = max(total_wall_width,
        #     min((canvas.get_canvas_width() - total_wall_width) - PADDLE_WIDTH, new_paddle_x))
        # canvas.move(paddle, 20, 0)

    # mouse testing
    def move_paddle(self):
        """
        Updates the paddle location to track the location of the mouse.  Specifically,
        sets the paddle location to keep the same y coordinate, but set the x coordinate
        such that the paddle is centered around the mouse.  Constrains the paddle to be
        entirely onscreen at all times.
        """
        raise Exception("this function can't work in PyGame")

        canvas, paddle = self.canvas, self.obj
        new_paddle_x = canvas.get_mouse_x() - PADDLE_WIDTH / 2
        new_paddle_x = max(total_wall_width,
                           min((canvas.get_canvas_width() - total_wall_width) - PADDLE_WIDTH, new_paddle_x))
        canvas.moveto(paddle, new_paddle_x, canvas.get_top_y(paddle))


class Ball(AbstractGameObject):
    def __init__(self, canvas: Canvas, np_random):
        self.canvas = canvas
        self.np_random = np_random

        self.obj = self.setup_ball()
        # need coords, velocity stuff
        # velocity_x, velocity_y are change_x, change_y
        # that needs to be updated throughout
        self.velocity_x, self.velocity_y = self.initialize_ball_velocity()

        # ball always appears in the same place
        # self.init_x = canvas.get_canvas_width() / 2 - BALL_RADIUS

        self.x, self.y = self.init_x, self.init_y

        self.ball_already_in_goal = False
        self.ball_destroyed = False

        # change_x, change_y are determined by many factors
        # in further processing
        # self.change_x, self.change_y = self.velocity_x, self.velocity_y

    def move(self):
        # move to a displacement (change/delta)
        self.canvas.move(self.obj, self.velocity_x, self.velocity_y)
        # update position
        self.x, self.y = self.canvas.get_left_x(self.obj), self.canvas.get_top_y(self.obj)

    def reset(self):
        # move ball back to original position
        # a destroyed ball can also be reset
        self.ball_already_in_goal = False
        self.ball_destroyed = False
        self.canvas.moveto(self.obj, self.init_x, self.init_y)
        self.velocity_x, self.velocity_y = self.initialize_ball_velocity()

    def destroy(self):
        # a ball is ONLY destroyed if there's no "launch new ball" in
        # "when ball in goal" or "when ball misses paddle"
        if self.ball_destroyed:
            return

        self.ball_destroyed = True
        self.ball_already_in_goal = False
        self.x, self.y = -10, -10
        self.velocity_x, self.velocity_y = 0, 0
        self.canvas.moveto(self.obj, self.x, self.y)

    @property
    def tkinter_obj(self):
        return self.obj

    def initialize_ball_velocity(self):
        """
        Returns an initial x velocity value and y velocity value.  The x velocity
        is a random value between the min and max x velocity, and randomly positive or
        negative.  The y velocity is VELOCITY_Y.
        """
        velocity_x = random.uniform(VELOCITY_X_MIN, VELOCITY_X_MAX)
        if random.random() < 0.5:
            velocity_x *= -1
        return velocity_x, VELOCITY_Y

    def setup_ball(self):
        """
        Creates the ball on-screen, centered, with the size
        as specified by BALL_RADIUS.  Returns the ball.
        """
        canvas = self.canvas
        ball_x = self.np_random.randint(BALL_RADIUS + wall_thickness, screen_width - wall_thickness - BALL_RADIUS)
        ball_y = canvas.get_canvas_height() / 2 - BALL_RADIUS

        # ball_x = canvas.get_canvas_width() / 2 - BALL_RADIUS
        # ball_y = canvas.get_canvas_height() / 2 - BALL_RADIUS
        ball = canvas.create_oval(ball_x, ball_y,
                                  ball_x + 2 * BALL_RADIUS, ball_y + 2 * BALL_RADIUS, 'black')

        # canvas.set_color(ball, 'black')

        self.init_x, self.init_y = ball_x, ball_y

        return ball

    def infer_ball_on_screen(self):
        if self.ball_destroyed:
            return False

        ball_y_top = self.canvas.get_top_y(self.obj)
        ball_y_bottom = ball_y_top + self.canvas.get_height(self.obj)

        on_screen = True
        if ball_y_bottom <= 0:
            on_screen = False
        elif ball_y_top >= CANVAS_HEIGHT:
            on_screen = False

        return on_screen

    def infer_ball_position(self, paddle: Paddle):
        # determine three conditions:
        # when_ball_in_goal
        # when_ball_hits_wall
        # when_ball_misses_paddle
        # when_ball_hits_paddle

        if self.ball_already_in_goal:
            return BALL_ALREADY_IN_GOAL

        if self.ball_destroyed:
            return BALL_DESTROYED

        canvas = self.canvas
        ball_x_right = canvas.get_left_x(self.obj) + canvas.get_width(self.obj)
        ball_y_bottom = canvas.get_top_y(self.obj) + canvas.get_height(self.obj)

        if canvas.get_top_y(self.obj) < total_wall_width and canvas.get_left_x(
                self.obj) > 100 - 1 and ball_x_right < 300 + 1:
            # TODO: what if we want bounce when-in-goal?
            self.ball_already_in_goal = True
            return BALL_IN_GOAL
        elif ball_y_bottom >= canvas.get_canvas_height():
            return BALL_MISS_PADDLE
        # left wall, right wall
        elif canvas.get_left_x(
                self.obj) < total_wall_width or ball_x_right >= canvas.get_canvas_width() - total_wall_width:
            return BALL_HIT_WALL
        # top wall
        elif canvas.get_top_y(self.obj) < total_wall_width:
            return BALL_HIT_WALL

        # this graphics method gets the location of the ball as a list
        ball_coords = self.canvas.coords(self.obj)

        # the list has four elements:
        ball_x_left = ball_coords[0]
        ball_y_top = ball_coords[1]
        ball_x_right = ball_coords[2]
        ball_y_bottom = ball_coords[3]

        # replace this part
        colliding_list = self.canvas.find_overlapping(ball_x_left, ball_y_top, ball_x_right, ball_y_bottom)
        for collider in colliding_list:
            if collider == paddle.obj:
                return BALL_HIT_PADDLE

        # None means it doesn't trigger anything
        return None

    def bounce(self, condition):
        canvas = self.canvas
        if condition == BALL_HIT_WALL:
            # if ball already in goal, we just let it go...
            if not self.ball_already_in_goal:
                ball_x_right = canvas.get_left_x(self.obj) + canvas.get_width(self.obj)
                # left wall
                if canvas.get_left_x(self.obj) < total_wall_width:
                    self.velocity_x = math.fabs(self.velocity_x)
                    # self.velocity_x *= -1
                # right wall
                elif ball_x_right >= canvas.get_canvas_width() - total_wall_width:
                    self.velocity_x = - math.fabs(self.velocity_x)
                    # self.velocity_x *= -1
                # top wall
                elif canvas.get_top_y(self.obj) < total_wall_width:
                    self.velocity_y = math.fabs(self.velocity_y)
                    # self.velocity_y *= -1
        elif condition == BALL_HIT_PADDLE:
            if self.velocity_y > 0:
                self.velocity_y = -self.velocity_y
        elif condition == BALL_IN_GOAL:
            # just need to flip this one open
            self.ball_already_in_goal = False
            # self.velocity_y *= -1
            self.velocity_y = math.fabs(self.velocity_y)
        elif condition == BALL_MISS_PADDLE:
            self.velocity_y = -math.fabs(self.velocity_y)


class ScoreBoard(object):
    def __init__(self, canvas: Canvas, win_points=3):
        self.own = 0
        self.opponent = 0
        self.win_points = win_points

        self.canvas = canvas
        self.obj = None

    def score_point(self):
        self.own += 1
        self.update()

    def score_opponent_point(self):
        self.opponent += 1
        self.update()

    def draw(self):
        text = "Score " + str(self.own) + " : " + str(self.opponent)
        x_pos = (screen_width - 20) // 2

        obj = self.canvas.create_text(x_pos, 50, text, "comicsansms", 25)

        self.obj = obj

    def update(self):
        text = "Score " + str(self.own) + " : " + str(self.opponent)
        print(text)
        self.canvas.set_text(self.obj, text)

    def game_over(self):
        if self.own >= self.win_points or self.opponent >= self.win_points:
            return True
        else:
            return False


class RNG(object):
    def __init__(self):
        self.np_random = None
        self.curr_seed = None

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        self.curr_seed = seed
        return [seed]

    def choice(self, a, size=None, replace=True, p=None):
        return self.np_random.choice(a, size, replace, p)

    def randint(self, low, high=None, size=None, dtype=int):
        return self.np_random.randint(low, high, size, dtype)


# TODO: ~ figure out if you need "shadow engine"
# TODO: 1. Just execute command
# TODO: 2. Execution of commands (inside conditions, as pass-in functions, except "bounce")
# TODO: 3. Scores keeping, etc.

def setup_walls(canvas):
    # left wall
    brick = canvas.create_rectangle(0, 0, total_wall_width, 400)
    canvas.set_color(brick, 'red')

    # right wall
    brick = canvas.create_rectangle(CANVAS_WIDTH - total_wall_width, 0, CANVAS_WIDTH, 400)
    canvas.set_color(brick, 'red')

    # top left wall
    brick = canvas.create_rectangle(total_wall_width, 0, 100, total_wall_width)
    canvas.set_color(brick, 'red')

    # top right wall
    brick = canvas.create_rectangle(300, 0, CANVAS_WIDTH - total_wall_width, total_wall_width)
    canvas.set_color(brick, 'red')


# 1: move left
# 2: move right
# 3: bounce ball
# 4: score point
# 5: score opponent point
# 6: launch new ball

class Bounce(object):
    """
    """

    def __init__(self, program):
        self.rng = RNG()
        self.seed()

        assert program is not None, "Specify program as None."

        self.program = program

        canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
        canvas.set_canvas_background_color('floral white')


        setup_walls(canvas)

        self.paddle = Paddle(canvas)
        # self.ball = Ball(canvas)

        self.balls = []  # , Ball(canvas, self.rng)

        self.score_board = ScoreBoard(canvas)

        self.canvas = canvas
        self.canvas.update()

        self.executable_cmds = [MOVE_LEFT, MOVE_RIGHT, SCORE_OPPO_POINT, SCORE_POINT, LAUNCH_NEW_BALL]

    def seed(self, seed=None):
        # we use a class object, so that if we update seed here, it broadcasts into everywhere
        return self.rng.seed(seed)

    def remove_bounce(self, cmds):
        # generate new list
        return [c for c in cmds if c != BOUNCE_BALL]

    def remove_set_cmds(self, cmds):
        # generate new list
        return [c for c in cmds if 'set' not in c]

    def remove_bounce_and_set_cmds(self, cmds):
        # generate new list
        return [c for c in cmds if c != BOUNCE_BALL and 'set' not in c]

    def execute(self, cmd):
        # we handle bounce inside Ball class
        assert cmd != "bounce ball"
        if cmd in self.executable_cmds:
            if " " in cmd:
                cmd = cmd.replace(" ", "_")
            eval("self." + cmd + "()")

    def when_run_execute(self):
        cmds = self.program[WHEN_RUN]
        cmds = self.remove_bounce_and_set_cmds(cmds)
        for cmd in cmds:
            self.execute(cmd)

    def when_left_arrow(self):
        cmds = self.program[WHEN_LEFT_ARROW]
        cmds = self.remove_bounce_and_set_cmds(cmds)
        for cmd in cmds:
            self.execute(cmd)

    def when_right_arrow(self, keys):
        cmds = self.program[WHEN_RIGHT_ARROW]
        cmds = self.remove_bounce_and_set_cmds(cmds)
        for cmd in cmds:
            self.execute(cmd)

    def move_left(self):
        self.paddle.move_left()

    def move_right(self):
        self.paddle.move_right()

    def score_point(self):
        self.score_board.score_point()

    def score_opponent_point(self):
        self.score_board.score_opponent_point()

    def launch_new_ball(self):
        # we can have up to 10 balls at any one point
        # we don't have a "remove" ball, we just reset them

        # first, let's look through our list of balls
        # to see if there are ones "destroyed" but not "reset"
        # for "when ball in goal", "when ball misses paddle", launch new ball = reset current ball
        # for other conditions, "launch new ball" = create new ball /ressurrect old ball

        created = False
        for ball in self.balls:
            if ball.ball_destroyed:
                ball.reset()
                created = True
                break

        if len(self.balls) < 10 and not created:
            self.balls.append(Ball(self.canvas, self.rng))

    """
    # 1: move left
    # 2: move right
    # 3: bounce ball (Do this!!!!!)
    # 4: score point
    # 5: score opponent point
    # 6: launch new ball

    These 4, still execute it in here (because score/new ball etc.), based on the condition of each ball

    BALL_HIT_PADDLE = "when ball hits paddle"
    BALL_HIT_WALL = "when ball hits wall"
    BALL_IN_GOAL = "when ball in goal"
    BALL_MISS_PADDLE = "when ball misses paddle"

    We are special handling "launch_new_ball" inside "when ball in goal".
    If there is one, then we reset the ball. Otherwise we don't reset the ball, we keep it out.
    """

    def run(self, debug=False):

        self.score_board.draw()

        self.when_run_execute()

        num_presses = 0
        # while turns > 0:
        while not self.score_board.game_over():

            # update ball
            for ball in self.balls:
                if ball.ball_destroyed:
                    continue
                ball.move()

            # update paddle (mouse-based)
            self.paddle.move_paddle()

            # arrow key based
            # if len(self.canvas.key_presses) > 0:
            #     if self.canvas.key_presses[-1].keysym == 'Left' and len(self.canvas.key_presses) > num_presses:
            #         num_presses = len(self.canvas.key_presses)
            #         self.paddle.move_left()
            #     elif self.canvas.key_presses[-1].keysym == 'Right' and len(self.canvas.key_presses) > num_presses:
            #         num_presses = len(self.canvas.key_presses)
            #         self.paddle.move_right()

            # collision

            # 4 ball-related conditions
            # ====== new modularized code ======
            for ball in self.balls:
                if ball.ball_destroyed:
                    continue

                ball_condition = ball.infer_ball_position(self.paddle)
                ball_on_screen = ball.infer_ball_on_screen()

                # add a safeguard here...
                # for out-of-boundary balls
                if not ball_on_screen:
                    ball.destroy()
                    continue

                if ball_condition == BALL_IN_GOAL:
                    cmds = self.program[BALL_IN_GOAL]
                    cmds = self.remove_set_cmds(cmds)
                    for cmd in cmds:
                        if cmd == BOUNCE_BALL:
                            ball.bounce(ball_condition)
                        elif cmd == LAUNCH_NEW_BALL:
                            # yeah, ball immediately disappears
                            # but that's ok...
                            if not self.score_board.game_over():
                                ball.reset()
                        else:
                            # the reason is that, unless the ball is reset
                            # once in goal or miss paddle, it's gone
                            self.execute(cmd)
                elif ball_condition == BALL_MISS_PADDLE:
                    cmds = self.program[BALL_MISS_PADDLE]
                    cmds = self.remove_set_cmds(cmds)
                    for cmd in cmds:
                        if cmd == BOUNCE_BALL:
                            ball.bounce(ball_condition)
                        elif cmd == LAUNCH_NEW_BALL:
                            # yeah, ball immediately disappears
                            # but that's ok...
                            if not self.score_board.game_over():
                                ball.reset()
                        else:
                            self.execute(cmd)
                elif ball_condition == BALL_HIT_WALL:
                    cmds = self.program[BALL_HIT_WALL]
                    cmds = self.remove_set_cmds(cmds)
                    for cmd in cmds:
                        if cmd == BOUNCE_BALL:
                            ball.bounce(ball_condition)
                        else:
                            self.execute(cmd)
                elif ball_condition == BALL_HIT_PADDLE:
                    cmds = self.program[BALL_HIT_PADDLE]
                    cmds = self.remove_set_cmds(cmds)
                    for cmd in cmds:
                        if cmd == BOUNCE_BALL:
                            ball.bounce(ball_condition)
                        else:
                            self.execute(cmd)

            self.canvas.update()
            time.sleep(1 / 60)

    # TODO: then RL Env
    # TODO: then train frame-stacking DQN
    def act(self, action):
        pass


# RL_Env here
# 1. We will directly add frame stacking into the RL env (no more Gym Wrapper); so we can control stuff
# 2. Decide state space.

if __name__ == '__main__':
    program = Program()
    program.set_correct()

    # program.load("programs/miss_paddle_no_launch_ball.json")
    # program.load("programs/hit_goal_no_point.json")
    # program.load("programs/empty.json")
    # program.load("programs/multi_ball.json")
    # program.load("programs/ball_through_wall.json")
    # program.load("programs/multi_ball2.json")

    game = Bounce(program)
    game.run()

    # print(program[BALL_MISS_PADDLE])
    # print(program[WHEN_RUN])