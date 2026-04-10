class EasyTask:

    def __init__(self):
        self.steps = 0
        self.done = False

    def get_state(self):
        return {
            "status": "service_down"
        }

    def step(self, action):
        self.steps += 1

        if action == "restart_service":
            self.done = True
            return self.get_state(), 0.99, True

        return self.get_state(), 0.05, False