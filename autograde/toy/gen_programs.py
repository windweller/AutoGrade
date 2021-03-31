"""
We use this to generate programs
"""

import random
from .maze import GAME_FAIL_BUG, GAME_CRASH_BUG, GAME_HALT_BUG, GAME_REWARD_BUG

random.seed(15123)

bug_types = [GAME_FAIL_BUG, GAME_CRASH_BUG, GAME_HALT_BUG, GAME_REWARD_BUG]
possible_start_locs = [(2, 0), (4, 2), (2, 2)]

def generate_broken_position():
    x = random.randint(0, 4)
    y = random.randint(0, 4)

    while (x, y) in possible_start_locs:
        x = random.randint(0, 4)
        y = random.randint(0, 4)

    return x, y

def generate_bug_type():
    bug_type = random.choice(bug_types)
    return bug_type

def get_broken_programs(num):
    programs = []
    for _ in range(num):
        program = {}
        program[generate_broken_position()] = generate_bug_type()
        programs.append(program)
    return programs

if __name__ == '__main__':
    print(get_broken_programs(5))