

import numpy as np

# from AppleVecEnv import AppleVecEnv
# env = AppleVecEnv(num_envs=2, pixel=True, mouse_action=True, scale_action=False, tab_id=1)

# from ColorVecEnv import ColorVecEnv
# env = ColorVecEnv(num_envs=2, pixel=True, mouse_action=True, scale_action=False)

from .BounceVecEnv import BounceVecEnv
env = BounceVecEnv(num_envs=2, pixel=True, spawn_process_manager=True, port=13459, tab_id=1)

# from FlyerVecEnv import FlyerVecEnv
# env = FlyerVecEnv(num_envs=2, pixel=True)


print('''Methods:
         env.reset()
         env.reset(envs_to_reset=[e1, e2, ...])
         env.step_async(np.ndarray)
         env.step_wait()
         env.render()
         env.render(i)
         env.close()
      ''')
