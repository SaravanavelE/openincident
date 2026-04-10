from tasks.easy import EasyTask
from tasks.medium import MediumTask
from tasks.hard import HardTask


def clamp_reward(value):
    try:
        value = float(value)
    except:
        value = 0.01
    return max(0.01, min(0.99, value))


class OpenIncidentEnv:
    def __init__(self):
        self.task = None
        self.done = False

    def reset(self, task_name="easy"):
        if task_name == "easy":
            self.task = EasyTask()
        elif task_name == "medium":
            self.task = MediumTask()
        elif task_name == "hard":
            self.task = HardTask()
        else:
            self.task = EasyTask()

        self.done = False

        return {
            "observation": self.task.get_state(),
            "done": False
        }

    def step(self, action):
        if self.done:
            return {
                "observation": {},
                "reward": clamp_reward(0.01),
                "done": True
            }

        obs, reward, done = self.task.step(action)

        reward = clamp_reward(reward)

        self.done = done

        return {
            "observation": obs,
            "reward": reward,
            "done": done
        }

    def state(self):
        return {
            "done": self.done
        }