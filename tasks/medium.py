class MediumTask:

    def __init__(self):
        self.steps = 0
        self.done = False

    def get_state(self):
        return {
            "status": "high_cpu"
        }

    def step(self, action):
        self.steps += 1

        if action == "kill_process":
            self.done = True
            return self.get_state(), 0.99, True

        return self.get_state(), 0.05, False