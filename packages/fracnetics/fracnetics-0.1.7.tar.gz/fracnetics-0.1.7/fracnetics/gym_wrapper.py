class GymEnvWrapper:
    def __init__(self, env):
        self.env = env

    def reset(self):
        obs, _ = self.env.reset()
        return obs

    def step(self, action):
        obs, reward, terminated, truncated, _ = self.env.step(action)
        done = terminated or truncated
        return obs, reward, done

