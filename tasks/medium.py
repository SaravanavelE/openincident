class MediumTask:

    def __init__(self):
        self.done = False

    def get_state(self):
        return {
            "status": "high_cpu"
        }

    def step(self, action):

        if action == "kill_process":
            self.done = True
            return self.get_state(), 0.98, True

        return self.get_state(), 0.05, False